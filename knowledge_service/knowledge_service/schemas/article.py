"""Article schemas for request/response validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from knowledge_service.core import ArticleStatus, EmployeeLevel
from knowledge_service.schemas.tag import TagResponse


class ArticleBase(BaseModel):
    """Base article schema."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    excerpt: str | None = Field(None, max_length=1000)
    category_id: int | None = None
    department: str | None = Field(None, max_length=100)
    position: str | None = Field(None, max_length=100)
    level: EmployeeLevel | None = None
    is_pinned: bool = False
    is_featured: bool = False
    meta_title: str | None = Field(None, max_length=200)
    meta_description: str | None = Field(None, max_length=500)
    keywords: list[str] = Field(default_factory=list)


class ArticleCreate(ArticleBase):
    """Article creation schema."""

    status: ArticleStatus = ArticleStatus.DRAFT
    tag_ids: list[int] = Field(default_factory=list)


class ArticleUpdate(BaseModel):
    """Article update schema."""

    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = Field(None, min_length=1)
    excerpt: str | None = Field(None, max_length=1000)
    category_id: int | None = None
    department: str | None = Field(None, max_length=100)
    position: str | None = Field(None, max_length=100)
    level: EmployeeLevel | None = None
    status: ArticleStatus | None = None
    is_pinned: bool | None = None
    is_featured: bool | None = None
    meta_title: str | None = Field(None, max_length=200)
    meta_description: str | None = Field(None, max_length=500)
    keywords: list[str] | None = None
    tag_ids: list[int] | None = None


class ArticleResponse(ArticleBase):
    """Article response schema."""

    id: int
    slug: str
    status: ArticleStatus
    author_id: int
    author_name: str
    view_count: int
    category_name: str | None = None
    tags: list[TagResponse] = Field(default_factory=list)
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None
    published_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    """Article list response schema."""

    total: int
    articles: list[ArticleResponse]
    page: int
    size: int
    pages: int


class ArticleViewStats(BaseModel):
    """Article view statistics schema."""

    article_id: int
    title: str
    view_count: int
    daily_views: list[dict[str, Any]]
    weekly_growth: float
    popular_tags: list[str]


class ArticleSearchResult(BaseModel):
    """Article search result schema."""

    id: int
    title: str
    slug: str
    excerpt: str | None
    category_name: str | None
    tags: list[str]
    relevance_score: float
    highlighted_content: str | None = None
    published_at: datetime | None = None
