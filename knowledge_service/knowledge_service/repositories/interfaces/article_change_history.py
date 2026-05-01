"""Article change history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from knowledge_service.models import ArticleChangeHistory
from knowledge_service.repositories.interfaces.base import BaseRepository


class IArticleChangeHistoryRepository(BaseRepository["ArticleChangeHistory", int]):
    """Article change history repository interface."""

    @abstractmethod
    async def create(self, entity: ArticleChangeHistory) -> ArticleChangeHistory:
        """Create article change history entry."""

    @abstractmethod
    async def get_by_article_id(
        self,
        article_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[ArticleChangeHistory]:
        """Get article change history for an article with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[ArticleChangeHistory], int]:
        """Get all article change history with filtering and pagination."""
