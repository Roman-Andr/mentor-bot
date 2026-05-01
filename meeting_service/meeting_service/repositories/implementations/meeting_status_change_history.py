"""SQLAlchemy implementation of Meeting status change history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.models import MeetingStatusChangeHistory
from meeting_service.repositories.implementations.base import SqlAlchemyBaseRepository
from meeting_service.repositories.interfaces.meeting_status_change_history import IMeetingStatusChangeHistoryRepository


class MeetingStatusChangeHistoryRepository(
    SqlAlchemyBaseRepository[MeetingStatusChangeHistory, int], IMeetingStatusChangeHistoryRepository
):
    """SQLAlchemy implementation of Meeting status change history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize MeetingStatusChangeHistoryRepository with database session."""
        super().__init__(session, MeetingStatusChangeHistory)

    async def create(self, entity: MeetingStatusChangeHistory) -> MeetingStatusChangeHistory:
        """Create meeting status change history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_meeting_id(
        self,
        meeting_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MeetingStatusChangeHistory]:
        """Get meeting status change history for a meeting with optional date filtering."""
        stmt = select(MeetingStatusChangeHistory).where(MeetingStatusChangeHistory.meeting_id == meeting_id)

        if from_date:
            stmt = stmt.where(MeetingStatusChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(MeetingStatusChangeHistory.changed_at <= to_date)

        stmt = stmt.order_by(MeetingStatusChangeHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[MeetingStatusChangeHistory], int]:
        """Get all meeting status change history with filtering and pagination."""
        count_stmt = select(func.count(MeetingStatusChangeHistory.id))
        stmt = select(MeetingStatusChangeHistory)

        if from_date:
            stmt = stmt.where(MeetingStatusChangeHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(MeetingStatusChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(MeetingStatusChangeHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(MeetingStatusChangeHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(MeetingStatusChangeHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
