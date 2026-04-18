"""Password reset schemas for request/response validation."""

from pydantic import BaseModel, EmailStr, Field


class PasswordResetRequestSchema(BaseModel):
    """Password reset request schema."""

    email: EmailStr


class PasswordResetValidateSchema(BaseModel):
    """Password reset token validation schema."""

    token: str


class PasswordResetConfirmSchema(BaseModel):
    """Password reset confirmation schema."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordResetResponse(BaseModel):
    """Password reset response schema."""

    message: str
    success: bool
