"""Unit tests for audit API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from checklists_service.api.deps import UserInfo
from checklists_service.api.endpoints.audit import (
    ChecklistStatusEntry,
    TaskCompletionEntry,
    TemplateChangeEntry,
)
from checklists_service.api.endpoints import audit


@pytest.fixture
def sample_hr_user():
    """Create sample HR user."""
    return UserInfo({
        "id": 10, "email": "hr@example.com", "role": "HR",
        "is_active": True, "employee_id": "HR001"
    })


@pytest.fixture
def sample_admin_user():
    """Create sample admin user."""
    return UserInfo({
        "id": 11, "email": "admin@example.com", "role": "ADMIN",
        "is_active": True, "employee_id": "ADM001"
    })


@pytest.fixture
def sample_employee_user():
    """Create sample employee user."""
    return UserInfo({
        "id": 1, "email": "employee@example.com", "role": "EMPLOYEE",
        "is_active": True, "employee_id": "EMP001"
    })


class TestRequireHrOrAdmin:
    """Test require_hr_or_admin function."""

    async def test_require_hr_or_admin_with_hr_role(self, sample_hr_user) -> None:
        """Test HR role passes validation."""
        # Should not raise any exception
        audit.require_hr_or_admin(sample_hr_user)

    async def test_require_hr_or_admin_with_admin_role(self, sample_admin_user) -> None:
        """Test Admin role passes validation."""
        # Should not raise any exception
        audit.require_hr_or_admin(sample_admin_user)

    async def test_require_hr_or_admin_with_employee_role(self, sample_employee_user) -> None:
        """Test Employee role raises PermissionError."""
        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            audit.require_hr_or_admin(sample_employee_user)


class TestGetChecklistStatusHistory:
    """Test GET /checklist-status-history endpoint."""

    async def test_get_checklist_status_history_with_checklist_id(self, sample_hr_user) -> None:
        """Test getting checklist status history filtered by checklist_id."""
        uow = MagicMock()
        now = datetime.now(UTC)

        mock_history = ChecklistStatusEntry(
            id=1,
            checklist_id=1,
            user_id=1,
            action="status_changed",
            old_status="IN_PROGRESS",
            new_status="COMPLETED",
            changed_at=now,
            changed_by=10,
            metadata={"reason": "onboarding complete"},
        )
        uow.checklist_status_history.get_by_checklist_id = AsyncMock(return_value=[mock_history])
        uow.checklist_status_history.get_by_user_id = AsyncMock(return_value=[])

        result = await audit.get_checklist_status_history(
            current_user=sample_hr_user,
            uow=uow,
            checklist_id=1,
            user_id=None,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].checklist_id == 1
        uow.checklist_status_history.get_by_checklist_id.assert_awaited_once()

    async def test_get_checklist_status_history_with_user_id(self, sample_hr_user) -> None:
        """Test getting checklist status history filtered by user_id."""
        uow = MagicMock()
        now = datetime.now(UTC)

        mock_history = ChecklistStatusEntry(
            id=1,
            checklist_id=1,
            user_id=1,
            action="status_changed",
            old_status="IN_PROGRESS",
            new_status="COMPLETED",
            changed_at=now,
            changed_by=10,
            metadata=None,
        )
        uow.checklist_status_history.get_by_user_id = AsyncMock(return_value=[mock_history])
        uow.checklist_status_history.get_by_checklist_id = AsyncMock(return_value=[])

        result = await audit.get_checklist_status_history(
            current_user=sample_hr_user,
            uow=uow,
            checklist_id=None,
            user_id=1,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].user_id == 1
        uow.checklist_status_history.get_by_user_id.assert_awaited_once()

    async def test_get_checklist_status_history_with_date_range(self, sample_hr_user) -> None:
        """Test getting checklist status history with date range."""
        uow = MagicMock()
        uow.checklist_status_history.get_all = AsyncMock(return_value=([], 0))
        uow.checklist_status_history.get_by_checklist_id = AsyncMock(return_value=[])
        uow.checklist_status_history.get_by_user_id = AsyncMock(return_value=[])

        result = await audit.get_checklist_status_history(
            current_user=sample_hr_user,
            uow=uow,
            checklist_id=None,
            user_id=None,
            from_date=datetime(2024, 1, 1, tzinfo=UTC),
            to_date=datetime(2024, 12, 31, tzinfo=UTC),
            limit=10,
            offset=0,
        )

        assert result.total == 0
        assert len(result.items) == 0
        uow.checklist_status_history.get_all.assert_awaited_once()

    async def test_get_checklist_status_history_default_pagination(self, sample_hr_user) -> None:
        """Test getting checklist status history with default pagination."""
        uow = MagicMock()
        uow.checklist_status_history.get_all = AsyncMock(return_value=([], 0))
        uow.checklist_status_history.get_by_checklist_id = AsyncMock(return_value=[])
        uow.checklist_status_history.get_by_user_id = AsyncMock(return_value=[])

        result = await audit.get_checklist_status_history(
            current_user=sample_hr_user,
            uow=uow,
            checklist_id=None,
            user_id=None,
            from_date=None,
            to_date=None,
        )

        assert result.total == 0
        uow.checklist_status_history.get_all.assert_awaited_once()

    async def test_get_checklist_status_history_permission_denied(self, sample_employee_user) -> None:
        """Test permission denied for non-HR/Admin user."""
        uow = MagicMock()

        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            await audit.get_checklist_status_history(
                current_user=sample_employee_user,
                uow=uow,
            )


class TestGetTaskCompletionHistory:
    """Test GET /task-completion-history endpoint."""

    async def test_get_task_completion_history_with_task_id(self, sample_hr_user) -> None:
        """Test getting task completion history filtered by task_id."""
        uow = MagicMock()
        now = datetime.now(UTC)

        mock_history = TaskCompletionEntry(
            id=1,
            task_id=1,
            checklist_id=1,
            user_id=1,
            completed_at=now,
            completion_notes="Task completed successfully",
            attachments={"file": "document.pdf"},
            completed_by=1,
        )
        uow.task_completion_history.get_by_task_id = AsyncMock(return_value=[mock_history])
        uow.task_completion_history.get_by_checklist_id = AsyncMock(return_value=[])
        uow.task_completion_history.get_by_user_id = AsyncMock(return_value=[])

        result = await audit.get_task_completion_history(
            current_user=sample_hr_user,
            uow=uow,
            task_id=1,
            checklist_id=None,
            user_id=None,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].task_id == 1
        uow.task_completion_history.get_by_task_id.assert_awaited_once()

    async def test_get_task_completion_history_with_checklist_id(self, sample_hr_user) -> None:
        """Test getting task completion history filtered by checklist_id."""
        uow = MagicMock()
        now = datetime.now(UTC)

        mock_history = TaskCompletionEntry(
            id=1,
            task_id=1,
            checklist_id=1,
            user_id=1,
            completed_at=now,
            completion_notes=None,
            attachments=None,
            completed_by=1,
        )
        uow.task_completion_history.get_by_checklist_id = AsyncMock(return_value=[mock_history])
        uow.task_completion_history.get_by_task_id = AsyncMock(return_value=[])
        uow.task_completion_history.get_by_user_id = AsyncMock(return_value=[])

        result = await audit.get_task_completion_history(
            current_user=sample_hr_user,
            uow=uow,
            checklist_id=1,
            task_id=None,
            user_id=None,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].checklist_id == 1
        uow.task_completion_history.get_by_checklist_id.assert_awaited_once()

    async def test_get_task_completion_history_with_user_id(self, sample_hr_user) -> None:
        """Test getting task completion history filtered by user_id."""
        uow = MagicMock()
        now = datetime.now(UTC)

        mock_history = TaskCompletionEntry(
            id=1,
            task_id=1,
            checklist_id=1,
            user_id=1,
            completed_at=now,
            completion_notes=None,
            attachments=None,
            completed_by=1,
        )
        uow.task_completion_history.get_by_user_id = AsyncMock(return_value=[mock_history])
        uow.task_completion_history.get_by_task_id = AsyncMock(return_value=[])
        uow.task_completion_history.get_by_checklist_id = AsyncMock(return_value=[])

        result = await audit.get_task_completion_history(
            current_user=sample_hr_user,
            uow=uow,
            user_id=1,
            task_id=None,
            checklist_id=None,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].user_id == 1
        uow.task_completion_history.get_by_user_id.assert_awaited_once()

    async def test_get_task_completion_history_with_pagination(self, sample_hr_user) -> None:
        """Test getting task completion history with custom pagination."""
        uow = MagicMock()
        uow.task_completion_history.get_all = AsyncMock(return_value=([], 0))
        uow.task_completion_history.get_by_task_id = AsyncMock(return_value=[])
        uow.task_completion_history.get_by_checklist_id = AsyncMock(return_value=[])
        uow.task_completion_history.get_by_user_id = AsyncMock(return_value=[])

        result = await audit.get_task_completion_history(
            current_user=sample_hr_user,
            uow=uow,
            task_id=None,
            checklist_id=None,
            user_id=None,
            limit=25,
            offset=10,
        )

        assert result.total == 0
        uow.task_completion_history.get_all.assert_awaited_once()

    async def test_get_task_completion_history_permission_denied(self, sample_employee_user) -> None:
        """Test permission denied for non-HR/Admin user."""
        uow = MagicMock()

        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            await audit.get_task_completion_history(
                current_user=sample_employee_user,
                uow=uow,
            )


class TestGetTemplateChangeHistory:
    """Test GET /template-change-history endpoint."""

    async def test_get_template_change_history_with_template_id(self, sample_hr_user) -> None:
        """Test getting template change history filtered by template_id."""
        uow = MagicMock()
        now = datetime.now(UTC)

        mock_history = TemplateChangeEntry(
            id=1,
            template_id=1,
            action="updated",
            old_name="Old Name",
            new_name="New Name",
            changed_at=now,
            changed_by=10,
            change_summary="Updated description",
        )
        uow.template_change_history.get_by_template_id = AsyncMock(return_value=[mock_history])

        result = await audit.get_template_change_history(
            current_user=sample_hr_user,
            uow=uow,
            template_id=1,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].template_id == 1
        uow.template_change_history.get_by_template_id.assert_awaited_once()

    async def test_get_template_change_history_all_templates(self, sample_hr_user) -> None:
        """Test getting template change history for all templates."""
        uow = MagicMock()
        uow.template_change_history.get_all = AsyncMock(return_value=([], 0))
        uow.template_change_history.get_by_template_id = AsyncMock(return_value=[])

        result = await audit.get_template_change_history(
            current_user=sample_hr_user,
            uow=uow,
            template_id=None,
        )

        assert result.total == 0
        uow.template_change_history.get_all.assert_awaited_once()

    async def test_get_template_change_history_with_date_range(self, sample_hr_user) -> None:
        """Test getting template change history with date range."""
        uow = MagicMock()
        uow.template_change_history.get_all = AsyncMock(return_value=([], 0))
        uow.template_change_history.get_by_template_id = AsyncMock(return_value=[])

        result = await audit.get_template_change_history(
            current_user=sample_hr_user,
            uow=uow,
            template_id=None,
            from_date=datetime(2024, 1, 1, tzinfo=UTC),
            to_date=datetime(2024, 12, 31, tzinfo=UTC),
        )

        assert result.total == 0
        uow.template_change_history.get_all.assert_awaited_once()

    async def test_get_template_change_history_custom_pagination(self, sample_hr_user) -> None:
        """Test getting template change history with custom pagination."""
        uow = MagicMock()
        uow.template_change_history.get_all = AsyncMock(return_value=([], 0))
        uow.template_change_history.get_by_template_id = AsyncMock(return_value=[])

        result = await audit.get_template_change_history(
            current_user=sample_hr_user,
            uow=uow,
            template_id=None,
            limit=100,
            offset=50,
        )

        assert result.total == 0
        uow.template_change_history.get_all.assert_awaited_once()

    async def test_get_template_change_history_permission_denied(self, sample_employee_user) -> None:
        """Test permission denied for non-HR/Admin user."""
        uow = MagicMock()

        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            await audit.get_template_change_history(
                current_user=sample_employee_user,
                uow=uow,
            )
