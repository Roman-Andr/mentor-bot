"""User meeting schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from meeting_service.core.enums import MeetingStatus
from meeting_service.schemas.meeting import MeetingResponse

MIN_RATING = 1
MAX_RATING = 5


class UserMeetingBase(BaseModel):
    """Base user meeting schema."""

    user_id: int
    meeting_id: int
    scheduled_at: datetime | None = None


class UserMeetingCreate(UserMeetingBase):
    """User meeting creation schema (for assignment)."""


class UserMeetingUpdate(BaseModel):
    """User meeting update schema (status, scheduled_at)."""

    status: MeetingStatus | None = None
    scheduled_at: datetime | None = None


class UserMeetingComplete(BaseModel):
    """Schema for marking a meeting as completed with feedback."""

    feedback: str | None = Field(None, max_length=2000)
    rating: int | None = Field(None, ge=1, le=5)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int | None) -> int | None:
        """Validate rating range."""
        if v is not None and not MIN_RATING <= v <= MAX_RATING:
            msg = f"Rating must be between {MIN_RATING} and {MAX_RATING}"
            raise ValueError(msg)
        return v


class UserMeetingResponse(UserMeetingBase):
    """User meeting response schema."""

    id: int
    status: MeetingStatus
    completed_at: datetime | None = None
    feedback: str | None = None
    rating: int | None = None
    google_calendar_event_id: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    meeting: MeetingResponse | None = None  # optionally expand meeting details

    model_config = ConfigDict(from_attributes=True)


class UserMeetingListResponse(BaseModel):
    """User meeting list response schema."""

    total: int
    items: list[UserMeetingResponse]
    page: int
    size: int
    pages: int
