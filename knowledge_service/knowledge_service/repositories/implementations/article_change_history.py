"""SQLAlchemy implementation of Article change history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import ArticleChangeHistory
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.article_change_history import IArticleChangeHistoryRepository


class ArticleChangeHistoryRepository(
    SqlAlchemyBaseRepository[ArticleChangeHistory, int], IArticleChangeHistoryRepository
):
    """SQLAlchemy implementation of Article change history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ArticleChangeHistoryRepository with database session."""
        super().__init__(session, ArticleChangeHistory)

    async def create(self, entity: ArticleChangeHistory) -> ArticleChangeHistory:
        """Create article change history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_article_id(
        self,
        article_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[ArticleChangeHistory]:
        """Get article change history for an article with optional date filtering."""
        stmt = select(ArticleChangeHistory).where(ArticleChangeHistory.article_id == article_id)

        if from_date:
            stmt = stmt.where(ArticleChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(ArticleChangeHistory.changed_at <= to_date)

        stmt = stmt.order_by(ArticleChangeHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[ArticleChangeHistory], int]:
        """Get all article change history with filtering and pagination."""
        count_stmt = select(func.count(ArticleChangeHistory.id))
        stmt = select(ArticleChangeHistory)

        if from_date:
            stmt = stmt.where(ArticleChangeHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(ArticleChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(ArticleChangeHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(ArticleChangeHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(ArticleChangeHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
