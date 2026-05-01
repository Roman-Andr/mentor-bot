"""Department document schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentDocumentBase(BaseModel):
    """Base department document schema."""

    department_id: int
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    category: str = Field(..., min_length=1, max_length=100)
    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_size: int = Field(..., ge=0)
    mime_type: str = Field(..., min_length=1, max_length=100)
    is_public: bool = False
    uploaded_by: int


class DepartmentDocumentCreate(DepartmentDocumentBase):
    """Department document creation schema."""


class DepartmentDocumentUpdate(BaseModel):
    """Department document update schema."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    category: str | None = Field(None, min_length=1, max_length=100)
    is_public: bool | None = None


class DepartmentDocumentResponse(DepartmentDocumentBase):
    """Department document response schema."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DepartmentDocumentListResponse(BaseModel):
    """Department document list response schema."""

    total: int
    documents: list[DepartmentDocumentResponse]
