"""Experience rating schemas for feedback service."""

from datetime import datetime

from pydantic import BaseModel, Field


class ExperienceRatingCreate(BaseModel):
    """Schema for creating an experience rating entry."""

    user_id: int = Field(..., description="User ID", ge=1)
    rating: int = Field(..., description="Rating from 1 to 5", ge=1, le=5)


class ExperienceRatingResponse(BaseModel):
    """Schema for experience rating response."""

    id: int
    user_id: int
    rating: int
    submitted_at: datetime

    model_config = {"from_attributes": True}
