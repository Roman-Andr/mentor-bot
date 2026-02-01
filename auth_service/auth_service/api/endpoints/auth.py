"""Authentication endpoints with repository pattern."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth_service.api.deps import (
    AuthServiceDep,
    CurrentUser,
)
from auth_service.core import (
    AuthException,
    ConflictException,
    NotFoundException,
    ValidationException,
)
from auth_service.core.telegram import verify_telegram_api_key
from auth_service.schemas import (
    LoginRequest,
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TelegramApiKeyAuth,
    TelegramAuthRequest,
    TelegramRegistrationRequest,
    Token,
    UserResponse,
)

router = APIRouter()


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> Token:
    """Login with email and password using repository pattern."""
    login_data = LoginRequest(email=form_data.username, password=form_data.password)

    try:
        _, token = await auth_service.authenticate_user(login_data)
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
        ) from e
    else:
        return token


@router.post("/refresh")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> Token:
    """Refresh access token using refresh token."""
    try:
        token = await auth_service.refresh_access_token(refresh_data)
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
        ) from e
    else:
        return token


@router.post("/telegram")
async def telegram_auth(
    telegram_data: TelegramApiKeyAuth,
    auth_service: AuthServiceDep,
    api_key: Annotated[str, Header(alias="X-API-Key")],
) -> Token:
    """Authenticate with Telegram data using API key."""
    if not verify_telegram_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if telegram_data.api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key mismatch",
        )

    try:
        telegram_auth_data = TelegramAuthRequest(
            telegram_id=telegram_data.telegram_id,
            username=None,
            first_name="",
            last_name=None,
        )

        _, token = await auth_service.authenticate_with_telegram(telegram_auth_data)
    except (AuthException, NotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
        ) from e
    else:
        return token


@router.post("/register/{invitation_token}")
async def register_with_invitation(
    invitation_token: str,
    telegram_data: TelegramRegistrationRequest,
    auth_service: AuthServiceDep,
    api_key: Annotated[str, Header(alias="X-API-Key")],
) -> Token:
    """Register new user using invitation token with Telegram."""
    if not verify_telegram_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    try:
        user = await auth_service.register_with_invitation_and_telegram(invitation_token, telegram_data)

        token = auth_service._create_token_for_user(user)
    except (ValidationException, ConflictException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e
    else:
        return token


@router.post("/password/reset")
async def request_password_reset(
    _reset_data: PasswordResetRequest,
) -> MessageResponse:
    """Request password reset link."""
    return MessageResponse(message="Password reset not implemented yet")


@router.post("/password/reset/confirm")
async def confirm_password_reset(
    _confirm_data: PasswordResetConfirm,
) -> MessageResponse:
    """Confirm password reset with token."""
    return MessageResponse(message="Password reset not implemented yet")


@router.get("/me")
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout() -> MessageResponse:
    """Logout user (client should discard tokens)."""
    return MessageResponse(message="Successfully logged out")
