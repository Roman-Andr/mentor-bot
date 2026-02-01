"""Tag schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    """Base tag schema."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class TagCreate(TagBase):
    """Tag creation schema."""


class TagUpdate(BaseModel):
    """Tag update schema."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class TagResponse(TagBase):
    """Tag response schema."""

    id: int
    usage_count: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
