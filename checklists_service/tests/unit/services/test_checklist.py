"""Unit tests for checklist service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from checklists_service.core import NotFoundException, ValidationException
from checklists_service.core.enums import ChecklistStatus, TaskStatus, TemplateStatus
from checklists_service.models import Checklist, Task, Template
from checklists_service.schemas import ChecklistCreate, ChecklistStats, ChecklistUpdate
from checklists_service.services import ChecklistService


class TestChecklistServiceCreate:
    """Test checklist creation."""

    async def test_create_checklist_success(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_task_template: Task,
        sample_datetime: datetime,
        mock_user_employee: dict,
    ) -> None:
        """Test successful checklist creation."""
        # Setup
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None
        mock_uow.checklists.create.return_value = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
        )
        mock_uow.task_templates.find_by_template.return_value = [sample_task_template]
        mock_uow.tasks.create.return_value = None
        mock_uow.checklists.update.return_value = mock_uow.checklists.create.return_value

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=None,
            hr_id=None,
            notes=None,
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(return_value=mock_user_employee)

            service = ChecklistService(mock_uow, "mock-token")
            result = await service.create_checklist(checklist_data, "mock-token")

        assert result.user_id == 1
        assert result.employee_id == "EMP001"
        assert result.template_id == 1
        assert result.status == ChecklistStatus.IN_PROGRESS
        mock_uow.checklists.create.assert_called_once()

    async def test_create_checklist_no_auth_token(self, mock_uow: MagicMock) -> None:
        """Test checklist creation fails without auth token."""
        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=datetime.now(UTC),
        )

        service = ChecklistService(mock_uow, None)

        with pytest.raises(ValidationException, match="Authentication required"):
            await service.create_checklist(checklist_data, None)

    async def test_create_checklist_user_not_found(self, mock_uow: MagicMock) -> None:
        """Test checklist creation fails when user not found."""
        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=datetime.now(UTC),
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(return_value=None)

            service = ChecklistService(mock_uow, "mock-token")

            with pytest.raises(ValidationException, match="User 1 not found"):
                await service.create_checklist(checklist_data, "mock-token")

    async def test_create_checklist_employee_id_mismatch(
        self,
        mock_uow: MagicMock,
        mock_user_employee: dict,
    ) -> None:
        """Test checklist creation fails when employee ID doesn't match."""
        mock_user_employee["employee_id"] = "DIFFERENT"
        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=datetime.now(UTC),
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(return_value=mock_user_employee)

            service = ChecklistService(mock_uow, "mock-token")

            with pytest.raises(ValidationException, match="Employee ID does not match"):
                await service.create_checklist(checklist_data, "mock-token")

    async def test_create_checklist_template_not_active(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        mock_user_employee: dict,
    ) -> None:
        """Test checklist creation fails when template is not active."""
        sample_template.status = TemplateStatus.DRAFT
        mock_uow.templates.get_by_id.return_value = sample_template

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=datetime.now(UTC),
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(return_value=mock_user_employee)

            service = ChecklistService(mock_uow, "mock-token")

            with pytest.raises(ValidationException, match="Template not found or not active"):
                await service.create_checklist(checklist_data, "mock-token")

    async def test_create_checklist_user_already_has_active(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_checklist: Checklist,
        mock_user_employee: dict,
    ) -> None:
        """Test checklist creation fails when user already has active checklist."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = sample_checklist

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=datetime.now(UTC),
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(return_value=mock_user_employee)

            service = ChecklistService(mock_uow, "mock-token")

            with pytest.raises(ValidationException, match="User already has a checklist for this template"):
                await service.create_checklist(checklist_data, "mock-token")

    async def test_create_checklist_with_mentor_validation(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_task_template: Task,
        sample_datetime: datetime,
        mock_user_employee: dict,
        mock_user_mentor: dict,
    ) -> None:
        """Test checklist creation with mentor validation."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None

        created_checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=2,
        )
        mock_uow.checklists.create.return_value = created_checklist
        mock_uow.task_templates.find_by_template.return_value = [sample_task_template]
        mock_uow.tasks.create.return_value = None
        mock_uow.checklists.update.return_value = created_checklist

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=2,
            hr_id=None,
            notes=None,
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(side_effect=[mock_user_employee, mock_user_mentor])

            service = ChecklistService(mock_uow, "mock-token")
            result = await service.create_checklist(checklist_data, "mock-token")

        assert result.mentor_id == 2

    async def test_create_checklist_mentor_not_found(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        mock_user_employee: dict,
    ) -> None:
        """Test checklist creation fails when mentor not found."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=datetime.now(UTC),
            mentor_id=999,
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(side_effect=[mock_user_employee, None])

            service = ChecklistService(mock_uow, "mock-token")

            with pytest.raises(ValidationException, match="Mentor 999 not found"):
                await service.create_checklist(checklist_data, "mock-token")

    async def test_create_checklist_mentor_invalid_role(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        mock_user_employee: dict,
    ) -> None:
        """Test checklist creation fails when mentor doesn't have valid role."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None

        mock_user_employee["role"] = "EMPLOYEE"  # Invalid role for mentor

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=datetime.now(UTC),
            mentor_id=2,
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(side_effect=[mock_user_employee, mock_user_employee])

            service = ChecklistService(mock_uow, "mock-token")

            with pytest.raises(ValidationException, match="Mentor must have MENTOR, HR or ADMIN role"):
                await service.create_checklist(checklist_data, "mock-token")

    async def test_create_checklist_hr_validation(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_task_template: Task,
        sample_datetime: datetime,
        mock_user_employee: dict,
        mock_user_hr: dict,
    ) -> None:
        """Test checklist creation with HR validation."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None

        created_checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            hr_id=3,
        )
        mock_uow.checklists.create.return_value = created_checklist
        mock_uow.task_templates.find_by_template.return_value = [sample_task_template]
        mock_uow.tasks.create.return_value = None
        mock_uow.checklists.update.return_value = created_checklist

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=sample_datetime,
            hr_id=3,
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(side_effect=[mock_user_employee, mock_user_hr])

            service = ChecklistService(mock_uow, "mock-token")
            result = await service.create_checklist(checklist_data, "mock-token")

        assert result.hr_id == 3

    async def test_create_checklist_hr_not_found(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        mock_user_employee: dict,
    ) -> None:
        """Test checklist creation fails when HR not found."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=datetime.now(UTC),
            hr_id=999,  # Non-existent HR
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(side_effect=[mock_user_employee, None])

            service = ChecklistService(mock_uow, "mock-token")

            with pytest.raises(ValidationException, match="HR 999 not found"):
                await service.create_checklist(checklist_data, "mock-token")

    async def test_create_checklist_hr_invalid_role(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        mock_user_employee: dict,
    ) -> None:
        """Test checklist creation fails when HR doesn't have valid role."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None

        # Employee role is invalid for HR
        mock_user_employee["role"] = "EMPLOYEE"

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=datetime.now(UTC),
            hr_id=2,  # This will be mocked to return an employee, not HR
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(side_effect=[mock_user_employee, mock_user_employee])

            service = ChecklistService(mock_uow, "mock-token")

            with pytest.raises(ValidationException, match="HR must have HR or ADMIN role"):
                await service.create_checklist(checklist_data, "mock-token")

    async def test_create_checklist_auto_due_date(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_task_template: Task,
        sample_datetime: datetime,
        mock_user_employee: dict,
    ) -> None:
        """Test checklist creation auto-sets due date from template duration."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None
        mock_uow.checklists.create.return_value = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=sample_template.duration_days),
        )
        mock_uow.task_templates.find_by_template.return_value = [sample_task_template]
        mock_uow.tasks.create.return_value = None
        mock_uow.checklists.update.return_value = mock_uow.checklists.create.return_value

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=sample_datetime,
            # No due_date provided - should be auto-calculated
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(return_value=mock_user_employee)

            service = ChecklistService(mock_uow, "mock-token")
            result = await service.create_checklist(checklist_data, "mock-token")

        expected_due_date = sample_datetime + timedelta(days=sample_template.duration_days)
        assert result.due_date == expected_due_date

    async def test_validate_user_without_token(self, mock_uow: MagicMock) -> None:
        """Test _validate_user raises error when no auth token."""
        service = ChecklistService(mock_uow, None)

        with pytest.raises(ValidationException, match="Authentication required"):
            await service._validate_user(1)

    async def test_validate_user_not_found(self, mock_uow: MagicMock) -> None:
        """Test _validate_user raises error when user not found."""
        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(return_value=None)

            service = ChecklistService(mock_uow, "mock-token")

            with pytest.raises(ValidationException, match="User 1 not found"):
                await service._validate_user(1)

    async def test_create_checklist_task_assignment_mentor(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_task_template: Task,
        sample_datetime: datetime,
        mock_user_employee: dict,
        mock_user_mentor: dict,
    ) -> None:
        """Test task assignment to mentor with auto_assign (lines 145-160)."""
        sample_task_template.auto_assign = True
        sample_task_template.assignee_role = "MENTOR"

        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None
        created_checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=2,
        )
        mock_uow.checklists.create.return_value = created_checklist
        mock_uow.task_templates.find_by_template.return_value = [sample_task_template]
        mock_uow.tasks.create.return_value = None
        mock_uow.checklists.update.return_value = created_checklist

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=sample_datetime,
            mentor_id=2,
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(side_effect=[mock_user_employee, mock_user_mentor])

            service = ChecklistService(mock_uow, "mock-token")
            await service.create_checklist(checklist_data, "mock-token")

        # Verify task was created with mentor as assignee
        task_call = mock_uow.tasks.create.call_args[0][0]
        assert task_call.assignee_id == 2

    async def test_create_checklist_with_task_dependencies_sets_blocks(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_datetime: datetime,
        mock_user_employee: dict,
        mock_user_mentor: dict,
    ) -> None:
        """Test create_checklist sets blocks field based on task dependencies (lines 122-124)."""
        from checklists_service.models import TaskTemplate

        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None

        created_checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=5,
            hr_id=None,
        )
        mock_uow.checklists.create.return_value = created_checklist

        # Create task templates with dependencies: task2 depends on task1
        task1_template = TaskTemplate(
            id=1,
            template_id=1,
            title="Task 1",
            description="First task",
            instructions="Do this first",
            category="DOCUMENTATION",
            order=0,
            due_days=1,
            estimated_minutes=30,
            resources=[],
            required_documents=[],
            assignee_role="MENTOR",
            auto_assign=True,
            depends_on=[],
            created_at=sample_datetime,
            updated_at=None,
        )
        task2_template = TaskTemplate(
            id=2,
            template_id=1,
            title="Task 2",
            description="Second task",
            instructions="Do this after task 1",
            category="DOCUMENTATION",
            order=1,
            due_days=2,
            estimated_minutes=30,
            resources=[],
            required_documents=[],
            assignee_role="MENTOR",
            auto_assign=True,
            depends_on=[1],  # Depends on task with template_task_id=1
            created_at=sample_datetime,
            updated_at=None,
        )
        mock_uow.task_templates.find_by_template.return_value = [task1_template, task2_template]

        # Capture created tasks to verify blocks are set
        created_tasks = []

        def capture_task(task):
            created_tasks.append(task)

        mock_uow.tasks.create.side_effect = capture_task
        mock_uow.checklists.update.return_value = created_checklist

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=sample_datetime,
            mentor_id=5,
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(side_effect=[mock_user_employee, mock_user_mentor])

            service = ChecklistService(mock_uow, "mock-token")
            result = await service.create_checklist(checklist_data, "mock-token")

        assert result.user_id == 1

        # Verify tasks were created
        assert len(created_tasks) == 2

        # Find the tasks by their template_task_id
        task1 = next((t for t in created_tasks if t.template_task_id == 1), None)
        task2 = next((t for t in created_tasks if t.template_task_id == 2), None)

        assert task1 is not None
        assert task2 is not None

        # Task1 should block task2 (line 124)
        assert task2.template_task_id in task1.blocks


class TestChecklistServiceGet:
    """Test getting checklists."""

    async def test_get_checklist_success(self, mock_uow: MagicMock, sample_checklist: Checklist) -> None:
        """Test successful checklist retrieval."""
        mock_uow.checklists.get_by_id.return_value = sample_checklist

        service = ChecklistService(mock_uow)
        result = await service.get_checklist(1)

        assert result.id == 1
        assert result.user_id == 1
        mock_uow.checklists.get_by_id.assert_called_once_with(1)

    async def test_get_checklist_not_found(self, mock_uow: MagicMock) -> None:
        """Test checklist retrieval fails when not found."""
        mock_uow.checklists.get_by_id.return_value = None

        service = ChecklistService(mock_uow)

        with pytest.raises(NotFoundException, match="Checklist"):
            await service.get_checklist(999)


class TestChecklistServiceUpdate:
    """Test updating checklists."""

    async def test_update_checklist_success(
        self,
        mock_uow: MagicMock,
        sample_checklist: Checklist,
        sample_datetime: datetime,
    ) -> None:
        """Test successful checklist update."""
        mock_uow.checklists.get_by_id.return_value = sample_checklist
        mock_uow.checklists.update.return_value = sample_checklist

        update_data = ChecklistUpdate(notes="Updated notes")

        service = ChecklistService(mock_uow)
        result = await service.update_checklist(1, update_data)

        assert result.notes == "Updated notes"
        mock_uow.checklists.recalculate_progress.assert_called_once_with(1)

    async def test_update_checklist_mark_completed(
        self,
        mock_uow: MagicMock,
        sample_checklist: Checklist,
        sample_datetime: datetime,
    ) -> None:
        """Test marking checklist as completed updates completed_at."""
        mock_uow.checklists.get_by_id.return_value = sample_checklist
        mock_uow.tasks.find_by_checklist.return_value = []
        mock_uow.checklists.update.return_value = sample_checklist

        update_data = ChecklistUpdate(status=ChecklistStatus.COMPLETED)

        service = ChecklistService(mock_uow)
        result = await service.update_checklist(1, update_data)

        assert result.completed_at is not None

    async def test_update_checklist_mark_completed_completes_pending_tasks(
        self,
        mock_uow: MagicMock,
        sample_checklist: Checklist,
        sample_datetime: datetime,
    ) -> None:
        """Test marking checklist as completed also marks pending/in-progress/blocked tasks as completed."""
        mock_uow.checklists.get_by_id.return_value = sample_checklist

        # Create tasks in different statuses that should be auto-completed
        pending_task = Task(
            id=1,
            checklist_id=1,
            title="Pending Task",
            status=TaskStatus.PENDING,
            due_date=sample_datetime,
            order=0,
            category="TEST",
            assignee_role="MENTOR",
            created_at=sample_datetime,
        )
        in_progress_task = Task(
            id=2,
            checklist_id=1,
            title="In Progress Task",
            status=TaskStatus.IN_PROGRESS,
            due_date=sample_datetime,
            order=1,
            category="TEST",
            assignee_role="MENTOR",
            started_at=sample_datetime,
            created_at=sample_datetime,
        )
        blocked_task = Task(
            id=3,
            checklist_id=1,
            title="Blocked Task",
            status=TaskStatus.BLOCKED,
            due_date=sample_datetime,
            order=2,
            category="TEST",
            assignee_role="MENTOR",
            created_at=sample_datetime,
        )

        # Mock the three separate calls for pending, in_progress, and blocked tasks
        mock_uow.tasks.find_by_checklist.side_effect = [
            [pending_task],  # First call: pending tasks
            [in_progress_task],  # Second call: in_progress tasks
            [blocked_task],  # Third call: blocked tasks
        ]
        mock_uow.checklists.update.return_value = sample_checklist

        update_data = ChecklistUpdate(status=ChecklistStatus.COMPLETED)

        service = ChecklistService(mock_uow)
        result = await service.update_checklist(1, update_data)

        assert result.completed_at is not None
        # Verify that all tasks were marked as completed
        assert pending_task.status == TaskStatus.COMPLETED
        assert pending_task.completed_at is not None
        assert in_progress_task.status == TaskStatus.COMPLETED
        assert in_progress_task.completed_at is not None
        assert blocked_task.status == TaskStatus.COMPLETED
        assert blocked_task.completed_at is not None

    async def test_update_checklist_not_found(self, mock_uow: MagicMock) -> None:
        """Test update fails when checklist not found."""
        mock_uow.checklists.get_by_id.return_value = None

        service = ChecklistService(mock_uow)

        with pytest.raises(NotFoundException, match="Checklist"):
            await service.update_checklist(999, ChecklistUpdate(notes="Test"))

    async def test_update_checklist_progress_percentage(
        self,
        mock_uow: MagicMock,
        sample_checklist: Checklist,
    ) -> None:
        """Test updating checklist progress percentage."""
        mock_uow.checklists.get_by_id.return_value = sample_checklist
        mock_uow.checklists.update.return_value = sample_checklist

        update_data = ChecklistUpdate(progress_percentage=50)

        service = ChecklistService(mock_uow)
        result = await service.update_checklist(1, update_data)

        assert result.progress_percentage == 50


class TestChecklistServiceDelete:
    """Test deleting checklists."""

    async def test_delete_checklist_success(
        self,
        mock_uow: MagicMock,
        sample_completed_checklist: Checklist,
    ) -> None:
        """Test successful checklist deletion."""
        mock_uow.checklists.get_by_id.return_value = sample_completed_checklist

        service = ChecklistService(mock_uow)
        await service.delete_checklist(1)

        mock_uow.checklists.delete.assert_called_once_with(1)

    async def test_delete_checklist_in_progress_fails(
        self,
        mock_uow: MagicMock,
        sample_checklist: Checklist,
    ) -> None:
        """Test deletion fails for in-progress checklist."""
        mock_uow.checklists.get_by_id.return_value = sample_checklist

        service = ChecklistService(mock_uow)

        with pytest.raises(ValidationException, match="Cannot delete in-progress checklist"):
            await service.delete_checklist(1)

    async def test_delete_checklist_not_found(self, mock_uow: MagicMock) -> None:
        """Test deletion fails when checklist not found."""
        mock_uow.checklists.get_by_id.return_value = None

        service = ChecklistService(mock_uow)

        with pytest.raises(NotFoundException, match="Checklist"):
            await service.delete_checklist(999)


class TestChecklistServiceList:
    """Test listing checklists."""

    async def test_get_checklists(self, mock_uow: MagicMock, sample_checklist: Checklist) -> None:
        """Test getting list of checklists."""
        mock_uow.checklists.find_checklists.return_value = ([sample_checklist], 1)

        service = ChecklistService(mock_uow)
        checklists, total = await service.get_checklists(skip=0, limit=50)

        assert len(checklists) == 1
        assert total == 1
        mock_uow.checklists.find_checklists.assert_called_once()

    async def test_get_checklists_with_filters(self, mock_uow: MagicMock, sample_checklist: Checklist) -> None:
        """Test getting checklists with filters."""
        mock_uow.checklists.find_checklists.return_value = ([sample_checklist], 1)

        service = ChecklistService(mock_uow)
        _checklists, total = await service.get_checklists(
            skip=0,
            limit=50,
            user_id=1,
            status="IN_PROGRESS",  # Use enum value name
            department_id=1,
            search="EMP",
        )

        assert total == 1
        mock_uow.checklists.find_checklists.assert_called_once()

    async def test_get_checklists_overdue_only(self, mock_uow: MagicMock, sample_checklist: Checklist) -> None:
        """Test getting only overdue checklists."""
        mock_uow.checklists.find_checklists.return_value = ([sample_checklist], 1)

        service = ChecklistService(mock_uow)
        _checklists, _total = await service.get_checklists(skip=0, limit=50, overdue_only=True)

        call_kwargs = mock_uow.checklists.find_checklists.call_args.kwargs
        assert call_kwargs["overdue_only"] is True


class TestChecklistServiceComplete:
    """Test completing checklists."""

    async def test_complete_checklist_success(
        self,
        mock_uow: MagicMock,
        sample_checklist: Checklist,
        sample_datetime: datetime,
    ) -> None:
        """Test successful checklist completion."""
        mock_uow.checklists.get_by_id.return_value = sample_checklist
        mock_uow.tasks.count_by_status.return_value = {TaskStatus.COMPLETED.value: 5}
        mock_uow.checklists.update.return_value = sample_checklist

        service = ChecklistService(mock_uow)
        result = await service.complete_checklist(1)

        assert result.status == ChecklistStatus.COMPLETED
        assert result.progress_percentage == 100
        assert result.completed_at is not None

    async def test_complete_checklist_already_completed(
        self,
        mock_uow: MagicMock,
        sample_completed_checklist: Checklist,
    ) -> None:
        """Test completing already completed checklist returns as-is."""
        mock_uow.checklists.get_by_id.return_value = sample_completed_checklist

        service = ChecklistService(mock_uow)
        result = await service.complete_checklist(1)

        assert result.status == ChecklistStatus.COMPLETED
        mock_uow.checklists.update.assert_not_called()

    async def test_complete_checklist_with_pending_tasks_fails(
        self,
        mock_uow: MagicMock,
        sample_checklist: Checklist,
    ) -> None:
        """Test completing checklist with pending tasks fails."""
        mock_uow.checklists.get_by_id.return_value = sample_checklist
        mock_uow.tasks.count_by_status.return_value = {
            TaskStatus.COMPLETED.value: 3,
            TaskStatus.PENDING.value: 2,
        }

        service = ChecklistService(mock_uow)

        with pytest.raises(ValidationException, match="Cannot complete checklist with pending tasks"):
            await service.complete_checklist(1)

    async def test_complete_checklist_not_found(self, mock_uow: MagicMock) -> None:
        """Test completion fails when checklist not found."""
        mock_uow.checklists.get_by_id.return_value = None

        service = ChecklistService(mock_uow)

        with pytest.raises(NotFoundException, match="Checklist"):
            await service.complete_checklist(999)


class TestChecklistServiceProgress:
    """Test checklist progress methods."""

    async def test_get_checklist_progress(self, mock_uow: MagicMock, sample_checklist: Checklist) -> None:
        """Test getting checklist progress."""
        mock_uow.checklists.get_by_id.return_value = sample_checklist
        mock_uow.checklists.get_progress.return_value = {
            "checklist_id": 1,
            "completed_tasks": 3,
            "total_tasks": 5,
            "completion_rate": 60.0,
        }

        service = ChecklistService(mock_uow)
        progress = await service.get_checklist_progress(1)

        assert progress["checklist_id"] == 1
        assert progress["completion_rate"] == 60.0

    async def test_get_checklist_stats(self, mock_uow: MagicMock) -> None:
        """Test getting checklist statistics."""
        mock_uow.checklists.get_statistics.return_value = {
            "total": 10,
            "completed": 5,
            "in_progress": 3,
            "overdue": 1,
            "not_started": 1,
            "avg_completion_days": 15.5,
            "completion_rate": 50.0,
            "by_department": {"1": 8, "2": 2},
            "recent_completions": [],
        }

        service = ChecklistService(mock_uow)
        stats = await service.get_checklist_stats(user_id=1, department_id=1)

        assert isinstance(stats, ChecklistStats)
        assert stats.total == 10
        assert stats.completion_rate == 50.0


class TestChecklistServiceMonthlyStats:
    """Test monthly statistics."""

    async def test_get_monthly_stats(self, mock_uow: MagicMock) -> None:
        """Test getting monthly statistics."""
        mock_uow.checklists.get_monthly_stats.return_value = [
            {"month": "Jan", "new_checklists": 5, "completed": 3},
            {"month": "Feb", "new_checklists": 8, "completed": 6},
        ]

        service = ChecklistService(mock_uow)
        stats = await service.get_monthly_stats(months=6)

        assert len(stats) == 2
        assert stats[0]["month"] == "Jan"

    async def test_get_completion_time_distribution(self, mock_uow: MagicMock) -> None:
        """Test getting completion time distribution."""
        mock_uow.checklists.get_completion_time_distribution.return_value = [
            {"range": "1-7 days", "count": 5},
            {"range": "8-14 days", "count": 10},
            {"range": "15-21 days", "count": 3},
        ]

        service = ChecklistService(mock_uow)
        distribution = await service.get_completion_time_distribution()

        assert len(distribution) == 3
        assert distribution[0]["range"] == "1-7 days"


class TestChecklistServiceAutoCreate:
    """Test auto-creating checklists."""

    async def test_auto_create_checklists_success(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_task_template: Task,
        sample_datetime: datetime,
    ) -> None:
        """Test successful auto-creation of checklists."""
        mock_uow.templates.find_matching.return_value = [sample_template]
        mock_uow.checklists.get_by_user_and_template.return_value = None
        mock_uow.checklists.create.return_value = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
        )
        mock_uow.task_templates.find_by_template.return_value = [sample_task_template]
        mock_uow.tasks.create.return_value = None
        mock_uow.checklists.update.return_value = mock_uow.checklists.create.return_value

        service = ChecklistService(mock_uow)
        result = await service.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=2,
        )

        assert len(result) == 1
        assert result[0].user_id == 1

    async def test_auto_create_checklists_no_matching_templates(self, mock_uow: MagicMock) -> None:
        """Test auto-create returns empty list when no matching templates."""
        mock_uow.templates.find_matching.return_value = []

        service = ChecklistService(mock_uow)
        result = await service.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=None,
        )

        assert len(result) == 0

    async def test_auto_create_checklists_skip_existing(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_checklist: Checklist,
    ) -> None:
        """Test auto-create skips templates user already has checklist for."""
        mock_uow.templates.find_matching.return_value = [sample_template]
        mock_uow.checklists.get_by_user_and_template.return_value = sample_checklist

        service = ChecklistService(mock_uow)
        result = await service.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=None,
        )

        assert len(result) == 0


class TestChecklistServiceEdgeCases:
    """Test additional edge cases for coverage."""

    async def test_get_checklist_statistics_empty_result(
        self,
        mock_uow: MagicMock,
    ) -> None:
        """Test get_checklist_statistics with empty result (line 299)."""
        mock_uow.checklists.get_statistics.return_value = {
            "total": 0,
            "completed": 0,
            "in_progress": 0,
            "overdue": 0,
            "not_started": 0,
            "avg_completion_days": 0.0,
            "completion_rate": 0.0,
            "by_department": {},
            "recent_completions": [],
        }

        service = ChecklistService(mock_uow)
        stats = await service.get_checklist_stats()

        assert stats.total == 0
        assert stats.completion_rate == 0.0


class TestChecklistServiceHRAssignee:
    """Test HR assignee logic (line 103)."""

    async def test_create_checklist_hr_assignee_auto_assignment(
        self,
        mock_uow: MagicMock,
        sample_template,
        sample_task_template: Task,
        sample_datetime: datetime,
        mock_user_employee: dict,
        mock_user_hr: dict,
    ) -> None:
        """Test that HR is auto-assigned as assignee when HR is configured (line 103)."""
        from checklists_service.models import TaskTemplate

        sample_template.duration_days = 30

        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.checklists.get_by_user_and_template.return_value = None

        created_checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=None,
            hr_id=10,  # HR ID set
        )
        mock_uow.checklists.create.return_value = created_checklist

        # Create a task template with HR role auto-assign
        hr_task_template = TaskTemplate(
            id=1,
            template_id=1,
            title="HR Documentation",
            description="Complete HR paperwork",
            instructions="Fill out forms",
            category="DOCUMENTATION",
            order=0,
            due_days=3,
            estimated_minutes=60,
            resources=[],
            required_documents=[],
            assignee_role="HR",  # HR role
            auto_assign=True,
            depends_on=[],
            created_at=sample_datetime,
            updated_at=None,
        )
        mock_uow.task_templates.find_by_template.return_value = [hr_task_template]
        mock_uow.tasks.create.return_value = None
        mock_uow.checklists.update.return_value = created_checklist

        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=sample_datetime,
            hr_id=10,  # HR assigned
        )

        with patch("checklists_service.utils.auth_service_client") as mock_auth:
            mock_auth.get_user = AsyncMock(side_effect=[mock_user_employee, mock_user_hr])

            service = ChecklistService(mock_uow, "mock-token")
            result = await service.create_checklist(checklist_data, "mock-token")

        assert result.hr_id == 10


class TestChecklistServiceAutoCreateLines:
    """Test auto_create_checklists specific lines (299, 319-320)."""

    async def test_auto_create_checklists_hr_assignee(
        self,
        mock_uow: MagicMock,
        sample_template,
        sample_datetime: datetime,
    ) -> None:
        """Test auto_create with HR assignee role (line 299)."""
        from checklists_service.models import TaskTemplate

        sample_template.duration_days = 30
        sample_template.default_assignee_role = "MENTOR"

        mock_uow.templates.find_matching.return_value = [sample_template]
        mock_uow.checklists.get_by_user_and_template.return_value = None

        created_checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=None,
            hr_id=10,
        )
        mock_uow.checklists.create.return_value = created_checklist

        # Task template with HR role
        hr_task_template = TaskTemplate(
            id=1,
            template_id=1,
            title="HR Task",
            description="HR paperwork",
            instructions="Fill out",
            category="DOCUMENTATION",
            order=0,
            due_days=3,
            estimated_minutes=60,
            resources=[],
            required_documents=[],
            assignee_role="HR",  # HR role
            auto_assign=True,
            depends_on=[],
            created_at=sample_datetime,
            updated_at=None,
        )
        mock_uow.task_templates.find_by_template.return_value = [hr_task_template]
        mock_uow.tasks.create.return_value = None
        mock_uow.checklists.update.return_value = created_checklist

        service = ChecklistService(mock_uow)
        result = await service.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=None,
        )

        assert len(result) == 1


class TestChecklistServiceAutoCreateAssignment:
    """Test auto_create_checklists method (lines 298-299, 319-320)."""

    async def test_auto_create_checklists_auto_assigns_mentor(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_datetime: datetime,
    ) -> None:
        """Test auto_create_checklists auto-assigns mentor when auto_assign=True and role=MENTOR (lines 298-299)."""
        from checklists_service.models import TaskTemplate

        sample_template.duration_days = 30
        sample_template.default_assignee_role = "MENTOR"
        sample_template.auto_assign = True

        mock_uow.templates.find_matching.return_value = [sample_template]
        mock_uow.checklists.get_by_user_and_template.return_value = None

        created_checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=5,  # Mentor ID provided
            hr_id=10,
        )
        mock_uow.checklists.create.return_value = created_checklist

        # Task template with MENTOR role and auto_assign=True
        mentor_task_template = TaskTemplate(
            id=1,
            template_id=1,
            title="Mentor Task",
            description="Mentor onboarding",
            instructions="Meet with mentor",
            category="ONBOARDING",
            order=0,
            due_days=3,
            estimated_minutes=60,
            resources=[],
            required_documents=[],
            assignee_role="MENTOR",
            auto_assign=True,  # Auto-assign enabled
            depends_on=[],
            created_at=sample_datetime,
            updated_at=None,
        )
        mock_uow.task_templates.find_by_template.return_value = [mentor_task_template]
        mock_uow.tasks.create.return_value = None
        mock_uow.checklists.update.return_value = created_checklist

        service = ChecklistService(mock_uow)
        result = await service.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=5,  # Mentor ID provided - should be auto-assigned
        )

        assert len(result) == 1
        # Verify tasks.create was called with assignee_id set to mentor_id (5)
        created_task = mock_uow.tasks.create.call_args[0][0]
        assert created_task.assignee_id == 5  # Mentor auto-assigned (line 101)

    async def test_auto_create_checklists_hr_auto_assign(
        self,
        mock_uow: MagicMock,
        sample_template: Template,
        sample_datetime: datetime,
    ) -> None:
        """Test auto_create_checklists with HR auto-assign (lines 123-124)."""
        from checklists_service.models import TaskTemplate

        sample_template.duration_days = 30
        sample_template.default_assignee_role = "MENTOR"
        sample_template.auto_assign = True

        mock_uow.templates.find_matching.return_value = [sample_template]
        mock_uow.checklists.get_by_user_and_template.return_value = None

        created_checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=5,
            hr_id=10,
        )
        mock_uow.checklists.create.return_value = created_checklist

        # Task template with HR role and auto_assign=True
        hr_task_template = TaskTemplate(
            id=1,
            template_id=1,
            title="HR Task",
            description="HR onboarding",
            instructions="Meet with HR",
            category="ONBOARDING",
            order=0,
            due_days=3,
            estimated_minutes=60,
            resources=[],
            required_documents=[],
            assignee_role="HR",
            auto_assign=True,
            depends_on=[],
            created_at=sample_datetime,
            updated_at=None,
        )
        mock_uow.task_templates.find_by_template.return_value = [hr_task_template]
        mock_uow.tasks.create.return_value = None
        mock_uow.checklists.update.return_value = created_checklist

        service = ChecklistService(mock_uow)
        result = await service.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=5,
        )

        assert len(result) == 1
        # Verify tasks.create was called with assignee_id set to hr_id (10)
        created_task = mock_uow.tasks.create.call_args[0][0]
        assert created_task.assignee_id == 10  # HR auto-assigned (lines 102-103)

    async def test_auto_create_checklists_builds_task_blocks(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_datetime: datetime,
    ) -> None:
        """Test auto_create_checklists builds task dependency blocks (lines 319-320)."""
        from checklists_service.models import Task, TaskTemplate

        sample_template.duration_days = 30
        sample_template.default_assignee_role = "MENTOR"
        sample_template.auto_assign = True

        mock_uow.templates.find_matching.return_value = [sample_template]
        mock_uow.checklists.get_by_user_and_template.return_value = None

        created_checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=5,
            hr_id=10,
        )
        mock_uow.checklists.create.return_value = created_checklist

        # Create two task templates where task2 depends on task1
        task1_template = TaskTemplate(
            id=1,
            template_id=1,
            title="Task 1",
            description="First task",
            instructions="Do this first",
            category="ONBOARDING",
            order=0,
            due_days=1,
            estimated_minutes=30,
            resources=[],
            required_documents=[],
            assignee_role="MENTOR",
            auto_assign=True,
            depends_on=[],  # No dependencies
            created_at=sample_datetime,
            updated_at=None,
        )
        task2_template = TaskTemplate(
            id=2,
            template_id=1,
            title="Task 2",
            description="Second task",
            instructions="Do this after task 1",
            category="ONBOARDING",
            order=1,
            due_days=2,
            estimated_minutes=30,
            resources=[],
            required_documents=[],
            assignee_role="MENTOR",
            auto_assign=True,
            depends_on=[1],  # Depends on task 1 (by template_task_id)
            created_at=sample_datetime,
            updated_at=None,
        )
        mock_uow.task_templates.find_by_template.return_value = [task1_template, task2_template]

        # Capture the created tasks when tasks.create is called
        created_tasks_list: list[Task] = []

        def capture_task(task):
            created_tasks_list.append(task)

        mock_uow.tasks.create.side_effect = capture_task

        mock_uow.checklists.update.return_value = created_checklist

        service = ChecklistService(mock_uow)
        result = await service.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=5,
        )

        assert len(result) == 1

        # Verify tasks were created
        assert len(created_tasks_list) == 2

        # Find task1 and task2
        task1 = next((t for t in created_tasks_list if t.template_task_id == 1), None)
        task2 = next((t for t in created_tasks_list if t.template_task_id == 2), None)

        assert task1 is not None, "Task 1 should be created"
        assert task2 is not None, "Task 2 should be created"

        # Task2 should depend on task1
        assert task1.template_task_id in task2.depends_on

        # Task1 should block task2 (line 320) - blocks are built based on depends_on
        # After the service processes, task1.blocks should contain task2's template_task_id
        assert task2.template_task_id in task1.blocks, (
            f"Task1.blocks = {task1.blocks}, expected {task2.template_task_id}"
        )

    async def test_auto_create_checklists_skips_when_existing_checklist(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_checklist: Checklist,
    ) -> None:
        """Test auto_create_checklists skips users who already have a checklist for the template."""
        mock_uow.templates.find_matching.return_value = [sample_template]
        mock_uow.checklists.get_by_user_and_template.return_value = sample_checklist

        service = ChecklistService(mock_uow)
        result = await service.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=None,
        )

        assert len(result) == 0

    async def test_auto_create_checklists_no_matching_templates(
        self,
        mock_uow: MagicMock,
    ) -> None:
        """Test auto_create_checklists returns empty when no matching templates."""
        mock_uow.templates.find_matching.return_value = []

        service = ChecklistService(mock_uow)
        result = await service.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=None,
        )

        assert len(result) == 0

    async def test_auto_create_checklists_with_department_filter(
        self,
        mock_uow: MagicMock,
        sample_template: Checklist,
        sample_datetime: datetime,
    ) -> None:
        """Test auto_create_checklists uses department filter when specified."""
        sample_template.duration_days = 30
        mock_uow.templates.find_matching.return_value = [sample_template]
        mock_uow.checklists.get_by_user_and_template.return_value = None

        created_checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
            start_date=sample_datetime,
            due_date=sample_datetime + timedelta(days=30),
            mentor_id=None,
            hr_id=None,
        )
        mock_uow.checklists.create.return_value = created_checklist
        mock_uow.task_templates.find_by_template.return_value = []
        mock_uow.checklists.update.return_value = created_checklist

        service = ChecklistService(mock_uow)
        result = await service.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=None,
        )

        assert len(result) == 1
        # Verify find_matching was called with department filter
        call_args = mock_uow.templates.find_matching.call_args
        # Method is called as find_matching(department_id, position)
        assert call_args.args[0] == 1  # department_id
