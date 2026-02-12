"""Meeting material schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from meeting_service.core.enums import MaterialType


class MaterialBase(BaseModel):
    """Base meeting material schema."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    url: str = Field(..., max_length=500)
    type: MaterialType
    order: int = 0


class MaterialCreate(MaterialBase):
    """Material creation schema."""


class MaterialResponse(MaterialBase):
    """Material response schema."""

    id: int
    meeting_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
