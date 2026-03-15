"""Tag repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

from knowledge_service.repositories.interfaces.base import BaseRepository

if TYPE_CHECKING:
    from knowledge_service.models import Tag


class ITagRepository(BaseRepository["Tag", int]):
    """Tag repository interface with specific queries."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> "Tag | None":
        """Get tag by slug."""

    @abstractmethod
    async def get_by_id_with_articles(self, entity_id: int) -> "Tag | None":
        """Get tag by ID with eager-loaded articles."""

    @abstractmethod
    async def find_by_name_or_slug(self, name: str, slug: str) -> "Tag | None":
        """Find tag by name or slug (for duplicate checking)."""

    @abstractmethod
    async def find_by_name_or_slug_excluding(self, name: str, slug: str, exclude_id: int) -> "Tag | None":
        """Find tag by name or slug excluding given ID (for update conflict checking)."""

    @abstractmethod
    async def find_tags(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        sort_by: str = "usage_count",
        sort_desc: bool = True,
    ) -> tuple[Sequence["Tag"], int]:
        """Find tags with filtering and sorting, return results + total count."""

    @abstractmethod
    async def get_popular(self, limit: int = 20) -> Sequence["Tag"]:
        """Get most popular tags by usage count."""

    @abstractmethod
    async def find_by_article(self, article_id: int) -> Sequence["Tag"]:
        """Get tags for a specific article."""
