"""ArticleView repository interface."""

from abc import abstractmethod
from datetime import datetime
from typing import Literal

from knowledge_service.models.article_view import ArticleView
from knowledge_service.repositories.interfaces.base import BaseRepository


class IArticleViewRepository(BaseRepository["ArticleView", int]):
    """ArticleView repository interface with specific queries."""

    @abstractmethod
    async def record_view(self, article_id: int, user_id: int | None = None) -> ArticleView:
        """Record a new article view."""

    @abstractmethod
    async def get_top_articles(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 10,
        department_id: int | None = None,
    ) -> list[dict[str, object]]:
        """Get top articles by view count."""

    @abstractmethod
    async def get_timeseries(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        granularity: Literal["day", "week"] = "day",
        article_id: int | None = None,
    ) -> list[dict[str, object]]:
        """Get views timeseries data."""

    @abstractmethod
    async def get_by_category(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[dict[str, object]]:
        """Get view statistics by category."""

    @abstractmethod
    async def get_by_tag(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[dict[str, object]]:
        """Get view statistics by tag."""

    @abstractmethod
    async def get_summary_stats(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict[str, object]:
        """Get summary statistics for knowledge base."""
