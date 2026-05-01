"""SQLAlchemy implementation of Task completion history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.models import TaskCompletionHistory
from checklists_service.repositories.implementations.base import SqlAlchemyBaseRepository
from checklists_service.repositories.interfaces.task_completion_history import ITaskCompletionHistoryRepository


class TaskCompletionHistoryRepository(
    SqlAlchemyBaseRepository[TaskCompletionHistory, int], ITaskCompletionHistoryRepository
):
    """SQLAlchemy implementation of Task completion history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize TaskCompletionHistoryRepository with database session."""
        super().__init__(session, TaskCompletionHistory)

    async def create(self, entity: TaskCompletionHistory) -> TaskCompletionHistory:
        """Create task completion history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_task_id(
        self,
        task_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[TaskCompletionHistory]:
        """Get task completion history for a task with optional date filtering."""
        stmt = select(TaskCompletionHistory).where(TaskCompletionHistory.task_id == task_id)

        if from_date:
            stmt = stmt.where(TaskCompletionHistory.completed_at >= from_date)
        if to_date:
            stmt = stmt.where(TaskCompletionHistory.completed_at <= to_date)

        stmt = stmt.order_by(TaskCompletionHistory.completed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_checklist_id(
        self,
        checklist_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[TaskCompletionHistory]:
        """Get task completion history for a checklist with optional date filtering."""
        stmt = select(TaskCompletionHistory).where(TaskCompletionHistory.checklist_id == checklist_id)

        if from_date:
            stmt = stmt.where(TaskCompletionHistory.completed_at >= from_date)
        if to_date:
            stmt = stmt.where(TaskCompletionHistory.completed_at <= to_date)

        stmt = stmt.order_by(TaskCompletionHistory.completed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[TaskCompletionHistory]:
        """Get task completion history for a user with optional date filtering."""
        stmt = select(TaskCompletionHistory).where(TaskCompletionHistory.user_id == user_id)

        if from_date:
            stmt = stmt.where(TaskCompletionHistory.completed_at >= from_date)
        if to_date:
            stmt = stmt.where(TaskCompletionHistory.completed_at <= to_date)

        stmt = stmt.order_by(TaskCompletionHistory.completed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[TaskCompletionHistory], int]:
        """Get all task completion history with filtering and pagination."""
        count_stmt = select(func.count(TaskCompletionHistory.id))
        stmt = select(TaskCompletionHistory)

        if from_date:
            stmt = stmt.where(TaskCompletionHistory.completed_at >= from_date)
            count_stmt = count_stmt.where(TaskCompletionHistory.completed_at >= from_date)
        if to_date:
            stmt = stmt.where(TaskCompletionHistory.completed_at <= to_date)
            count_stmt = count_stmt.where(TaskCompletionHistory.completed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(TaskCompletionHistory.completed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
