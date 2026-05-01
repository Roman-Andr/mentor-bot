"""SQLAlchemy implementation of Category change history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import CategoryChangeHistory
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.category_change_history import ICategoryChangeHistoryRepository


class CategoryChangeHistoryRepository(
    SqlAlchemyBaseRepository[CategoryChangeHistory, int], ICategoryChangeHistoryRepository
):
    """SQLAlchemy implementation of Category change history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize CategoryChangeHistoryRepository with database session."""
        super().__init__(session, CategoryChangeHistory)

    async def create(self, entity: CategoryChangeHistory) -> CategoryChangeHistory:
        """Create category change history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_category_id(
        self,
        category_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[CategoryChangeHistory]:
        """Get category change history for a category with optional date filtering."""
        stmt = select(CategoryChangeHistory).where(CategoryChangeHistory.category_id == category_id)

        if from_date:
            stmt = stmt.where(CategoryChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(CategoryChangeHistory.changed_at <= to_date)

        stmt = stmt.order_by(CategoryChangeHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[CategoryChangeHistory], int]:
        """Get all category change history with filtering and pagination."""
        count_stmt = select(func.count(CategoryChangeHistory.id))
        stmt = select(CategoryChangeHistory)

        if from_date:
            stmt = stmt.where(CategoryChangeHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(CategoryChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(CategoryChangeHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(CategoryChangeHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(CategoryChangeHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
