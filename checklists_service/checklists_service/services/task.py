"""Task management service with repository pattern."""

from datetime import UTC, datetime
from typing import Any

from loguru import logger
from sqlalchemy.orm.attributes import flag_modified

from checklists_service.core import NotFoundException, TaskStatus, ValidationException
from checklists_service.models import Task
from checklists_service.repositories.unit_of_work import IUnitOfWork
from checklists_service.schemas import TaskBulkUpdate, TaskProgress, TaskUpdate


class TaskService:
    """Service for task management operations with repository pattern."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize task service with Unit of Work."""
        self._uow = uow

    async def get_task(self, task_id: int) -> Task:
        """Get task by ID."""
        task = await self._uow.tasks.get_by_id(task_id)
        if not task:
            logger.warning("Task not found (task_id={})", task_id)
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
        tasks = await self._uow.tasks.find_by_checklist(
            checklist_id=checklist_id,
            status=status,
            category=category,
            overdue_only=overdue_only,
        )
        return list(tasks)

    async def get_assigned_tasks(
        self,
        assignee_id: int,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> tuple[list[Task], int]:
        """Get tasks assigned to a user."""
        tasks, total = await self._uow.tasks.find_assigned(
            assignee_id=assignee_id,
            skip=skip,
            limit=limit,
            status=status,
        )
        return list(tasks), total

    async def update_task(self, task_id: int, update_data: TaskUpdate) -> Task:
        """Update task."""
        logger.debug("Updating task (task_id={})", task_id)
        task = await self.get_task(task_id)

        if update_data.status and not self._is_valid_status_transition(task.status, update_data.status):
            logger.warning(
                "Invalid task status transition (task_id={}, from={}, to={})",
                task_id,
                task.status,
                update_data.status,
            )
            msg = f"Invalid status transition from {task.status} to {update_data.status}"
            raise ValidationException(msg)

        if update_data.status == TaskStatus.COMPLETED and task.status != TaskStatus.COMPLETED:
            if not update_data.completed_at:
                update_data.completed_at = datetime.now(UTC)

            incomplete_deps = list(await self._uow.tasks.get_incomplete_dependencies(task_id))
            if incomplete_deps:
                dep_titles = [t.title for t in incomplete_deps]
                logger.warning(
                    "Task complete blocked by deps (task_id={}, deps={})",
                    task_id,
                    [d.id for d in incomplete_deps],
                )
                msg = f"Cannot complete task. Dependencies not completed: {', '.join(dep_titles)}"
                raise ValidationException(msg)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)

        if update_data.status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.now(UTC)

        task.updated_at = datetime.now(UTC)
        task = await self._uow.tasks.update(task)

        await self._uow.checklists.recalculate_progress(task.checklist_id)

        logger.info(
            "Task updated (task_id={}, status={})", task.id, task.status
        )
        return task

    async def update_task_progress(self, task_id: int, progress_data: TaskProgress) -> Task:
        """Update task progress."""
        logger.debug(
            "Updating task progress (task_id={}, new_status={})",
            task_id,
            progress_data.status,
        )
        task = await self.get_task(task_id)

        old_status = task.status
        task.status = progress_data.status

        if progress_data.notes:
            if task.completion_notes:
                task.completion_notes += f"\n\n{progress_data.notes}"
            else:
                task.completion_notes = progress_data.notes

        if progress_data.attachments:
            task.attachments.extend(progress_data.attachments)

        if progress_data.status == TaskStatus.COMPLETED and old_status != TaskStatus.COMPLETED:
            task.completed_at = datetime.now(UTC)

            incomplete_deps = list(await self._uow.tasks.get_incomplete_dependencies(task_id))
            if incomplete_deps:
                dep_titles = [t.title for t in incomplete_deps]
                logger.warning(
                    "Task progress complete blocked by deps (task_id={}, deps={})",
                    task_id,
                    [d.id for d in incomplete_deps],
                )
                msg = f"Cannot complete task. Dependencies not completed: {', '.join(dep_titles)}"
                raise ValidationException(msg)

        task.updated_at = datetime.now(UTC)
        task = await self._uow.tasks.update(task)

        await self._uow.checklists.recalculate_progress(task.checklist_id)

        logger.info(
            "Task progress updated (task_id={}, status={})", task.id, task.status
        )
        return task

    async def complete_task(self, task_id: int, completed_by: int, notes: str | None = None) -> Task:
        """Mark task as completed."""
        logger.debug(
            "Completing task (task_id={}, completed_by={})", task_id, completed_by
        )
        task = await self.get_task(task_id)

        if task.status == TaskStatus.COMPLETED:
            logger.debug("complete_task: already completed (task_id={})", task_id)
            return task

        incomplete_deps = list(await self._uow.tasks.get_incomplete_dependencies(task_id))
        if incomplete_deps:
            dep_titles = [t.title for t in incomplete_deps]
            logger.warning(
                "complete_task blocked by deps (task_id={}, deps={})",
                task_id,
                [d.id for d in incomplete_deps],
            )
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
        task = await self._uow.tasks.update(task)

        await self._uow.checklists.recalculate_progress(task.checklist_id)

        await self._unblock_dependent_tasks(task_id)

        logger.info(
            "Task completed (task_id={}, completed_by={})", task.id, completed_by
        )
        return task

    async def bulk_update_tasks(self, bulk_data: TaskBulkUpdate) -> None:
        """Bulk update tasks."""
        if not bulk_data.task_ids:
            logger.debug("bulk_update_tasks called with empty task_ids")
            return

        logger.info(
            "Bulk update tasks (count={}, task_ids={})",
            len(bulk_data.task_ids),
            bulk_data.task_ids,
        )
        tasks = list(await self._uow.tasks.find_by_ids(bulk_data.task_ids))

        if len(tasks) != len(bulk_data.task_ids):
            logger.warning(
                "Bulk update: some tasks missing (requested={}, found={})",
                len(bulk_data.task_ids),
                len(tasks),
            )
            msg = "Some tasks not found"
            raise ValidationException(msg)

        for task in tasks:
            update_data = bulk_data.model_dump(exclude_unset=True, exclude={"task_ids"})
            for field, value in update_data.items():
                setattr(task, field, value)
            task.updated_at = datetime.now(UTC)
            await self._uow.tasks.update(task)

        checklist_ids = {task.checklist_id for task in tasks}
        for checklist_id in checklist_ids:
            await self._uow.checklists.recalculate_progress(checklist_id)

    async def get_task_dependencies(self, task_id: int) -> dict[str, Any]:
        """Get task dependencies and blockers."""
        await self.get_task(task_id)
        return await self._uow.tasks.get_dependencies(task_id)

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

    async def _unblock_dependent_tasks(self, task_id: int) -> None:
        """Unblock tasks that depend on this completed task."""
        blocked_tasks = list(await self._uow.tasks.get_blocked_by(task_id))

        for blocked_task in blocked_tasks:
            incomplete_deps = list(await self._uow.tasks.get_incomplete_dependencies(blocked_task.id))

            if not incomplete_deps:
                blocked_task.status = TaskStatus.PENDING
                blocked_task.updated_at = datetime.now(UTC)
                await self._uow.tasks.update(blocked_task)
                logger.info(
                    "Task unblocked (task_id={}, unblocked_by_task_id={})",
                    blocked_task.id,
                    task_id,
                )

    async def add_attachment(
        self,
        task_id: int,
        filename: str,
        file_size: int,
        mime_type: str,
        description: str | None,
        uploaded_by: int,
    ) -> dict:
        """Add an attachment to a task."""
        logger.debug(
            "Adding attachment to task (task_id={}, filename={}, size={}, mime={})",
            task_id,
            filename,
            file_size,
            mime_type,
        )
        task = await self.get_task(task_id)

        attachment = {
            "id": len(task.attachments) + 1,
            "filename": filename,
            "file_size": file_size,
            "mime_type": mime_type,
            "description": description,
            "uploaded_at": datetime.now(UTC).isoformat(),
            "uploaded_by": uploaded_by,
        }

        # Create new list to trigger SQLAlchemy change detection
        task.attachments = task.attachments + [attachment]
        flag_modified(task, "attachments")

        task.updated_at = datetime.now(UTC)
        await self._uow.tasks.update(task)

        logger.info(
            "Attachment added (task_id={}, filename={}, uploaded_by={})",
            task_id,
            filename,
            uploaded_by,
        )
        return attachment

    async def get_attachments(self, task_id: int) -> list[dict]:
        """Get all attachments for a task."""
        task = await self.get_task(task_id)
        return task.attachments
