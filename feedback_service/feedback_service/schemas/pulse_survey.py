"""Pulse survey schemas for feedback service."""

from datetime import datetime

from pydantic import BaseModel, Field


class PulseSurveyCreate(BaseModel):
    """Schema for creating a pulse survey entry."""

    rating: int = Field(..., description="Rating from 1 to 10", ge=1, le=10)
    is_anonymous: bool = Field(default=False, description="Submit anonymously")
    user_id: int | None = Field(default=None, description="User ID (for service-to-service calls)")


class PulseSurveyResponse(BaseModel):
    """Schema for pulse survey response."""

    id: int
    user_id: int | None = None
    is_anonymous: bool
    rating: int
    submitted_at: datetime

    model_config = {"from_attributes": True}
