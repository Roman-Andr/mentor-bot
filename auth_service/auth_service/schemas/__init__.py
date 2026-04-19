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
from auth_service.schemas.department import (
    DepartmentCreate,
    DepartmentListResponse,
    DepartmentResponse,
    DepartmentUpdate,
)
from auth_service.schemas.invitation import (
    InvitationBase,
    InvitationCreate,
    InvitationListResponse,
    InvitationResponse,
    InvitationStats,
)
from auth_service.schemas.password_reset import (
    PasswordResetConfirmSchema,
    PasswordResetRequestSchema,
    PasswordResetResponse,
    PasswordResetValidateSchema,
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
from auth_service.schemas.user_mentor import (
    UserMentorCreate,
    UserMentorListResponse,
    UserMentorResponse,
    UserMentorUpdate,
)

__all__ = [
    "ChangePasswordRequest",
    "DepartmentCreate",
    "DepartmentListResponse",
    "DepartmentResponse",
    "DepartmentUpdate",
    "HealthCheck",
    "InvitationBase",
    "InvitationCreate",
    "InvitationListResponse",
    "InvitationResponse",
    "InvitationStats",
    "LoginRequest",
    "MessageResponse",
    "PasswordResetConfirm",
    "PasswordResetConfirmSchema",
    "PasswordResetRequest",
    "PasswordResetRequestSchema",
    "PasswordResetResponse",
    "PasswordResetValidateSchema",
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
    "UserMentorCreate",
    "UserMentorListResponse",
    "UserMentorResponse",
    "UserMentorUpdate",
    "UserResponse",
    "UserUpdate",
]
