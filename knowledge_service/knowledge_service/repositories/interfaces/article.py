"""Article repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import date
from typing import TYPE_CHECKING

from knowledge_service.repositories.interfaces.base import BaseRepository

if TYPE_CHECKING:
    from knowledge_service.models import Article


class IArticleRepository(BaseRepository["Article", int]):
    """Article repository interface with specific queries."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> "Article | None":
        """Get article by slug with eager-loaded relationships."""

    @abstractmethod
    async def get_by_id_with_relations(self, entity_id: int) -> "Article | None":
        """Get article by ID with eager-loaded category, tags, attachments."""

    @abstractmethod
    async def find_articles(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
        tag_id: int | None = None,
        department: str | None = None,
        status: str | None = None,
        user_filters: dict | None = None,
        featured_only: bool = False,
        pinned_only: bool = False,
    ) -> tuple[Sequence["Article"], int]:
        """Find articles with filtering, return results + total count."""

    @abstractmethod
    async def find_department_articles(
        self, department: str, *, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence["Article"], int]:
        """Find published articles for a specific department."""

    @abstractmethod
    async def slug_exists(self, slug: str, *, exclude_id: int | None = None) -> bool:
        """Check if slug exists, optionally excluding an article ID."""

    @abstractmethod
    async def increment_view_count(self, article_id: int) -> None:
        """Increment article view count."""

    @abstractmethod
    async def update_search_vector(self, article_id: int) -> None:
        """Update PostgreSQL full-text search vector for an article."""

    @abstractmethod
    async def get_daily_views(self, article_id: int, start_date: date) -> dict[date, int]:
        """Get daily view counts from start_date for 7 days."""

    @abstractmethod
    async def get_previous_week_views(self, article_id: int, before_date: date) -> int:
        """Get total views for the 7 days before given date."""
