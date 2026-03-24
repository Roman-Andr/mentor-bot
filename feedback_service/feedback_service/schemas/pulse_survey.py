"""Pulse survey schemas for feedback service."""

from datetime import datetime

from pydantic import BaseModel, Field


class PulseSurveyCreate(BaseModel):
    """Schema for creating a pulse survey entry."""

    user_id: int = Field(..., description="User ID", ge=1)
    rating: int = Field(..., description="Rating from 1 to 10", ge=1, le=10)


class PulseSurveyResponse(BaseModel):
    """Schema for pulse survey response."""

    id: int
    user_id: int
    rating: int
    submitted_at: datetime

    model_config = {"from_attributes": True}
