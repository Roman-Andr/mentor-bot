"""SQLAlchemy implementation of Meeting participant history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.models import MeetingParticipantHistory
from meeting_service.repositories.implementations.base import SqlAlchemyBaseRepository
from meeting_service.repositories.interfaces.meeting_participant_history import IMeetingParticipantHistoryRepository


class MeetingParticipantHistoryRepository(
    SqlAlchemyBaseRepository[MeetingParticipantHistory, int], IMeetingParticipantHistoryRepository
):
    """SQLAlchemy implementation of Meeting participant history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize MeetingParticipantHistoryRepository with database session."""
        super().__init__(session, MeetingParticipantHistory)

    async def create(self, entity: MeetingParticipantHistory) -> MeetingParticipantHistory:
        """Create meeting participant history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_meeting_id(
        self,
        meeting_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MeetingParticipantHistory]:
        """Get meeting participant history for a meeting with optional date filtering."""
        stmt = select(MeetingParticipantHistory).where(MeetingParticipantHistory.meeting_id == meeting_id)

        if from_date:
            stmt = stmt.where(MeetingParticipantHistory.joined_at >= from_date)
        if to_date:
            stmt = stmt.where(MeetingParticipantHistory.joined_at <= to_date)

        stmt = stmt.order_by(MeetingParticipantHistory.joined_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MeetingParticipantHistory]:
        """Get meeting participant history for a user with optional date filtering."""
        stmt = select(MeetingParticipantHistory).where(MeetingParticipantHistory.user_id == user_id)

        if from_date:
            stmt = stmt.where(MeetingParticipantHistory.joined_at >= from_date)
        if to_date:
            stmt = stmt.where(MeetingParticipantHistory.joined_at <= to_date)

        stmt = stmt.order_by(MeetingParticipantHistory.joined_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[MeetingParticipantHistory], int]:
        """Get all meeting participant history with filtering and pagination."""
        count_stmt = select(func.count(MeetingParticipantHistory.id))
        stmt = select(MeetingParticipantHistory)

        if from_date:
            stmt = stmt.where(MeetingParticipantHistory.joined_at >= from_date)
            count_stmt = count_stmt.where(MeetingParticipantHistory.joined_at >= from_date)
        if to_date:
            stmt = stmt.where(MeetingParticipantHistory.joined_at <= to_date)
            count_stmt = count_stmt.where(MeetingParticipantHistory.joined_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(MeetingParticipantHistory.joined_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
