"""Authentication schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from auth_service.core import UserRole


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105
    expires_at: datetime
    user_id: int
    role: UserRole


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: str
    user_id: int
    role: UserRole


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""

    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""

    current_password: str
    new_password: str = Field(..., min_length=8)


class TelegramAuthRequest(BaseModel):
    """Telegram authentication request schema."""

    telegram_id: int
    username: str | None = None
    first_name: str
    last_name: str | None = None


class TelegramRegistrationRequest(BaseModel):
    """Telegram registration request schema (for invitation registration)."""

    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = Field(None, max_length=20)


class TelegramApiKeyAuth(BaseModel):
    """Telegram API key authentication schema."""

    api_key: str
    telegram_id: int
