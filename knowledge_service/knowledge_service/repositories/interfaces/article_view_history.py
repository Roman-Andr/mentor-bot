"""Article view history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from knowledge_service.models import ArticleViewHistory
from knowledge_service.repositories.interfaces.base import BaseRepository


class IArticleViewHistoryRepository(BaseRepository["ArticleViewHistory", int]):
    """Article view history repository interface."""

    @abstractmethod
    async def create(self, entity: ArticleViewHistory) -> ArticleViewHistory:
        """Create article view history entry."""

    @abstractmethod
    async def get_by_article_id(
        self,
        article_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[ArticleViewHistory]:
        """Get article view history for an article with optional date filtering."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[ArticleViewHistory]:
        """Get article view history for a user with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[ArticleViewHistory], int]:
        """Get all article view history with filtering and pagination."""
