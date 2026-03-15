"""Search schemas for Telegram bot."""

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Search result schema."""

    id: int
    title: str
    slug: str
    excerpt: str | None = None
    category_name: str | None = None
    tags: list[str] = Field(default_factory=list)
    relevance_score: float = 0.0
    highlighted_content: str | None = None
    published_at: str | None = None


class SearchResponse(BaseModel):
    """Search response schema."""

    total: int
    results: list[SearchResult]
    query: str
    filters: dict
    suggestions: list[str] = Field(default_factory=list)
    page: int
    size: int
    pages: int
