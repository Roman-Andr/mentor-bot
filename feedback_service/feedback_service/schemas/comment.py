"""Comment schemas for feedback service."""

from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    """Schema for creating a comment entry."""

    comment: str = Field(..., description="Comment text", min_length=10)
    is_anonymous: bool = Field(default=False, description="Submit anonymously")
    allow_contact: bool = Field(default=False, description="Allow HR to contact for follow-up")
    contact_email: str | None = Field(default=None, description="Contact email for follow-up")


class CommentReplyCreate(BaseModel):
    """Schema for creating a reply to a comment."""

    reply: str = Field(..., description="Reply text", min_length=1)


class CommentResponse(BaseModel):
    """Schema for comment response."""

    id: int
    user_id: int | None = None
    is_anonymous: bool
    comment: str
    submitted_at: datetime
    allow_contact: bool
    contact_email: str | None = None
    reply: str | None = None
    replied_at: datetime | None = None
    replied_by: int | None = None

    model_config = {"from_attributes": True}
