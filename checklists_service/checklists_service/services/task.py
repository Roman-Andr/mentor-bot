"""Task management service."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.core import NotFoundException, TaskStatus, ValidationException
from checklists_service.core.enums import ChecklistStatus
from checklists_service.models import Checklist, Task
from checklists_service.schemas import TaskBulkUpdate, TaskProgress, TaskUpdate


class TaskService:
    """Service for task management operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize task service with database session."""
        self.db = db

    async def get_task(self, task_id: int) -> Task:
        """Get task by ID."""
        stmt = select(Task).where(Task.id == task_id)
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            msg = "Task"
            raise NotFoundException(msg)

        return task

    async def get_checklist_tasks(
        self,
        checklist_id: int,
        status: str | None = None,
        category: str | None = None,
        *,
        overdue_only: bool = False,
    ) -> list[Task]:
        """Get tasks for a specific checklist."""
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
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_assigned_tasks(
        self,
        assignee_id: int,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> tuple[list[Task], int]:
        """Get tasks assigned to a user."""
        stmt = select(Task).where(Task.assignee_id == assignee_id)
        count_stmt = select(func.count(Task.id)).where(Task.assignee_id == assignee_id)

        if status:
            stmt = stmt.where(Task.status == status)
            count_stmt = count_stmt.where(Task.status == status)

        result = await self.db.execute(count_stmt)
        total = result.scalar_one()

        stmt = stmt.offset(skip).limit(limit).order_by(Task.due_date)
        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())

        return tasks, total

    async def update_task(self, task_id: int, update_data: TaskUpdate) -> Task:
        """Update task."""
        task = await self.get_task(task_id)

        if update_data.status and not self._is_valid_status_transition(task.status, update_data.status):
            msg = f"Invalid status transition from {task.status} to {update_data.status}"
            raise ValidationException(msg)

        if update_data.status == TaskStatus.COMPLETED and task.status != TaskStatus.COMPLETED:
            if not update_data.completed_at:
                update_data.completed_at = datetime.now(UTC)

            if task.depends_on:
                stmt = select(Task).where(
                    Task.id.in_(task.depends_on),
                    Task.status != TaskStatus.COMPLETED,
                )
                result = await self.db.execute(stmt)
                incomplete_deps = list(result.scalars().all())

                if incomplete_deps:
                    dep_titles = [t.title for t in incomplete_deps]
                    msg = f"Cannot complete task. Dependencies not completed: {', '.join(dep_titles)}"
                    raise ValidationException(msg)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)

        if update_data.status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.now(UTC)

        task.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(task)

        await self._update_checklist_progress(task.checklist_id)

        return task

    async def update_task_progress(self, task_id: int, progress_data: TaskProgress) -> Task:
        """Update task progress."""
        task = await self.get_task(task_id)

        task.status = progress_data.status

        if progress_data.notes:
            if task.completion_notes:
                task.completion_notes += f"\n\n{progress_data.notes}"
            else:
                task.completion_notes = progress_data.notes

        if progress_data.attachments:
            task.attachments.extend(progress_data.attachments)

        if progress_data.status == TaskStatus.COMPLETED and task.status != TaskStatus.COMPLETED:
            task.completed_at = datetime.now(UTC)

            if task.depends_on:
                stmt = select(Task).where(
                    Task.id.in_(task.depends_on),
                    Task.status != TaskStatus.COMPLETED,
                )
                result = await self.db.execute(stmt)
                incomplete_deps = list(result.scalars().all())

                if incomplete_deps:
                    dep_titles = [t.title for t in incomplete_deps]
                    msg = f"Cannot complete task. Dependencies not completed: {', '.join(dep_titles)}"
                    raise ValidationException(msg)

        task.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(task)

        await self._update_checklist_progress(task.checklist_id)

        return task

    async def complete_task(self, task_id: int, completed_by: int, notes: str | None = None) -> Task:
        """Mark task as completed."""
        task = await self.get_task(task_id)

        if task.status == TaskStatus.COMPLETED:
            return task

        if task.depends_on:
            stmt = select(Task).where(
                Task.id.in_(task.depends_on),
                Task.status != TaskStatus.COMPLETED,
            )
            result = await self.db.execute(stmt)
            incomplete_deps = list(result.scalars().all())

            if incomplete_deps:
                dep_titles = [t.title for t in incomplete_deps]
                msg = f"Cannot complete task. Dependencies not completed: {', '.join(dep_titles)}"
                raise ValidationException(msg)

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(UTC)
        task.completed_by = completed_by

        if notes:
            if task.completion_notes:
                task.completion_notes += f"\n\n{notes}"
            else:
                task.completion_notes = notes

        task.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(task)

        await self._update_checklist_progress(task.checklist_id)

        await self._unblock_dependent_tasks(task_id)

        return task

    async def bulk_update_tasks(self, bulk_data: TaskBulkUpdate) -> None:
        """Bulk update tasks."""
        if not bulk_data.task_ids:
            return

        stmt = select(Task).where(Task.id.in_(bulk_data.task_ids))
        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())

        if len(tasks) != len(bulk_data.task_ids):
            msg = "Some tasks not found"
            raise ValidationException(msg)

        for task in tasks:
            update_data = bulk_data.model_dump(exclude_unset=True, exclude={"task_ids"})
            for field, value in update_data.items():
                setattr(task, field, value)
            task.updated_at = datetime.now(UTC)

        await self.db.commit()

        checklist_ids = {task.checklist_id for task in tasks}
        for checklist_id in checklist_ids:
            await self._update_checklist_progress(checklist_id)

    async def get_task_dependencies(self, task_id: int) -> dict[str, Any]:
        """Get task dependencies and blockers."""
        task = await self.get_task(task_id)

        dependencies = []
        if task.depends_on:
            stmt = select(Task).where(Task.id.in_(task.depends_on))
            result = await self.db.execute(stmt)
            dependencies = [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                }
                for t in result.scalars().all()
            ]

        stmt = select(Task).where(
            Task.depends_on.contains([task_id]),
        )
        result = await self.db.execute(stmt)
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

    def _is_valid_status_transition(self, current_status: str, new_status: str) -> bool:
        """Validate task status transition."""
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
            TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
            TaskStatus.BLOCKED: [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
            TaskStatus.COMPLETED: [],
            TaskStatus.CANCELLED: [TaskStatus.PENDING],
        }

        return new_status in valid_transitions.get(current_status, [])

    async def _update_checklist_progress(self, checklist_id: int) -> None:
        """Update checklist progress after task changes."""
        stmt = select(
            func.count(Task.id).label("total"),
            func.count(Task.id).filter(Task.status == TaskStatus.COMPLETED).label("completed"),
        ).where(Task.checklist_id == checklist_id)

        result = await self.db.execute(stmt)
        row = result.one()

        total = row.total or 0
        completed = row.completed or 0

        progress = (completed / total * 100) if total > 0 else 0

        stmt = select(Checklist).where(Checklist.id == checklist_id)
        result = await self.db.execute(stmt)
        checklist = result.scalar_one()

        checklist.completed_tasks = completed
        checklist.total_tasks = total
        checklist.progress_percentage = round(progress)

        if completed == total and total > 0:
            checklist.status = ChecklistStatus.COMPLETED
            checklist.completed_at = datetime.now(UTC)

        checklist.updated_at = datetime.now(UTC)
        await self.db.commit()

    async def _unblock_dependent_tasks(self, task_id: int) -> None:
        """Unblock tasks that depend on this completed task."""
        stmt = select(Task).where(
            Task.depends_on.contains([task_id]),
            Task.status == TaskStatus.BLOCKED,
        )
        result = await self.db.execute(stmt)
        blocked_tasks = list(result.scalars().all())

        for blocked_task in blocked_tasks:
            if blocked_task.depends_on:
                stmt = select(Task).where(
                    Task.id.in_(blocked_task.depends_on),
                    Task.status != TaskStatus.COMPLETED,
                )
                result = await self.db.execute(stmt)
                incomplete_deps = list(result.scalars().all())

                if not incomplete_deps:
                    blocked_task.status = TaskStatus.PENDING
                    blocked_task.updated_at = datetime.now(UTC)

        if blocked_tasks:
            await self.db.commit()
