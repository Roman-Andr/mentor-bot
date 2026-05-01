"""Knowledge analytics schemas for request/response validation."""

from pydantic import BaseModel


class TopArticleStats(BaseModel):
    """Top articles by view count."""

    article_id: int
    title: str
    view_count: int
    unique_viewers: int


class TimeseriesPoint(BaseModel):
    """Timeseries data point for views over time."""

    bucket: str
    views: int
    unique_viewers: int


class CategoryStats(BaseModel):
    """View statistics by category."""

    category_id: int
    category_name: str
    view_count: int


class TagStats(BaseModel):
    """View statistics by tag."""

    tag_id: int
    tag_name: str
    view_count: int


class KnowledgeSummary(BaseModel):
    """Summary statistics for knowledge base."""

    total_views: int
    unique_viewers: int
    total_articles: int
    avg_views_per_article: float
