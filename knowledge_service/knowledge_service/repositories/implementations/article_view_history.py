"""SQLAlchemy implementation of Article view history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import ArticleViewHistory
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.article_view_history import IArticleViewHistoryRepository


class ArticleViewHistoryRepository(SqlAlchemyBaseRepository[ArticleViewHistory, int], IArticleViewHistoryRepository):
    """SQLAlchemy implementation of Article view history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ArticleViewHistoryRepository with database session."""
        super().__init__(session, ArticleViewHistory)

    async def create(self, entity: ArticleViewHistory) -> ArticleViewHistory:
        """Create article view history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_article_id(
        self,
        article_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[ArticleViewHistory]:
        """Get article view history for an article with optional date filtering."""
        stmt = select(ArticleViewHistory).where(ArticleViewHistory.article_id == article_id)

        if from_date:
            stmt = stmt.where(ArticleViewHistory.viewed_at >= from_date)
        if to_date:
            stmt = stmt.where(ArticleViewHistory.viewed_at <= to_date)

        stmt = stmt.order_by(ArticleViewHistory.viewed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[ArticleViewHistory]:
        """Get article view history for a user with optional date filtering."""
        stmt = select(ArticleViewHistory).where(ArticleViewHistory.user_id == user_id)

        if from_date:
            stmt = stmt.where(ArticleViewHistory.viewed_at >= from_date)
        if to_date:
            stmt = stmt.where(ArticleViewHistory.viewed_at <= to_date)

        stmt = stmt.order_by(ArticleViewHistory.viewed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[ArticleViewHistory], int]:
        """Get all article view history with filtering and pagination."""
        count_stmt = select(func.count(ArticleViewHistory.id))
        stmt = select(ArticleViewHistory)

        if from_date:
            stmt = stmt.where(ArticleViewHistory.viewed_at >= from_date)
            count_stmt = count_stmt.where(ArticleViewHistory.viewed_at >= from_date)
        if to_date:
            stmt = stmt.where(ArticleViewHistory.viewed_at <= to_date)
            count_stmt = count_stmt.where(ArticleViewHistory.viewed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(ArticleViewHistory.viewed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
