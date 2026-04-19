"""Meeting template schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from meeting_service.core.enums import EmployeeLevel, MeetingType


class MeetingBase(BaseModel):
    """Base meeting template schema."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    type: MeetingType
    department_id: int | None = None
    position: str | None = Field(None, max_length=100)
    level: EmployeeLevel | None = None
    is_mandatory: bool = True
    order: int = 0
    deadline_days: int = Field(default=7, ge=0, le=365)
    duration_minutes: int = Field(default=60, ge=1, le=480)


class MeetingCreate(MeetingBase):
    """Meeting creation schema."""


class MeetingUpdate(BaseModel):
    """Meeting update schema (all fields optional)."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    type: MeetingType | None = None
    department_id: int | None = None
    position: str | None = Field(None, max_length=100)
    level: EmployeeLevel | None = None
    is_mandatory: bool | None = None
    order: int | None = None
    deadline_days: int | None = Field(None, ge=0, le=365)
    duration_minutes: int | None = Field(None, ge=1, le=480)


class MeetingResponse(MeetingBase):
    """Meeting response schema."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MeetingListResponse(BaseModel):
    """Meeting list response schema."""

    total: int
    meetings: list[MeetingResponse]
    page: int
    size: int
    pages: int
