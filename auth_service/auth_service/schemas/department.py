"""Department schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    """Base department schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class DepartmentCreate(DepartmentBase):
    """Department creation schema."""


class DepartmentUpdate(BaseModel):
    """Department update schema."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class DepartmentResponse(DepartmentBase):
    """Department response schema."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DepartmentListResponse(BaseModel):
    """Department list response schema."""

    total: int
    departments: list[DepartmentResponse]
    page: int
    size: int
    pages: int
