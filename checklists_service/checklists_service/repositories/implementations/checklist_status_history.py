"""SQLAlchemy implementation of Checklist status history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.models import ChecklistStatusHistory
from checklists_service.repositories.implementations.base import SqlAlchemyBaseRepository
from checklists_service.repositories.interfaces.checklist_status_history import IChecklistStatusHistoryRepository


class ChecklistStatusHistoryRepository(
    SqlAlchemyBaseRepository[ChecklistStatusHistory, int], IChecklistStatusHistoryRepository
):
    """SQLAlchemy implementation of Checklist status history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ChecklistStatusHistoryRepository with database session."""
        super().__init__(session, ChecklistStatusHistory)

    async def create(self, entity: ChecklistStatusHistory) -> ChecklistStatusHistory:
        """Create checklist status history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_checklist_id(
        self,
        checklist_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[ChecklistStatusHistory]:
        """Get checklist status history for a checklist with optional date filtering."""
        stmt = select(ChecklistStatusHistory).where(ChecklistStatusHistory.checklist_id == checklist_id)

        if from_date:
            stmt = stmt.where(ChecklistStatusHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(ChecklistStatusHistory.changed_at <= to_date)

        stmt = stmt.order_by(ChecklistStatusHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[ChecklistStatusHistory]:
        """Get checklist status history for a user with optional date filtering."""
        stmt = select(ChecklistStatusHistory).where(ChecklistStatusHistory.user_id == user_id)

        if from_date:
            stmt = stmt.where(ChecklistStatusHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(ChecklistStatusHistory.changed_at <= to_date)

        stmt = stmt.order_by(ChecklistStatusHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[ChecklistStatusHistory], int]:
        """Get all checklist status history with filtering and pagination."""
        count_stmt = select(func.count(ChecklistStatusHistory.id))
        stmt = select(ChecklistStatusHistory)

        if from_date:
            stmt = stmt.where(ChecklistStatusHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(ChecklistStatusHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(ChecklistStatusHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(ChecklistStatusHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(ChecklistStatusHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
