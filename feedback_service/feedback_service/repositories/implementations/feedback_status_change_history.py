"""SQLAlchemy implementation of Feedback status change history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from feedback_service.models import FeedbackStatusChangeHistory
from feedback_service.repositories.implementations.base import SqlAlchemyBaseRepository
from feedback_service.repositories.interfaces.feedback_status_change_history import (
    IFeedbackStatusChangeHistoryRepository,
)


class FeedbackStatusChangeHistoryRepository(
    SqlAlchemyBaseRepository[FeedbackStatusChangeHistory, int], IFeedbackStatusChangeHistoryRepository
):
    """SQLAlchemy implementation of Feedback status change history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize FeedbackStatusChangeHistoryRepository with database session."""
        super().__init__(session, FeedbackStatusChangeHistory)

    async def create(self, entity: FeedbackStatusChangeHistory) -> FeedbackStatusChangeHistory:
        """Create feedback status change history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_feedback_id(
        self,
        feedback_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[FeedbackStatusChangeHistory]:
        """Get feedback status change history for a feedback with optional date filtering."""
        stmt = select(FeedbackStatusChangeHistory).where(FeedbackStatusChangeHistory.feedback_id == feedback_id)

        if from_date:
            stmt = stmt.where(FeedbackStatusChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(FeedbackStatusChangeHistory.changed_at <= to_date)

        stmt = stmt.order_by(FeedbackStatusChangeHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[FeedbackStatusChangeHistory], int]:
        """Get all feedback status change history with filtering and pagination."""
        count_stmt = select(func.count(FeedbackStatusChangeHistory.id))
        stmt = select(FeedbackStatusChangeHistory)

        if from_date:
            stmt = stmt.where(FeedbackStatusChangeHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(FeedbackStatusChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(FeedbackStatusChangeHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(FeedbackStatusChangeHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(FeedbackStatusChangeHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
