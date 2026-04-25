"""Authentication endpoints with repository pattern."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from auth_service.api.deps import (
    AuthServiceDep,
    CurrentUser,
)
from auth_service.config import settings
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
    RefreshTokenRequest,
    TelegramApiKeyAuth,
    TelegramAuthRequest,
    TelegramRegistrationRequest,
    Token,
    UserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login")
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> Token:
    """
    Login with email and password using repository pattern.

    Sets httpOnly cookies for token storage (secure against XSS).
    """
    logger.info("Login request received (email=%s)", form_data.username)
    login_data = LoginRequest(email=form_data.username, password=form_data.password)

    try:
        _, token = await auth_service.authenticate_user(login_data)
    except AuthException as e:
        logger.warning("Login failed for email=%s: %s", form_data.username, e.detail)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
        ) from e
    else:
        # Set httpOnly cookies for secure token storage
        # secure=False in DEBUG mode for local testing, True in production
        cookie_secure = not settings.DEBUG
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=cookie_secure,
            samesite="lax",
            max_age=token.expires_in,
        )
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            httponly=True,
            secure=cookie_secure,
            samesite="lax",
            max_age=7 * 24 * 3600,  # 7 days in seconds
        )
        return token


@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> Token:
    """
    Refresh access token using refresh token.

    Updates httpOnly cookies with new tokens.
    """
    logger.debug("Refresh token request received")
    try:
        token = await auth_service.refresh_access_token(refresh_data)
    except AuthException as e:
        logger.warning("Refresh token failed: %s", e.detail)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
        ) from e
    else:
        # Update httpOnly cookies with new tokens
        # secure=False in DEBUG mode for local testing, True in production
        cookie_secure = not settings.DEBUG
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=cookie_secure,
            samesite="lax",
            max_age=token.expires_in,
        )
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            httponly=True,
            secure=cookie_secure,
            samesite="lax",
            max_age=7 * 24 * 3600,  # 7 days in seconds
        )
        return token


@router.post("/telegram")
async def telegram_auth(
    telegram_data: TelegramApiKeyAuth,
    auth_service: AuthServiceDep,
    api_key: Annotated[str, Header(alias="X-API-Key")],
) -> Token:
    """Authenticate with Telegram data using API key."""
    logger.info("Telegram auth request (telegram_id=%s)", telegram_data.telegram_id)
    if not verify_telegram_api_key(api_key):
        logger.warning("Telegram auth rejected: invalid API key (telegram_id=%s)", telegram_data.telegram_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if telegram_data.api_key != api_key:
        logger.warning("Telegram auth rejected: API key mismatch (telegram_id=%s)", telegram_data.telegram_id)
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
        logger.warning(
            "Telegram auth failed (telegram_id=%s): %s",
            telegram_data.telegram_id,
            e.detail,
        )
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
    logger.info(
        "Registration request via invitation (telegram_id=%s)",
        telegram_data.telegram_id,
    )
    if not verify_telegram_api_key(api_key):
        logger.warning("Registration rejected: invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    try:
        user = await auth_service.register_with_invitation_and_telegram(invitation_token, telegram_data)

        # Auto-create checklists from matching templates
        try:
            await auth_service.auto_create_user_checklists(user)
        except Exception:
            logger.exception("Failed to auto-create checklists for user %s", user.id)

        token = auth_service.create_token_for_user(user)
    except (ValidationException, ConflictException) as e:
        logger.warning(
            "Registration failed (telegram_id=%s): %s",
            telegram_data.telegram_id,
            e.detail,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e
    else:
        logger.info("Registration completed (user_id=%s)", user.id)
        return token


@router.get("/me")
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(response: Response) -> MessageResponse:
    """Logout user and clear httpOnly cookies."""
    logger.info("Logout request received")
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return MessageResponse(message="Successfully logged out")
