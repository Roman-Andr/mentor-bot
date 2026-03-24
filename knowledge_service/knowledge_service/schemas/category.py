"""Category schemas for request/response validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from knowledge_service.core import EmployeeLevel


class CategoryBase(BaseModel):
    """Base category schema."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    parent_id: int | None = None
    order: int = Field(0, ge=0)
    department_id: int | None = None
    position: str | None = Field(None, max_length=100)
    level: EmployeeLevel | None = None
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)


class CategoryCreate(CategoryBase):
    """Category creation schema."""


class CategoryUpdate(BaseModel):
    """Category update schema."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    parent_id: int | None = None
    order: int | None = Field(None, ge=0)
    department_id: int | None = None
    position: str | None = Field(None, max_length=100)
    level: EmployeeLevel | None = None
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)


class CategoryResponse(CategoryBase):
    """Category response schema."""

    id: int
    parent_name: str | None = None
    children_count: int = 0
    articles_count: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CategoryWithArticles(CategoryResponse):
    """Category response with articles."""

    articles: list[dict[str, Any]] = Field(default_factory=list)


class CategoryListResponse(BaseModel):
    """Category list response schema."""

    total: int
    categories: list[CategoryResponse]
    page: int
    size: int
    pages: int
