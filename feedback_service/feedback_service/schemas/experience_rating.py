"""Experience rating schemas for feedback service."""

from datetime import datetime

from pydantic import BaseModel, Field


class ExperienceRatingCreate(BaseModel):
    """Schema for creating an experience rating entry."""

    rating: int = Field(..., description="Rating from 1 to 5", ge=1, le=5)
    is_anonymous: bool = Field(default=False, description="Submit anonymously")


class ExperienceRatingResponse(BaseModel):
    """Schema for experience rating response."""

    id: int
    user_id: int | None = None
    is_anonymous: bool
    rating: int
    submitted_at: datetime

    model_config = {"from_attributes": True}
