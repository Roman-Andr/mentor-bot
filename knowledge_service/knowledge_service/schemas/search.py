"""Search schemas for request/response validation."""

from typing import Any

from pydantic import BaseModel, Field

from knowledge_service.core import SearchSortBy


class SearchQuery(BaseModel):
    """Search query schema."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    category_id: int | None = Field(None, description="Filter by category ID")
    tag_ids: list[int] | None = Field(None, description="Filter by tag IDs")
    department_id: int | None = Field(None, description="Filter by department ID")
    position: str | None = Field(None, description="Filter by position")
    level: str | None = Field(None, description="Filter by employee level")
    only_published: bool = Field(default=True, description="Only show published articles")
    sort_by: SearchSortBy = Field(SearchSortBy.RELEVANCE, description="Sort order")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=10, description="Page size")


class SearchResponse(BaseModel):
    """Search response schema."""

    total: int
    results: list[dict]
    query: str
    filters: dict
    suggestions: list[str] = Field(default_factory=list)
    page: int
    size: int
    pages: int


class SearchHistoryResponse(BaseModel):
    """Search history response schema."""

    id: int
    query: str
    results_count: int
    created_at: str
    filters: dict


class SearchStats(BaseModel):
    """Search statistics schema."""

    total_searches: int
    popular_queries: list[dict[str, Any]]
    no_results_queries: list[dict[str, Any]]
    searches_by_department: dict[str, int]
    avg_results_per_search: float
    searches_last_30_days: list[dict[str, Any]]
