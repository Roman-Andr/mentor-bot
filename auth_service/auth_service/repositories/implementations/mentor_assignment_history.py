"""SQLAlchemy implementation of Mentor assignment history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import MentorAssignmentHistory
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.mentor_assignment_history import IMentorAssignmentHistoryRepository


class MentorAssignmentHistoryRepository(
    SqlAlchemyBaseRepository[MentorAssignmentHistory, int], IMentorAssignmentHistoryRepository
):
    """SQLAlchemy implementation of Mentor assignment history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize MentorAssignmentHistoryRepository with database session."""
        super().__init__(session, MentorAssignmentHistory)

    async def create(self, entity: MentorAssignmentHistory) -> MentorAssignmentHistory:
        """Create mentor assignment history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MentorAssignmentHistory]:
        """Get mentor assignment history for a user with optional date filtering."""
        stmt = select(MentorAssignmentHistory).where(MentorAssignmentHistory.user_id == user_id)

        if from_date:
            stmt = stmt.where(MentorAssignmentHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(MentorAssignmentHistory.changed_at <= to_date)

        stmt = stmt.order_by(MentorAssignmentHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_mentor_id(
        self,
        mentor_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MentorAssignmentHistory]:
        """Get mentor assignment history for a mentor with optional date filtering."""
        stmt = select(MentorAssignmentHistory).where(MentorAssignmentHistory.mentor_id == mentor_id)

        if from_date:
            stmt = stmt.where(MentorAssignmentHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(MentorAssignmentHistory.changed_at <= to_date)

        stmt = stmt.order_by(MentorAssignmentHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[MentorAssignmentHistory], int]:
        """Get all mentor assignment history with filtering and pagination."""
        count_stmt = select(func.count(MentorAssignmentHistory.id))
        stmt = select(MentorAssignmentHistory)

        if from_date:
            stmt = stmt.where(MentorAssignmentHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(MentorAssignmentHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(MentorAssignmentHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(MentorAssignmentHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(MentorAssignmentHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
