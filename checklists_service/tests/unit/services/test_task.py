"""Unit tests for task service."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from checklists_service.core import NotFoundException, ValidationException
from checklists_service.core.enums import TaskStatus
from checklists_service.models import Task  # noqa: TC001
from checklists_service.schemas import TaskBulkUpdate, TaskProgress, TaskUpdate
from checklists_service.services import TaskService

if TYPE_CHECKING:
    from datetime import datetime


class TestTaskServiceGet:
    """Test task retrieval methods."""

    async def test_get_task_success(self, mock_uow: MagicMock, sample_task: Task) -> None:
        """Test successful task retrieval."""
        mock_uow.tasks.get_by_id.return_value = sample_task

        service = TaskService(mock_uow)
        result = await service.get_task(1)

        assert result.id == 1
        assert result.title == "Complete Documentation"
        mock_uow.tasks.get_by_id.assert_called_once_with(1)

    async def test_get_task_not_found(self, mock_uow: MagicMock) -> None:
        """Test task retrieval fails when not found."""
        mock_uow.tasks.get_by_id.return_value = None

        service = TaskService(mock_uow)

        with pytest.raises(NotFoundException, match="Task"):
            await service.get_task(999)


class TestTaskServiceGetChecklistTasks:
    """Test getting tasks for a checklist."""

    async def test_get_checklist_tasks(self, mock_uow: MagicMock, sample_task: Task) -> None:
        """Test getting tasks for a checklist."""
        mock_uow.tasks.find_by_checklist.return_value = [sample_task]

        service = TaskService(mock_uow)
        tasks = await service.get_checklist_tasks(checklist_id=1)

        assert len(tasks) == 1
        assert tasks[0].checklist_id == 1

    async def test_get_checklist_tasks_with_status_filter(
        self, mock_uow: MagicMock, sample_task: Task
    ) -> None:
        """Test getting tasks filtered by status."""
        mock_uow.tasks.find_by_checklist.return_value = [sample_task]

        service = TaskService(mock_uow)
        tasks = await service.get_checklist_tasks(checklist_id=1, status="pending")

        assert len(tasks) == 1
        call_kwargs = mock_uow.tasks.find_by_checklist.call_args.kwargs
        assert call_kwargs["status"] == "pending"

    async def test_get_checklist_tasks_with_category_filter(
        self, mock_uow: MagicMock, sample_task: Task
    ) -> None:
        """Test getting tasks filtered by category."""
        mock_uow.tasks.find_by_checklist.return_value = [sample_task]

        service = TaskService(mock_uow)
        tasks = await service.get_checklist_tasks(checklist_id=1, category="DOCUMENTATION")

        assert len(tasks) == 1
        call_kwargs = mock_uow.tasks.find_by_checklist.call_args.kwargs
        assert call_kwargs["category"] == "DOCUMENTATION"

    async def test_get_checklist_tasks_overdue_only(
        self, mock_uow: MagicMock, sample_task: Task
    ) -> None:
        """Test getting only overdue tasks."""
        mock_uow.tasks.find_by_checklist.return_value = [sample_task]

        service = TaskService(mock_uow)
        await service.get_checklist_tasks(checklist_id=1, overdue_only=True)

        call_kwargs = mock_uow.tasks.find_by_checklist.call_args.kwargs
        assert call_kwargs["overdue_only"] is True


class TestTaskServiceGetAssignedTasks:
    """Test getting assigned tasks."""

    async def test_get_assigned_tasks(self, mock_uow: MagicMock, sample_task: Task) -> None:
        """Test getting tasks assigned to user."""
        mock_uow.tasks.find_assigned.return_value = ([sample_task], 1)

        service = TaskService(mock_uow)
        tasks, total = await service.get_assigned_tasks(assignee_id=2)

        assert len(tasks) == 1
        assert total == 1

    async def test_get_assigned_tasks_with_pagination(self, mock_uow: MagicMock, sample_task: Task) -> None:
        """Test getting assigned tasks with pagination."""
        mock_uow.tasks.find_assigned.return_value = ([sample_task], 10)

        service = TaskService(mock_uow)
        tasks, total = await service.get_assigned_tasks(assignee_id=2, skip=10, limit=5)

        assert len(tasks) == 1
        assert total == 10
        mock_uow.tasks.find_assigned.assert_called_once()


class TestTaskServiceUpdate:
    """Test task updates."""

    async def test_update_task_success(self, mock_uow: MagicMock, sample_task: Task) -> None:
        """Test successful task update."""
        mock_uow.tasks.get_by_id.return_value = sample_task
        mock_uow.tasks.update.return_value = sample_task

        update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS, assignee_id=3)

        service = TaskService(mock_uow)
        result = await service.update_task(1, update_data)

        assert result.status == TaskStatus.IN_PROGRESS
        assert result.assignee_id == 3
        mock_uow.checklists.recalculate_progress.assert_called_once_with(1)

    async def test_update_task_invalid_status_transition(
        self, mock_uow: MagicMock, sample_completed_task: Task
    ) -> None:
        """Test invalid status transition fails."""
        mock_uow.tasks.get_by_id.return_value = sample_completed_task

        # Cannot go from COMPLETED to PENDING
        update_data = TaskUpdate(status=TaskStatus.PENDING)

        service = TaskService(mock_uow)

        with pytest.raises(ValidationException, match="Invalid status transition"):
            await service.update_task(1, update_data)

    async def test_update_task_to_completed_with_incomplete_deps_fails(
        self, mock_uow: MagicMock, sample_in_progress_task: Task, sample_task: Task
    ) -> None:
        """Test completing task with incomplete dependencies fails."""
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = [sample_task]

        update_data = TaskUpdate(status=TaskStatus.COMPLETED)

        service = TaskService(mock_uow)

        with pytest.raises(ValidationException, match="Dependencies not completed"):
            await service.update_task(1, update_data)

    async def test_update_task_to_completed_sets_completed_at(
        self, mock_uow: MagicMock, sample_in_progress_task: Task
    ) -> None:
        """Test marking task completed sets completed_at timestamp."""
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = []
        mock_uow.tasks.update.return_value = sample_in_progress_task

        update_data = TaskUpdate(status=TaskStatus.COMPLETED)

        service = TaskService(mock_uow)
        result = await service.update_task(1, update_data)

        assert result.completed_at is not None

    async def test_update_task_to_in_progress_sets_started_at(
        self, mock_uow: MagicMock, sample_pending_task: Task
    ) -> None:
        """Test marking task in_progress sets started_at timestamp."""
        sample_pending_task.started_at = None
        mock_uow.tasks.get_by_id.return_value = sample_pending_task
        mock_uow.tasks.update.return_value = sample_pending_task

        update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)

        service = TaskService(mock_uow)
        result = await service.update_task(1, update_data)

        assert result.started_at is not None

    async def test_update_task_progress_with_notes_appends(
        self, mock_uow: MagicMock, sample_in_progress_task: Task
    ) -> None:
        """Test update_task_progress appends notes to existing notes."""
        sample_in_progress_task.completion_notes = "Previous notes"
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = []
        mock_uow.tasks.update.return_value = sample_in_progress_task

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.IN_PROGRESS,
            progress_percentage=50,
            notes="New notes",
        )

        service = TaskService(mock_uow)
        result = await service.update_task_progress(1, progress_data)

        assert "Previous notes" in str(result.completion_notes)
        assert "New notes" in str(result.completion_notes)

    async def test_update_task_progress_with_notes_sets_new(
        self, mock_uow: MagicMock, sample_in_progress_task: Task
    ) -> None:
        """Test update_task_progress sets notes when none exist."""
        sample_in_progress_task.completion_notes = None
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = []
        mock_uow.tasks.update.return_value = sample_in_progress_task

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.IN_PROGRESS,
            progress_percentage=50,
            notes="First notes",
        )

        service = TaskService(mock_uow)
        result = await service.update_task_progress(1, progress_data)

        assert result.completion_notes == "First notes"

    async def test_update_task_progress_with_attachments(
        self, mock_uow: MagicMock, sample_in_progress_task: Task
    ) -> None:
        """Test update_task_progress extends attachments."""
        sample_in_progress_task.attachments = []
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = []
        mock_uow.tasks.update.return_value = sample_in_progress_task

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.IN_PROGRESS,
            progress_percentage=50,
            attachments=[{"filename": "file1.pdf"}, {"filename": "file2.pdf"}],
        )

        service = TaskService(mock_uow)
        result = await service.update_task_progress(1, progress_data)

        assert len(result.attachments) == 2

    async def test_update_task_progress_complete_with_incomplete_deps(
        self, mock_uow: MagicMock, sample_in_progress_task: Task, sample_task: Task
    ) -> None:
        """Test update_task_progress completion fails with incomplete deps."""
        sample_in_progress_task.status = TaskStatus.IN_PROGRESS
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = [sample_task]

        progress_data = TaskProgress(
            task_id=1, status=TaskStatus.COMPLETED, progress_percentage=100
        )

        service = TaskService(mock_uow)

        with pytest.raises(ValidationException, match="Dependencies not completed"):
            await service.update_task_progress(1, progress_data)

    async def test_update_task_to_in_progress_sets_started_at(
        self, mock_uow: MagicMock, sample_task: Task
    ) -> None:
        """Test marking task in-progress sets started_at timestamp."""
        mock_uow.tasks.get_by_id.return_value = sample_task
        mock_uow.tasks.update.return_value = sample_task

        update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)

        service = TaskService(mock_uow)
        result = await service.update_task(1, update_data)

        assert result.started_at is not None


class TestTaskServiceUpdateProgress:
    """Test task progress updates."""

    async def test_update_task_progress_success(
        self, mock_uow: MagicMock, sample_in_progress_task: Task
    ) -> None:
        """Test successful progress update."""
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.update.return_value = sample_in_progress_task

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.IN_PROGRESS,
            progress_percentage=50,
            notes="Halfway done",
            attachments=[],
        )

        service = TaskService(mock_uow)
        result = await service.update_task_progress(1, progress_data)

        assert result.status == TaskStatus.IN_PROGRESS
        assert "Halfway done" in str(result.completion_notes)

    async def test_update_task_progress_appends_notes(
        self, mock_uow: MagicMock, sample_completed_task: Task
    ) -> None:
        """Test progress notes are appended to existing notes."""
        sample_completed_task.completion_notes = "Previous notes"
        mock_uow.tasks.get_by_id.return_value = sample_completed_task
        mock_uow.tasks.update.return_value = sample_completed_task

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.COMPLETED,
            progress_percentage=100,
            notes="New update",
        )

        service = TaskService(mock_uow)
        result = await service.update_task_progress(1, progress_data)

        assert "Previous notes" in str(result.completion_notes)
        assert "New update" in str(result.completion_notes)

    async def test_update_task_progress_adds_attachments(
        self, mock_uow: MagicMock, sample_in_progress_task: Task
    ) -> None:
        """Test progress update adds attachments."""
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.update.return_value = sample_in_progress_task

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.IN_PROGRESS,
            progress_percentage=50,
            attachments=[{"filename": "doc.pdf"}],
        )

        service = TaskService(mock_uow)
        result = await service.update_task_progress(1, progress_data)

        assert len(result.attachments) > 0

    async def test_update_task_progress_complete_with_incomplete_deps_fails(
        self, mock_uow: MagicMock, sample_in_progress_task: Task, sample_task: Task
    ) -> None:
        """Test completing task via progress update with incomplete dependencies fails (lines 107-113)."""
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = [sample_task]

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.COMPLETED,
            progress_percentage=100,
        )

        service = TaskService(mock_uow)

        with pytest.raises(ValidationException, match="Dependencies not completed"):
            await service.update_task_progress(1, progress_data)

    async def test_update_task_progress_complete_sets_completed_at(
        self, mock_uow: MagicMock, sample_in_progress_task: Task
    ) -> None:
        """Test marking task completed via progress update sets completed_at (lines 107-108)."""
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = []
        mock_uow.tasks.update.return_value = sample_in_progress_task

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.COMPLETED,
            progress_percentage=100,
        )

        service = TaskService(mock_uow)
        result = await service.update_task_progress(1, progress_data)

        assert result.completed_at is not None


class TestTaskServiceComplete:
    """Test completing tasks."""

    async def test_complete_task_success(
        self, mock_uow: MagicMock, sample_in_progress_task: Task, sample_datetime: datetime  # noqa: ARG002
    ) -> None:
        """Test successful task completion."""
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = []
        mock_uow.tasks.update.return_value = sample_in_progress_task

        service = TaskService(mock_uow)
        result = await service.complete_task(1, completed_by=1, notes="Done!")

        assert result.status == TaskStatus.COMPLETED
        assert result.completed_by == 1
        assert result.completed_at is not None
        assert "Done!" in str(result.completion_notes)
        mock_uow.checklists.recalculate_progress.assert_called_once_with(1)

    async def test_complete_task_already_completed(
        self, mock_uow: MagicMock, sample_completed_task: Task
    ) -> None:
        """Test completing already completed task returns as-is."""
        mock_uow.tasks.get_by_id.return_value = sample_completed_task

        service = TaskService(mock_uow)
        result = await service.complete_task(1, completed_by=1)

        assert result.status == TaskStatus.COMPLETED
        mock_uow.tasks.update.assert_not_called()

    async def test_complete_task_with_incomplete_deps_fails(
        self, mock_uow: MagicMock, sample_in_progress_task: Task, sample_task: Task
    ) -> None:
        """Test completing task with incomplete dependencies fails."""
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = [sample_task]

        service = TaskService(mock_uow)

        with pytest.raises(ValidationException, match="Dependencies not completed"):
            await service.complete_task(1, completed_by=1)

    async def test_complete_task_unblocks_dependent_tasks(
        self, mock_uow: MagicMock, sample_in_progress_task: Task, sample_blocked_task: Task
    ) -> None:
        """Test completing task unblocks dependent tasks."""
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = []
        mock_uow.tasks.get_blocked_by.return_value = [sample_blocked_task]
        mock_uow.tasks.get_incomplete_dependencies.side_effect = [[], []]  # First for task, second for blocked
        mock_uow.tasks.update.return_value = sample_in_progress_task

        service = TaskService(mock_uow)
        result = await service.complete_task(1, completed_by=1)

        assert result.status == TaskStatus.COMPLETED
        # Verify that _unblock_dependent_tasks was called
        mock_uow.tasks.get_blocked_by.assert_called_once_with(1)

    async def test_complete_task_appends_notes_when_existing(
        self, mock_uow: MagicMock, sample_in_progress_task: Task
    ) -> None:
        """Test that completing task appends notes when completion_notes already exists (line 141)."""
        sample_in_progress_task.completion_notes = "Previous notes"
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_incomplete_dependencies.return_value = []
        mock_uow.tasks.update.return_value = sample_in_progress_task

        service = TaskService(mock_uow)
        result = await service.complete_task(1, completed_by=1, notes="New completion note")

        assert result.status == TaskStatus.COMPLETED
        assert "Previous notes" in str(result.completion_notes)
        assert "New completion note" in str(result.completion_notes)




class TestTaskServiceBulkUpdate:
    """Test bulk task updates."""

    async def test_bulk_update_tasks_success(
        self, mock_uow: MagicMock, sample_task: Task, sample_in_progress_task: Task
    ) -> None:
        """Test successful bulk update."""
        mock_uow.tasks.find_by_ids.return_value = [sample_task, sample_in_progress_task]
        mock_uow.tasks.update.return_value = None

        bulk_data = TaskBulkUpdate(
            task_ids=[1, 2],
            status=TaskStatus.IN_PROGRESS,
            assignee_id=5,
        )

        service = TaskService(mock_uow)
        await service.bulk_update_tasks(bulk_data)

        assert mock_uow.tasks.update.call_count == 2
        mock_uow.checklists.recalculate_progress.assert_called()

    async def test_bulk_update_tasks_empty_list(self, mock_uow: MagicMock) -> None:
        """Test bulk update with empty list returns immediately."""
        bulk_data = TaskBulkUpdate(task_ids=[], status=TaskStatus.IN_PROGRESS)

        service = TaskService(mock_uow)
        await service.bulk_update_tasks(bulk_data)

        mock_uow.tasks.find_by_ids.assert_not_called()

    async def test_bulk_update_tasks_missing_tasks_fails(
        self, mock_uow: MagicMock, sample_task: Task
    ) -> None:
        """Test bulk update fails when some tasks not found."""
        mock_uow.tasks.find_by_ids.return_value = [sample_task]  # Only 1 found, but 2 requested

        bulk_data = TaskBulkUpdate(task_ids=[1, 999], status=TaskStatus.IN_PROGRESS)

        service = TaskService(mock_uow)

        with pytest.raises(ValidationException, match="Some tasks not found"):
            await service.bulk_update_tasks(bulk_data)


class TestTaskServiceDependencies:
    """Test task dependency methods."""

    async def test_get_task_dependencies(self, mock_uow: MagicMock, sample_in_progress_task: Task) -> None:
        """Test getting task dependencies."""
        mock_uow.tasks.get_by_id.return_value = sample_in_progress_task
        mock_uow.tasks.get_dependencies.return_value = {
            "task_id": 1,
            "dependencies": [{"id": 1, "status": "COMPLETED"}],
            "blocked_tasks": [{"id": 3, "status": "BLOCKED"}],
            "can_complete": True,
        }

        service = TaskService(mock_uow)
        deps = await service.get_task_dependencies(1)

        assert deps["task_id"] == 1
        assert deps["can_complete"] is True


class TestTaskServiceStatusTransitions:
    """Test valid status transitions."""

    async def test_valid_transitions(self, mock_uow: MagicMock) -> None:
        """Test all valid status transitions."""
        service = TaskService(mock_uow)

        # PENDING can go to: IN_PROGRESS, BLOCKED, CANCELLED
        assert service._is_valid_status_transition(TaskStatus.PENDING, TaskStatus.IN_PROGRESS) is True
        assert service._is_valid_status_transition(TaskStatus.PENDING, TaskStatus.BLOCKED) is True
        assert service._is_valid_status_transition(TaskStatus.PENDING, TaskStatus.CANCELLED) is True

        # IN_PROGRESS can go to: COMPLETED, BLOCKED, CANCELLED
        assert service._is_valid_status_transition(TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED) is True
        assert service._is_valid_status_transition(TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED) is True
        assert service._is_valid_status_transition(TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED) is True

        # BLOCKED can go to: PENDING, IN_PROGRESS, CANCELLED
        assert service._is_valid_status_transition(TaskStatus.BLOCKED, TaskStatus.PENDING) is True
        assert service._is_valid_status_transition(TaskStatus.BLOCKED, TaskStatus.IN_PROGRESS) is True
        assert service._is_valid_status_transition(TaskStatus.BLOCKED, TaskStatus.CANCELLED) is True

        # CANCELLED can go to: PENDING
        assert service._is_valid_status_transition(TaskStatus.CANCELLED, TaskStatus.PENDING) is True

    async def test_invalid_transitions(self, mock_uow: MagicMock) -> None:
        """Test invalid status transitions."""
        service = TaskService(mock_uow)

        # COMPLETED cannot transition to anything
        assert service._is_valid_status_transition(TaskStatus.COMPLETED, TaskStatus.PENDING) is False
        assert service._is_valid_status_transition(TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS) is False

        # PENDING cannot go directly to COMPLETED
        assert service._is_valid_status_transition(TaskStatus.PENDING, TaskStatus.COMPLETED) is False

        # CANCELLED cannot go to IN_PROGRESS or COMPLETED directly
        assert service._is_valid_status_transition(TaskStatus.CANCELLED, TaskStatus.IN_PROGRESS) is False
        assert service._is_valid_status_transition(TaskStatus.CANCELLED, TaskStatus.COMPLETED) is False


class TestTaskServiceAttachments:
    """Test task attachment methods."""

    async def test_add_attachment_success(self, mock_uow: MagicMock, sample_task: Task) -> None:
        """Test successful attachment addition."""
        mock_uow.tasks.get_by_id.return_value = sample_task
        mock_uow.tasks.update.return_value = sample_task

        service = TaskService(mock_uow)
        attachment = await service.add_attachment(
            task_id=1,
            filename="document.pdf",
            file_size=1024,
            mime_type="application/pdf",
            description="Important document",
            uploaded_by=1,
        )

        assert attachment["filename"] == "document.pdf"
        assert attachment["file_size"] == 1024
        assert attachment["uploaded_by"] == 1

    async def test_add_attachment_multiple(self, mock_uow: MagicMock, sample_task: Task) -> None:
        """Test adding multiple attachments."""
        sample_task.attachments = [{"id": 1, "filename": "existing.pdf"}]
        mock_uow.tasks.get_by_id.return_value = sample_task
        mock_uow.tasks.update.return_value = sample_task

        service = TaskService(mock_uow)
        attachment = await service.add_attachment(
            task_id=1,
            filename="new.pdf",
            file_size=2048,
            mime_type="application/pdf",
            description=None,
            uploaded_by=1,
        )

        assert attachment["id"] == 2  # Should increment ID
        assert attachment["filename"] == "new.pdf"
        assert len(sample_task.attachments) == 2

    async def test_get_attachments(self, mock_uow: MagicMock, sample_task: Task) -> None:
        """Test getting all attachments for a task."""
        sample_task.attachments = [
            {"id": 1, "filename": "doc1.pdf", "uploaded_by": 1},
            {"id": 2, "filename": "doc2.pdf", "uploaded_by": 2},
        ]
        mock_uow.tasks.get_by_id.return_value = sample_task

        service = TaskService(mock_uow)
        attachments = await service.get_attachments(1)

        assert len(attachments) == 2

    async def test_add_attachment_no_description(self, mock_uow: MagicMock, sample_task: Task) -> None:
        """Test adding attachment without description."""
        mock_uow.tasks.get_by_id.return_value = sample_task
        mock_uow.tasks.update.return_value = sample_task

        service = TaskService(mock_uow)
        attachment = await service.add_attachment(
            task_id=1,
            filename="document.pdf",
            file_size=1024,
            mime_type="application/pdf",
            description=None,
            uploaded_by=1,
        )

        assert attachment["filename"] == "document.pdf"
        assert attachment["description"] is None
        assert attachment["mime_type"] == "application/pdf"
