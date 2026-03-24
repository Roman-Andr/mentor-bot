"""Invitation schemas for request/response validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from auth_service.core import EmployeeLevel, InvitationStatus, UserRole
from auth_service.schemas.department import DepartmentResponse


class InvitationBase(BaseModel):
    """Base invitation schema."""

    email: EmailStr
    employee_id: str = Field(..., min_length=1, max_length=50)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    department_id: int | None = None
    position: str | None = Field(None, max_length=100)
    level: EmployeeLevel | None = Field(None, max_length=50)
    role: UserRole = Field(default=UserRole.NEWBIE, description="User role to assign on registration")
    mentor_id: int | None = None
    expires_in_days: int = Field(default=7, ge=1, le=30)


class InvitationCreate(InvitationBase):
    """Invitation creation schema."""


class InvitationResponse(InvitationBase):
    """Invitation response schema."""

    id: int
    token: str
    status: InvitationStatus
    created_at: datetime
    expires_at: datetime
    used_at: datetime | None = None
    user_id: int | None = None
    invitation_url: str
    is_expired: bool
    department: DepartmentResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class InvitationStats(BaseModel):
    """Invitation statistics schema."""

    total: int = Field(..., description="Total number of invitations")
    pending: int = Field(..., description="Number of pending invitations")
    used: int = Field(..., description="Number of used invitations")
    revoked: int = Field(..., description="Number of revoked invitations")
    expired: int = Field(..., description="Number of expired pending invitations")
    conversion_rate: float = Field(..., description="Percentage of used invitations (used/total)", ge=0.0, le=100.0)
    by_status: dict[InvitationStatus, int] = Field(..., description="Count of invitations by status")
    recent_activity: list[dict[str, Any]] = Field(..., description="Daily invitation creation counts for last 30 days")


class InvitationListResponse(BaseModel):
    """Invitation list response schema."""

    total: int
    invitations: list[InvitationResponse]
    page: int
    size: int
    pages: int
    stats: InvitationStats
