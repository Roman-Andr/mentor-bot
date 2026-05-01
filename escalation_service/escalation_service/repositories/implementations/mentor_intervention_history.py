"""SQLAlchemy implementation of Mentor intervention history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from escalation_service.models import MentorInterventionHistory
from escalation_service.repositories.implementations.base import SqlAlchemyBaseRepository
from escalation_service.repositories.interfaces.mentor_intervention_history import IMentorInterventionHistoryRepository


class MentorInterventionHistoryRepository(
    SqlAlchemyBaseRepository[MentorInterventionHistory, int], IMentorInterventionHistoryRepository
):
    """SQLAlchemy implementation of Mentor intervention history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize MentorInterventionHistoryRepository with database session."""
        super().__init__(session, MentorInterventionHistory)

    async def create(self, entity: MentorInterventionHistory) -> MentorInterventionHistory:
        """Create mentor intervention history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_escalation_id(
        self,
        escalation_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MentorInterventionHistory]:
        """Get mentor intervention history for an escalation with optional date filtering."""
        stmt = select(MentorInterventionHistory).where(MentorInterventionHistory.escalation_id == escalation_id)

        if from_date:
            stmt = stmt.where(MentorInterventionHistory.intervention_at >= from_date)
        if to_date:
            stmt = stmt.where(MentorInterventionHistory.intervention_at <= to_date)

        stmt = stmt.order_by(MentorInterventionHistory.intervention_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_mentor_id(
        self,
        mentor_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MentorInterventionHistory]:
        """Get mentor intervention history for a mentor with optional date filtering."""
        stmt = select(MentorInterventionHistory).where(MentorInterventionHistory.mentor_id == mentor_id)

        if from_date:
            stmt = stmt.where(MentorInterventionHistory.intervention_at >= from_date)
        if to_date:
            stmt = stmt.where(MentorInterventionHistory.intervention_at <= to_date)

        stmt = stmt.order_by(MentorInterventionHistory.intervention_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[MentorInterventionHistory], int]:
        """Get all mentor intervention history with filtering and pagination."""
        count_stmt = select(func.count(MentorInterventionHistory.id))
        stmt = select(MentorInterventionHistory)

        if from_date:
            stmt = stmt.where(MentorInterventionHistory.intervention_at >= from_date)
            count_stmt = count_stmt.where(MentorInterventionHistory.intervention_at >= from_date)
        if to_date:
            stmt = stmt.where(MentorInterventionHistory.intervention_at <= to_date)
            count_stmt = count_stmt.where(MentorInterventionHistory.intervention_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(MentorInterventionHistory.intervention_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
