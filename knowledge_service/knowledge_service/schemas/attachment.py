"""Attachment schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from knowledge_service.core import AttachmentType


class AttachmentBase(BaseModel):
    """Base attachment schema."""

    article_id: int
    name: str = Field(..., min_length=1, max_length=500)
    type: AttachmentType
    url: str = Field(..., max_length=2000)
    file_size: int | None = Field(None, ge=0)
    mime_type: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)
    order: int = Field(0, ge=0)
    is_downloadable: bool = True


class AttachmentCreate(AttachmentBase):
    """Attachment creation schema."""


class AttachmentResponse(AttachmentBase):
    """Attachment response schema."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
