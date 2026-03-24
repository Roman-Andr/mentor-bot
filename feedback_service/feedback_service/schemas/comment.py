"""Comment schemas for feedback service."""

from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    """Schema for creating a comment entry."""

    user_id: int = Field(..., description="User ID", ge=1)
    comment: str = Field(..., description="Comment text", min_length=10)


class CommentResponse(BaseModel):
    """Schema for comment response."""

    id: int
    user_id: int
    comment: str
    submitted_at: datetime

    model_config = {"from_attributes": True}
