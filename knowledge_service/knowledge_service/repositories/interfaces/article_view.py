"""ArticleView repository interface."""

from abc import abstractmethod

from knowledge_service.models.article_view import ArticleView
from knowledge_service.repositories.interfaces.base import BaseRepository


class IArticleViewRepository(BaseRepository["ArticleView", int]):
    """ArticleView repository interface with specific queries."""

    @abstractmethod
    async def record_view(self, article_id: int, user_id: int | None = None) -> ArticleView:
        """Record a new article view."""
