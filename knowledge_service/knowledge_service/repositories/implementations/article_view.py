"""SQLAlchemy implementation of ArticleView repository."""

from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models.article_view import ArticleView
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.article_view import IArticleViewRepository


class ArticleViewRepository(SqlAlchemyBaseRepository[ArticleView, int], IArticleViewRepository):
    """SQLAlchemy implementation of ArticleView repository."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ArticleView)

    async def record_view(self, article_id: int, user_id: int | None = None) -> ArticleView:
        view = ArticleView(article_id=article_id, user_id=user_id)
        return await self.create(view)
