"""User-Mentor relationship schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserMentorBase(BaseModel):
    """Base user-mentor schema."""

    user_id: int
    mentor_id: int
    notes: str | None = None


class UserMentorCreate(UserMentorBase):
    """User-Mentor creation schema."""


class UserMentorUpdate(BaseModel):
    """User-Mentor update schema."""

    is_active: bool | None = None
    notes: str | None = None


class UserMentorResponse(UserMentorBase):
    """User-Mentor response schema."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserMentorListResponse(BaseModel):
    """User-Mentor list response schema."""

    total: int
    relations: list[UserMentorResponse]
