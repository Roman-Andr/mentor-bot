"""Department schemas."""

from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    """Schema for creating a department."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class DepartmentUpdate(BaseModel):
    """Schema for updating a department."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class DepartmentResponse(BaseModel):
    """Schema for department response."""

    id: int
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}
