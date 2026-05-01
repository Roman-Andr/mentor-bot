"""SQLAlchemy implementation of Template change history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.models import TemplateChangeHistory
from checklists_service.repositories.implementations.base import SqlAlchemyBaseRepository
from checklists_service.repositories.interfaces.template_change_history import ITemplateChangeHistoryRepository


class TemplateChangeHistoryRepository(
    SqlAlchemyBaseRepository[TemplateChangeHistory, int], ITemplateChangeHistoryRepository
):
    """SQLAlchemy implementation of Template change history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize TemplateChangeHistoryRepository with database session."""
        super().__init__(session, TemplateChangeHistory)

    async def create(self, entity: TemplateChangeHistory) -> TemplateChangeHistory:
        """Create template change history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_template_id(
        self,
        template_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[TemplateChangeHistory]:
        """Get template change history for a template with optional date filtering."""
        stmt = select(TemplateChangeHistory).where(TemplateChangeHistory.template_id == template_id)

        if from_date:
            stmt = stmt.where(TemplateChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(TemplateChangeHistory.changed_at <= to_date)

        stmt = stmt.order_by(TemplateChangeHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[TemplateChangeHistory], int]:
        """Get all template change history with filtering and pagination."""
        count_stmt = select(func.count(TemplateChangeHistory.id))
        stmt = select(TemplateChangeHistory)

        if from_date:
            stmt = stmt.where(TemplateChangeHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(TemplateChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(TemplateChangeHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(TemplateChangeHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(TemplateChangeHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
