"""SQLAlchemy implementation of Task repository."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.core.enums import TaskStatus
from checklists_service.models import Task
from checklists_service.repositories.implementations.base import SqlAlchemyBaseRepository
from checklists_service.repositories.interfaces.task import ITaskRepository


class TaskRepository(SqlAlchemyBaseRepository[Task, int], ITaskRepository):
    """SQLAlchemy implementation of Task repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize TaskRepository with database session."""
        super().__init__(session, Task)

    async def find_by_checklist(
        self,
        checklist_id: int,
        *,
        status: str | None = None,
        category: str | None = None,
        overdue_only: bool = False,
    ) -> Sequence[Task]:
        """Find tasks for a specific checklist with optional filters."""
        stmt = select(Task).where(Task.checklist_id == checklist_id)

        if status:
            stmt = stmt.where(Task.status == status)

        if category:
            stmt = stmt.where(Task.category == category)

        if overdue_only:
            now = datetime.now(UTC)
            stmt = stmt.where(
                and_(
                    Task.due_date < now,
                    Task.status != TaskStatus.COMPLETED,
                )
            )

        stmt = stmt.order_by(Task.order)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_assigned(
        self,
        assignee_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> tuple[Sequence[Task], int]:
        """Find tasks assigned to a specific user."""
        stmt = select(Task).where(Task.assignee_id == assignee_id)
        count_stmt = select(func.count(Task.id)).where(Task.assignee_id == assignee_id)

        if status:
            stmt = stmt.where(Task.status == status)
            count_stmt = count_stmt.where(Task.status == status)

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        stmt = stmt.offset(skip).limit(limit).order_by(Task.due_date)
        result = await self._session.execute(stmt)
        tasks = result.scalars().all()

        return tasks, total

    async def get_dependencies(self, task_id: int) -> dict[str, Any]:
        """Get task dependencies and blockers."""
        task = await self.get_by_id(task_id)
        if not task:
            return {}

        dependencies = []
        if task.depends_on:
            dep_stmt = select(Task).where(Task.id.in_(task.depends_on))
            result = await self._session.execute(dep_stmt)
            dependencies = [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                }
                for t in result.scalars().all()
            ]

        blocked_stmt = select(Task).where(Task.depends_on.contains([task_id]))
        result = await self._session.execute(blocked_stmt)
        blocked_tasks = [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
            }
            for t in result.scalars().all()
        ]

        return {
            "task_id": task_id,
            "title": task.title,
            "status": task.status,
            "dependencies": dependencies,
            "blocked_tasks": blocked_tasks,
            "can_complete": all(dep["status"] == TaskStatus.COMPLETED for dep in dependencies),
        }

    async def get_incomplete_dependencies(self, task_id: int) -> Sequence[Task]:
        """Get incomplete tasks that this task depends on."""
        task = await self.get_by_id(task_id)
        if not task or not task.depends_on:
            return []

        stmt = select(Task).where(
            Task.id.in_(task.depends_on),
            Task.status != TaskStatus.COMPLETED,
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_blocked_by(self, task_id: int) -> Sequence[Task]:
        """Get tasks that are blocked by this task."""
        stmt = select(Task).where(
            Task.depends_on.contains([task_id]),
            Task.status == TaskStatus.BLOCKED,
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count_by_status(self, checklist_id: int) -> dict[str, int]:
        """Count tasks by status for a checklist."""
        stmt = select(Task.status, func.count(Task.id)).where(Task.checklist_id == checklist_id).group_by(Task.status)
        result = await self._session.execute(stmt)
        return {str(k): v for k, v in result.all()}

    async def count_by_category(self, checklist_id: int) -> dict[str, int]:
        """Count tasks by category for a checklist."""
        stmt = (
            select(Task.category, func.count(Task.id)).where(Task.checklist_id == checklist_id).group_by(Task.category)
        )
        result = await self._session.execute(stmt)
        return {str(k): v for k, v in result.all()}

    async def count_overdue(self, checklist_id: int) -> int:
        """Count overdue tasks for a checklist."""
        now = datetime.now(UTC)
        stmt = select(func.count(Task.id)).where(
            Task.checklist_id == checklist_id,
            Task.due_date < now,
            Task.status != TaskStatus.COMPLETED,
        )
        result = await self._session.execute(stmt)
        return cast("int", result.scalar_one() or 0)

    async def get_blocked_tasks(self, checklist_id: int) -> Sequence[Task]:
        """Get blocked tasks for a checklist."""
        stmt = select(Task).where(
            Task.checklist_id == checklist_id,
            Task.status == TaskStatus.BLOCKED,
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_by_ids(self, task_ids: list[int]) -> Sequence[Task]:
        """Find tasks by a list of IDs."""
        if not task_ids:
            return []

        stmt = select(Task).where(Task.id.in_(task_ids))
        result = await self._session.execute(stmt)
        return result.scalars().all()
