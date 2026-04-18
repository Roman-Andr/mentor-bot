"""Unit tests for checklists API endpoints."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from checklists_service.api.deps import UserInfo
from checklists_service.api.endpoints import checklists
from checklists_service.core import NotFoundException, PermissionDenied, ValidationException
from checklists_service.core.enums import ChecklistStatus
from checklists_service.schemas import (
    AutoCreateChecklistsRequest,
    ChecklistCreate,
    ChecklistStats,
    ChecklistUpdate,
)


@pytest.fixture
def sample_checklist_dict():
    """Create sample checklist dict."""
    now = datetime.now(UTC)
    return {
        "id": 1,
        "user_id": 1,
        "employee_id": "EMP001",
        "template_id": 1,
        "status": ChecklistStatus.IN_PROGRESS,
        "progress_percentage": 0,
        "completed_tasks": 0,
        "total_tasks": 5,
        "start_date": now,
        "due_date": now + timedelta(days=30),
        "completed_at": None,
        "mentor_id": 2,
        "hr_id": 3,
        "notes": "Test checklist",
        "created_at": now,
        "updated_at": None,
    }


@pytest.fixture
def sample_user():
    """Create sample user."""
    return UserInfo({
        "id": 1, "email": "test@example.com", "role": "EMPLOYEE",
        "is_active": True, "employee_id": "EMP001"
    })


@pytest.fixture
def sample_hr_user():
    """Create sample HR user."""
    return UserInfo({
        "id": 10, "email": "hr@example.com", "role": "HR",
        "is_active": True, "employee_id": "HR001"
    })


class TestGetChecklists:
    """Test GET /checklists endpoint."""

    async def test_get_checklists_as_employee(self, sample_user) -> None:
        """Test employee can see their own checklists."""
        uow = MagicMock()
        now = datetime.now(UTC)

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.user_id = 1
        checklist_mock.employee_id = "EMP001"
        checklist_mock.template_id = 1
        checklist_mock.status = ChecklistStatus.IN_PROGRESS
        checklist_mock.progress_percentage = 0
        checklist_mock.completed_tasks = 0
        checklist_mock.total_tasks = 5
        checklist_mock.start_date = now
        checklist_mock.due_date = now + timedelta(days=30)
        checklist_mock.completed_at = None
        checklist_mock.mentor_id = 2
        checklist_mock.hr_id = 3
        checklist_mock.notes = "Test checklist"
        checklist_mock.created_at = now
        checklist_mock.updated_at = None

        # Use actual ChecklistStats object, not MagicMock
        stats = ChecklistStats(
            total=1, completed=0, in_progress=1, overdue=0, not_started=0,
            avg_completion_days=0.0, completion_rate=0.0, by_department={}, recent_completions=[]
        )

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklists = AsyncMock(return_value=([checklist_mock], 1))
            instance.get_checklist_stats = AsyncMock(return_value=stats)

            result = await checklists.get_checklists(
                uow=uow,
                current_user=sample_user,
                skip=0,
                limit=50,
                user_id=None,
                status=None,
                department_id=None,
                search=None,
                overdue_only=False,
            )

            assert result.total == 1
            assert len(result.checklists) == 1
            assert result.checklists[0].user_id == 1

    async def test_get_checklists_as_hr(self, sample_hr_user) -> None:
        """Test HR can see all checklists."""
        uow = MagicMock()
        now = datetime.now(UTC)

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.user_id = 1
        checklist_mock.employee_id = "EMP001"
        checklist_mock.template_id = 1
        checklist_mock.status = ChecklistStatus.IN_PROGRESS
        checklist_mock.progress_percentage = 0
        checklist_mock.completed_tasks = 0
        checklist_mock.total_tasks = 5
        checklist_mock.start_date = now
        checklist_mock.due_date = now + timedelta(days=30)
        checklist_mock.completed_at = None
        checklist_mock.mentor_id = 2
        checklist_mock.hr_id = 3
        checklist_mock.notes = "Test checklist"
        checklist_mock.created_at = now
        checklist_mock.updated_at = None

        # Use actual ChecklistStats object
        stats = ChecklistStats(
            total=1, completed=0, in_progress=1, overdue=0, not_started=0,
            avg_completion_days=0.0, completion_rate=0.0, by_department={}, recent_completions=[]
        )

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklists = AsyncMock(return_value=([checklist_mock], 1))
            instance.get_checklist_stats = AsyncMock(return_value=stats)

            result = await checklists.get_checklists(
                uow=uow,
                current_user=sample_hr_user,
                skip=0,
                limit=50,
            )

            assert result.total == 1


class TestCreateChecklist:
    """Test POST /checklists endpoint."""

    async def test_create_checklist_success(self, sample_hr_user) -> None:
        """Test successful checklist creation."""
        uow = MagicMock()
        now = datetime.now(UTC)
        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=now,
            due_date=now + timedelta(days=30),
            mentor_id=2,
            hr_id=3,
            notes="Test checklist",
        )

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.user_id = 1
        checklist_mock.employee_id = "EMP001"
        checklist_mock.template_id = 1
        checklist_mock.status = ChecklistStatus.IN_PROGRESS
        checklist_mock.progress_percentage = 0
        checklist_mock.completed_tasks = 0
        checklist_mock.total_tasks = 5
        checklist_mock.start_date = now
        checklist_mock.due_date = now + timedelta(days=30)
        checklist_mock.completed_at = None
        checklist_mock.mentor_id = 2
        checklist_mock.hr_id = 3
        checklist_mock.notes = "Test checklist"
        checklist_mock.created_at = now
        checklist_mock.updated_at = None

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.create_checklist = AsyncMock(return_value=checklist_mock)

            result = await checklists.create_checklist(
                checklist_data=checklist_data,
                uow=uow,
                _current_user=sample_hr_user,
                auth_token="mock-token",  # noqa: S106
            )

            assert result.id == 1
            assert result.user_id == 1


class TestGetChecklist:
    """Test GET /checklists/{id} endpoint."""

    async def test_get_checklist_success(self, sample_user) -> None:
        """Test successful checklist retrieval."""
        uow = MagicMock()
        now = datetime.now(UTC)

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.user_id = 1
        checklist_mock.employee_id = "EMP001"
        checklist_mock.template_id = 1
        checklist_mock.status = ChecklistStatus.IN_PROGRESS
        checklist_mock.progress_percentage = 0
        checklist_mock.completed_tasks = 0
        checklist_mock.total_tasks = 5
        checklist_mock.start_date = now
        checklist_mock.due_date = now + timedelta(days=30)
        checklist_mock.completed_at = None
        checklist_mock.mentor_id = 2
        checklist_mock.hr_id = 3
        checklist_mock.notes = "Test checklist"
        checklist_mock.created_at = now
        checklist_mock.updated_at = None

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(return_value=checklist_mock)

            result = await checklists.get_checklist(
                checklist_id=1,
                uow=uow,
                current_user=sample_user,
            )

            assert result.id == 1
            assert result.user_id == 1

    async def test_get_checklist_not_found(self, sample_user) -> None:
        """Test getting non-existent checklist raises 404."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(side_effect=NotFoundException("Checklist"))

            with pytest.raises(HTTPException) as exc_info:
                await checklists.get_checklist(
                    checklist_id=999,
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404


class TestUpdateChecklist:
    """Test PUT /checklists/{id} endpoint."""

    async def test_update_checklist_success(self, sample_user) -> None:
        """Test successful checklist update."""
        uow = MagicMock()
        now = datetime.now(UTC)

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.user_id = 1
        checklist_mock.employee_id = "EMP001"
        checklist_mock.template_id = 1
        checklist_mock.status = ChecklistStatus.IN_PROGRESS
        checklist_mock.progress_percentage = 0
        checklist_mock.completed_tasks = 0
        checklist_mock.total_tasks = 5
        checklist_mock.start_date = now
        checklist_mock.due_date = now + timedelta(days=30)
        checklist_mock.completed_at = None
        checklist_mock.mentor_id = 2
        checklist_mock.hr_id = 3
        checklist_mock.notes = "Updated notes"
        checklist_mock.created_at = now
        checklist_mock.updated_at = now

        update_data = ChecklistUpdate(notes="Updated notes")

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(return_value=checklist_mock)
            instance.update_checklist = AsyncMock(return_value=checklist_mock)

            result = await checklists.update_checklist(
                checklist_id=1,
                checklist_data=update_data,
                uow=uow,
                current_user=sample_user,
            )

            assert result.id == 1
            assert result.notes == "Updated notes"

    async def test_update_checklist_not_found(self, sample_user) -> None:
        """Test update_checklist for non-existent checklist raises 404 (line 174)."""
        uow = MagicMock()

        update_data = ChecklistUpdate(notes="Updated notes")

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(side_effect=NotFoundException("Checklist"))

            with pytest.raises(HTTPException) as exc_info:
                await checklists.update_checklist(
                    checklist_id=999,
                    checklist_data=update_data,
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404


class TestDeleteChecklist:
    """Test DELETE /checklists/{id} endpoint."""

    async def test_delete_checklist_success(self, sample_hr_user) -> None:
        """Test successful checklist deletion."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.delete_checklist = AsyncMock(return_value=None)

            result = await checklists.delete_checklist(
                checklist_id=1,
                uow=uow,
                _current_user=sample_hr_user,
            )

            assert "deleted" in result.message.lower() or "success" in result.message.lower()


class TestCompleteChecklist:
    """Test POST /checklists/{id}/complete endpoint."""

    async def test_complete_checklist_success(self, sample_user) -> None:
        """Test successful checklist completion."""
        uow = MagicMock()
        now = datetime.now(UTC)

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.user_id = 1
        checklist_mock.employee_id = "EMP001"
        checklist_mock.template_id = 1
        checklist_mock.status = ChecklistStatus.COMPLETED
        checklist_mock.progress_percentage = 100
        checklist_mock.completed_tasks = 5
        checklist_mock.total_tasks = 5
        checklist_mock.start_date = now
        checklist_mock.due_date = now + timedelta(days=30)
        checklist_mock.completed_at = now
        checklist_mock.mentor_id = 2
        checklist_mock.hr_id = 3
        checklist_mock.notes = "Test checklist"
        checklist_mock.created_at = now
        checklist_mock.updated_at = now

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(return_value=checklist_mock)
            instance.complete_checklist = AsyncMock(return_value=checklist_mock)

            result = await checklists.complete_checklist(
                checklist_id=1,
                uow=uow,
                current_user=sample_user,
            )

            assert result.status == ChecklistStatus.COMPLETED
            assert result.progress_percentage == 100


class TestGetChecklistProgress:
    """Test GET /checklists/{id}/progress endpoint."""

    async def test_get_checklist_progress(self, sample_user) -> None:
        """Test getting checklist progress."""
        uow = MagicMock()

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.user_id = 1

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(return_value=checklist_mock)
            instance.get_checklist_progress = AsyncMock(return_value={
                "checklist_id": 1,
                "completed_tasks": 3,
                "total_tasks": 5,
                "completion_rate": 60.0,
            })

            result = await checklists.get_checklist_progress(
                checklist_id=1,
                uow=uow,
                current_user=sample_user,
            )

            assert result["checklist_id"] == 1
            assert result["completion_rate"] == 60.0


class TestGetChecklistStats:
    """Test GET /checklists/stats/summary endpoint."""

    async def test_get_checklist_stats(self, sample_hr_user) -> None:
        """Test getting checklist statistics."""
        uow = MagicMock()

        stats = ChecklistStats(
            total=10,
            completed=5,
            in_progress=3,
            overdue=1,
            not_started=1,
            avg_completion_days=15.5,
            completion_rate=50.0,
            by_department={"1": 8},
            recent_completions=[],
        )

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist_stats = AsyncMock(return_value=stats)

            result = await checklists.get_checklist_stats(
                uow=uow,
                _current_user=sample_hr_user,
            )

            assert result.total == 10
            assert result.completion_rate == 50.0


class TestAutoCreateChecklists:
    """Test POST /checklists/auto-create endpoint."""

    @pytest.mark.usefixtures("sample_hr_user")
    async def test_auto_create_checklists(self) -> None:
        """Test auto-creating checklists from templates."""
        uow = MagicMock()
        now = datetime.now(UTC)

        request_data = AutoCreateChecklistsRequest(
            user_id=1,
            employee_id="EMP001",
            department_id=1,
            position="Developer",
            mentor_id=2,
        )

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.user_id = 1
        checklist_mock.employee_id = "EMP001"
        checklist_mock.template_id = 1
        checklist_mock.status = ChecklistStatus.IN_PROGRESS
        checklist_mock.progress_percentage = 0
        checklist_mock.completed_tasks = 0
        checklist_mock.total_tasks = 5
        checklist_mock.start_date = now
        checklist_mock.due_date = now + timedelta(days=30)
        checklist_mock.completed_at = None
        checklist_mock.mentor_id = 2
        checklist_mock.hr_id = None
        checklist_mock.notes = None
        checklist_mock.created_at = now
        checklist_mock.updated_at = None

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.auto_create_checklists = AsyncMock(return_value=[checklist_mock])

            result = await checklists.auto_create_checklists(
                request=request_data,
                uow=uow,
                _service_auth=True,
            )

            assert len(result) == 1
            assert result[0].user_id == 1


class TestMonthlyStats:
    """Test GET /checklists/stats/monthly endpoint."""

    async def test_get_monthly_stats(self, sample_hr_user) -> None:
        """Test getting monthly statistics."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_monthly_stats = AsyncMock(return_value=[
                {"month": "Jan", "new_checklists": 5, "completed": 3},
                {"month": "Feb", "new_checklists": 8, "completed": 6},
            ])

            result = await checklists.get_monthly_stats(
                uow=uow,
                _current_user=sample_hr_user,
                months=6,
            )

            assert len(result) == 2
            assert result[0].month == "Jan"


class TestCompletionTimeStats:
    """Test GET /checklists/stats/completion-time endpoint."""

    async def test_get_completion_time_stats(self, sample_hr_user) -> None:
        """Test getting completion time distribution."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_completion_time_distribution = AsyncMock(return_value=[
                {"range": "1-7 days", "count": 5},
                {"range": "8-14 days", "count": 10},
            ])

            result = await checklists.get_completion_time_stats(
                uow=uow,
                _current_user=sample_hr_user,
            )

            assert len(result) == 2
            assert result[0].range == "1-7 days"


class TestChecklistEndpointsErrorHandling:
    """Test error handling and permission denied scenarios."""

    async def test_get_checklists_permission_denied_viewing_others(self, sample_user) -> None:
        """Test permission denied when viewing another user's checklists."""
        uow = MagicMock()

        with pytest.raises(PermissionDenied) as exc_info:
            await checklists.get_checklists(
                uow=uow,
                current_user=sample_user,  # User ID 1
                user_id=999,  # Trying to view different user's checklists
            )

        assert "Cannot view other users' checklists" in str(exc_info.value.detail)

    async def test_create_checklist_validation_exception(self, sample_hr_user) -> None:
        """Test create_checklist handles ValidationException."""
        uow = MagicMock()

        now = datetime.now(UTC)
        checklist_data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=now,
            due_date=now + timedelta(days=30),
        )

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.create_checklist = AsyncMock(side_effect=ValidationException("Invalid template"))

            with pytest.raises(HTTPException) as exc_info:
                await checklists.create_checklist(
                    checklist_data=checklist_data,
                    uow=uow,
                    _current_user=sample_hr_user,
                    auth_token="mock-token",  # noqa: S106
                )

            assert exc_info.value.status_code == 400
            assert "Invalid template" in str(exc_info.value.detail)

    async def test_get_checklist_permission_denied(self, sample_user) -> None:
        """Test get_checklist raises 403 when accessing other user's checklist."""
        uow = MagicMock()
        now = datetime.now(UTC)

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(return_value=MagicMock(
                id=1,
                user_id=999,  # Different user
                due_date=now + timedelta(days=30),
                status=ChecklistStatus.IN_PROGRESS,
            ))

            with pytest.raises(HTTPException) as exc_info:
                await checklists.get_checklist(
                    checklist_id=1,
                    uow=uow,
                    current_user=sample_user,  # User ID 1
                )

            assert exc_info.value.status_code == 403

    async def test_update_checklist_permission_denied(self, sample_user) -> None:
        """Test update_checklist raises 403 when updating other user's checklist."""
        uow = MagicMock()

        update_data = ChecklistUpdate(notes="Updated notes")

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(return_value=MagicMock(
                id=1,
                user_id=999,  # Different user
                due_date=datetime.now(UTC) + timedelta(days=30),
                status=ChecklistStatus.IN_PROGRESS,
            ))

            with pytest.raises(HTTPException) as exc_info:
                await checklists.update_checklist(
                    checklist_id=1,
                    checklist_data=update_data,
                    uow=uow,
                    current_user=sample_user,  # User ID 1
                )

            assert exc_info.value.status_code == 403

    async def test_delete_checklist_not_found(self, sample_hr_user) -> None:
        """Test delete_checklist raises 404 for non-existent checklist."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.delete_checklist = AsyncMock(side_effect=NotFoundException("Checklist"))

            with pytest.raises(HTTPException) as exc_info:
                await checklists.delete_checklist(
                    checklist_id=999,
                    uow=uow,
                    _current_user=sample_hr_user,
                )

            assert exc_info.value.status_code == 404

    async def test_complete_checklist_permission_denied(self, sample_user) -> None:
        """Test complete_checklist raises 403 when completing other user's checklist."""
        uow = MagicMock()
        now = datetime.now(UTC)

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(return_value=MagicMock(
                id=1,
                user_id=999,  # Different user
                due_date=now,
                status=ChecklistStatus.IN_PROGRESS,
            ))

            with pytest.raises(HTTPException) as exc_info:
                await checklists.complete_checklist(
                    checklist_id=1,
                    uow=uow,
                    current_user=sample_user,  # User ID 1
                )

            assert exc_info.value.status_code == 403

    async def test_get_checklist_progress_permission_denied(self, sample_user) -> None:
        """Test get_checklist_progress raises 403 for other user's checklist."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(return_value=MagicMock(
                id=1,
                user_id=999,  # Different user
            ))

            with pytest.raises(HTTPException) as exc_info:
                await checklists.get_checklist_progress(
                    checklist_id=1,
                    uow=uow,
                    current_user=sample_user,  # User ID 1
                )

            assert exc_info.value.status_code == 403

    async def test_complete_checklist_not_found(self, sample_user) -> None:
        """Test complete_checklist raises 404 for non-existent checklist (line 222)."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(side_effect=NotFoundException("Checklist"))

            with pytest.raises(HTTPException) as exc_info:
                await checklists.complete_checklist(
                    checklist_id=999,
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404

    async def test_get_checklist_progress_not_found(self, sample_user) -> None:
        """Test get_checklist_progress raises 404 for non-existent checklist."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.checklists.ChecklistService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_checklist = AsyncMock(side_effect=NotFoundException("Checklist"))

            with pytest.raises(HTTPException) as exc_info:
                await checklists.get_checklist_progress(
                    checklist_id=999,
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404
