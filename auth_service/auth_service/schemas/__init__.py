"""Pydantic schemas for request/response validation."""

from auth_service.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TelegramApiKeyAuth,
    TelegramAuthRequest,
    TelegramRegistrationRequest,
    Token,
    TokenPayload,
)
from auth_service.schemas.invitation import (
    InvitationBase,
    InvitationCreate,
    InvitationListResponse,
    InvitationResponse,
    InvitationStats,
)
from auth_service.schemas.responses import (
    HealthCheck,
    MessageResponse,
    ServiceStatus,
)
from auth_service.schemas.user import (
    UserBase,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)

__all__ = [
    "ChangePasswordRequest",
    "HealthCheck",
    "InvitationBase",
    "InvitationCreate",
    "InvitationListResponse",
    "InvitationResponse",
    "InvitationStats",
    "LoginRequest",
    "MessageResponse",
    "PasswordResetConfirm",
    "PasswordResetRequest",
    "RefreshTokenRequest",
    "ServiceStatus",
    "TelegramApiKeyAuth",
    "TelegramAuthRequest",
    "TelegramRegistrationRequest",
    "Token",
    "TokenPayload",
    "UserBase",
    "UserCreate",
    "UserListResponse",
    "UserResponse",
    "UserUpdate",
]
