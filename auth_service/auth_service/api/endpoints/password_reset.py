"""Password reset endpoints with rate limiting."""

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from auth_service.database import AsyncSessionLocal
from auth_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from auth_service.schemas import (
    PasswordResetConfirmSchema,
    PasswordResetRequestSchema,
    PasswordResetResponse,
    PasswordResetValidateSchema,
)
from auth_service.services.password_reset import PasswordResetService
from auth_service.utils.integrations import notification_service_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/request")
async def request_password_reset(
    data: PasswordResetRequestSchema,
    request: Request,
    background_tasks: BackgroundTasks,
) -> PasswordResetResponse:
    """
    Request password reset email.

    Always returns success to prevent email enumeration attacks.
    Rate limited to 3 requests per user per hour.
    """
    async with AsyncSessionLocal() as session:
        uow = SqlAlchemyUnitOfWork(AsyncSessionLocal)
        await uow.__aenter__()
        try:
            service = PasswordResetService(uow, session)

            ip_address = request.client.host if request.client else None

            _success, raw_token, user = await service.request_reset(
                email=data.email,
                ip_address=ip_address,
            )

            # Send email in background if token was created
            if raw_token and user:
                background_tasks.add_task(
                    notification_service_client.send_password_reset_email,
                    to_email=user.email,
                    user_name=user.first_name,
                    reset_token=raw_token,
                )

            # Commit the transaction
            await uow.commit()

            # Always return generic message to prevent enumeration
            return PasswordResetResponse(
                message="If an account with this email exists, you will receive a password reset link",
                success=True,
            )
        finally:
            await uow.__aexit__(None, None, None)


@router.post("/validate")
async def validate_reset_token(data: PasswordResetValidateSchema) -> PasswordResetResponse:
    """
    Validate reset token without consuming it.

    Returns success if token is valid and not expired.
    """
    async with AsyncSessionLocal() as session:
        uow = SqlAlchemyUnitOfWork(AsyncSessionLocal)
        await uow.__aenter__()
        try:
            service = PasswordResetService(uow, session)
            user = await service.validate_token(data.token)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired token",
                )

            return PasswordResetResponse(
                message="Token is valid",
                success=True,
            )
        finally:
            await uow.__aexit__(None, None, None)


@router.post("/confirm")
async def confirm_password_reset(
    data: PasswordResetConfirmSchema,
    background_tasks: BackgroundTasks,
) -> PasswordResetResponse:
    """
    Confirm password reset with valid token.

    Updates the user's password and marks the token as used.
    Sends confirmation email on success.
    """
    async with AsyncSessionLocal() as session:
        uow = SqlAlchemyUnitOfWork(AsyncSessionLocal)
        await uow.__aenter__()
        user_email = None
        user_name = None
        try:
            service = PasswordResetService(uow, session)

            # Get user email before resetting for confirmation email
            user = await service.validate_token(data.token)
            if user:
                user_email = user.email
                user_name = user.first_name

            success = await service.confirm_reset(data.token, data.new_password)

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired token",
                )

            # Commit the transaction
            await uow.commit()

            # Send confirmation email in background
            if user_email:
                background_tasks.add_task(
                    notification_service_client.send_password_reset_confirmation_email,
                    to_email=user_email,
                    user_name=user_name or "User",
                )

            return PasswordResetResponse(
                message="Password updated successfully",
                success=True,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Password reset confirmation failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password",
            ) from e
        finally:
            await uow.__aexit__(None, None, None)
