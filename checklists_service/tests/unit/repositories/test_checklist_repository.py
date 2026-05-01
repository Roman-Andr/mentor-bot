"""Tests for checklist repository implementation."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.core.enums import ChecklistStatus
from checklists_service.models import Checklist
from checklists_service.repositories.implementations.checklist import ChecklistRepository


class TestChecklistRepository:
    """Test checklist repository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock SQLAlchemy session."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Create a checklist repository instance."""
        return ChecklistRepository(mock_session)

    @pytest.fixture
    def sample_checklist(self):
        """Create a sample checklist."""
        now = datetime.now(UTC)
        checklist = MagicMock(spec=Checklist)
        checklist.id = 1
        checklist.user_id = 1
        checklist.employee_id = "EMP001"
        checklist.template_id = 1
        checklist.status = ChecklistStatus.IN_PROGRESS
        checklist.progress_percentage = 50
        checklist.completed_tasks = 2
        checklist.total_tasks = 4
        checklist.start_date = now
        checklist.due_date = now + timedelta(days=30)
        checklist.completed_at = None
        checklist.created_at = now
        return checklist

    async def test_find_checklists_basic(self, repository, mock_session, sample_checklist):
        """Test finding checklists without filters."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_checklist]
        mock_session.execute.return_value = mock_result

        checklists, total = await repository.find_checklists()

        assert total == 1
        assert len(checklists) == 1
        assert checklists[0].id == 1

    async def test_find_checklists_with_user_filter(self, repository, mock_session, sample_checklist):
        """Test finding checklists with user_id filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_checklist]
        mock_session.execute.return_value = mock_result

        _checklists, total = await repository.find_checklists(user_id=1)

        assert total == 1

    async def test_find_checklists_with_status_filter(self, repository, mock_session, sample_checklist):
        """Test finding checklists with status filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_checklist]
        mock_session.execute.return_value = mock_result

        _checklists, total = await repository.find_checklists(status=ChecklistStatus.IN_PROGRESS)

        assert total == 1

    async def test_find_checklists_with_department_filter(self, repository, mock_session, sample_checklist):
        """Test finding checklists with department_id filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_checklist]
        mock_session.execute.return_value = mock_result

        _checklists, total = await repository.find_checklists(department_id=1)

        assert total == 1

    async def test_find_checklists_with_search(self, repository, mock_session, sample_checklist):
        """Test finding checklists with search filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_checklist]
        mock_session.execute.return_value = mock_result

        _checklists, total = await repository.find_checklists(search="EMP")

        assert total == 1

    async def test_find_checklists_overdue_only(self, repository, mock_session, sample_checklist):
        """Test finding only overdue checklists."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_checklist]
        mock_session.execute.return_value = mock_result

        _checklists, total = await repository.find_checklists(overdue_only=True)

        assert total == 1

    async def test_find_checklists_pagination(self, repository, mock_session):
        """Test checklist pagination."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 100
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        _checklists, total = await repository.find_checklists(skip=20, limit=10)

        assert total == 100

    async def test_find_checklists_sort_asc(self, repository, mock_session, sample_checklist):
        """Test finding checklists with ascending sort order (line 86)."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_checklist]
        mock_session.execute.return_value = mock_result

        _checklists, total = await repository.find_checklists(sort_by="status", sort_order="asc")

        assert total == 1
        # Verify the query was called with asc() ordering
        call_stmt = str(mock_session.execute.call_args[0][0])
        assert "ORDER BY" in call_stmt

    async def test_get_active_by_user_found(self, repository, mock_session, sample_checklist):
        """Test getting active checklist for user when exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_checklist
        mock_session.execute.return_value = mock_result

        result = await repository.get_active_by_user(1)

        assert result is not None
        assert result.id == 1

    async def test_get_active_by_user_not_found(self, repository, mock_session):
        """Test getting active checklist when none exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_active_by_user(999)

        assert result is None

    async def test_get_progress_with_checklist(self, repository, mock_session, sample_checklist):
        """Test getting progress for existing checklist."""
        # First call - get checklist
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = sample_checklist

        # Second call - status counts
        mock_result2 = MagicMock()
        mock_result2.all.return_value = [("completed", 2), ("pending", 2)]

        # Third call - category counts
        mock_result3 = MagicMock()
        mock_result3.all.return_value = [("documentation", 2), ("technical", 2)]

        # Fourth call - overdue count
        mock_result4 = MagicMock()
        mock_result4.scalar_one.return_value = 0

        mock_session.execute.side_effect = [
            mock_result1, mock_result2, mock_result3, mock_result4
        ]

        result = await repository.get_progress(1)

        assert result["checklist_id"] == 1
        assert result["total_tasks"] == 4
        assert result["completed_tasks"] == 2
        assert result["completion_rate"] == 50.0

    async def test_get_progress_no_checklist(self, repository, mock_session):
        """Test getting progress for non-existent checklist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_progress(999)

        assert result == {}

    async def test_get_progress_with_blocked_tasks(self, repository, mock_session, sample_checklist):
        """Test getting progress with blocked tasks."""
        # Setup mock results for multiple queries
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = sample_checklist

        mock_result2 = MagicMock()
        mock_result2.all.return_value = [("completed", 2), ("blocked", 1)]

        mock_result3 = MagicMock()
        mock_result3.all.return_value = [("documentation", 3)]

        mock_result4 = MagicMock()
        mock_result4.scalar_one.return_value = 1  # overdue

        mock_result5 = MagicMock()
        mock_blocked_task = MagicMock()
        mock_blocked_task.id = 5
        mock_blocked_task.title = "Blocked Task"
        mock_result5.scalars.return_value.all.return_value = [mock_blocked_task]

        mock_session.execute.side_effect = [
            mock_result1, mock_result2, mock_result3, mock_result4, mock_result5
        ]

        result = await repository.get_progress(1)

        assert "blocked_tasks" in result
        assert len(result["blocked_tasks"]) == 1

    async def test_get_statistics_basic(self, repository, mock_session):
        """Test getting basic statistics."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_session.execute.return_value = mock_result

        stats = await repository.get_statistics()

        assert stats["total"] == 10
        assert stats["completed"] == 10
        assert stats["in_progress"] == 10
        assert stats["not_started"] == 10
        assert stats["overdue"] == 10

    async def test_get_statistics_with_user_filter(self, repository, mock_session):
        """Test getting statistics filtered by user."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_session.execute.return_value = mock_result

        stats = await repository.get_statistics(user_id=1)

        assert stats["total"] == 5

    async def test_get_statistics_with_department_filter(self, repository, mock_session):
        """Test getting statistics filtered by department."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        mock_session.execute.return_value = mock_result

        stats = await repository.get_statistics(department_id=1)

        assert stats["total"] == 3

    async def test_recalculate_progress(self, repository, mock_session):
        """Test recalculating checklist progress."""
        mock_checklist = MagicMock()
        mock_checklist.status = ChecklistStatus.IN_PROGRESS
        mock_checklist.completed_tasks = 0
        mock_checklist.total_tasks = 0
        mock_checklist.progress_percentage = 0
        mock_checklist.completed_at = None

        # First call - task counts
        mock_result1 = MagicMock()
        mock_row = MagicMock()
        mock_row.total = 10
        mock_row.completed = 5
        mock_result1.one.return_value = mock_row

        # Second call - get checklist
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = mock_checklist

        mock_session.execute.side_effect = [mock_result1, mock_result2]

        await repository.recalculate_progress(1)

        assert mock_checklist.completed_tasks == 5
        assert mock_checklist.total_tasks == 10
        assert mock_checklist.progress_percentage == 50

    async def test_recalculate_progress_completes_checklist(self, repository, mock_session):
        """Test that recalculate_progress marks checklist complete when all tasks done."""
        mock_checklist = MagicMock()
        mock_checklist.status = ChecklistStatus.IN_PROGRESS
        mock_checklist.completed_at = None

        mock_result1 = MagicMock()
        mock_row = MagicMock()
        mock_row.total = 5
        mock_row.completed = 5
        mock_result1.one.return_value = mock_row

        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = mock_checklist

        mock_session.execute.side_effect = [mock_result1, mock_result2]

        await repository.recalculate_progress(1)

        assert mock_checklist.status == ChecklistStatus.COMPLETED
        assert mock_checklist.completed_at is not None

    async def test_recalculate_progress_no_checklist(self, repository, mock_session):
        """Test recalculate_progress when checklist doesn't exist."""
        mock_result1 = MagicMock()
        mock_row = MagicMock()
        mock_row.total = 5
        mock_row.completed = 3
        mock_result1.one.return_value = mock_row

        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [mock_result1, mock_result2]

        # Should not raise exception
        await repository.recalculate_progress(999)

    async def test_get_by_user_and_template_found(self, repository, mock_session, sample_checklist):
        """Test getting checklist by user and template when exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_checklist
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_user_and_template(1, 1)

        assert result is not None
        assert result.id == 1

    async def test_get_by_user_and_template_not_found(self, repository, mock_session):
        """Test getting checklist by user and template when not exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_user_and_template(1, 999)

        assert result is None

    async def test_get_monthly_stats(self, repository, mock_session):
        """Test getting monthly statistics."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_session.execute.return_value = mock_result

        result = await repository.get_monthly_stats(months=3)

        assert len(result) == 3  # 3 months of data
        assert "month" in result[0]
        assert "new_checklists" in result[0]
        assert "completed" in result[0]

    async def test_get_monthly_stats_six_months(self, repository, mock_session):
        """Test getting 6 months of statistics."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_session.execute.return_value = mock_result

        result = await repository.get_monthly_stats(months=6)

        assert len(result) == 6

    async def test_get_completion_time_distribution(self, repository, mock_session):
        """Test getting completion time distribution."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_session.execute.return_value = mock_result

        result = await repository.get_completion_time_distribution()

        assert len(result) == 5  # 5 time ranges
        ranges = [r["range"] for r in result]
        assert "1-7 days" in ranges
        assert "8-14 days" in ranges
        assert "15-21 days" in ranges
        assert "22-30 days" in ranges
        assert ">30 days" in ranges

    async def test_get_completion_time_distribution_counts(self, repository, mock_session):
        """Test completion time distribution returns correct counts."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_session.execute.return_value = mock_result

        result = await repository.get_completion_time_distribution()

        for item in result:
            assert "range" in item
            assert "count" in item
            assert isinstance(item["count"], int)

    def test_get_sort_column_employee_id(self, repository):
        """Test _get_sort_column returns employee_id column."""
        column = repository._get_sort_column("employee_id")
        assert column is not None

    def test_get_sort_column_status(self, repository):
        """Test _get_sort_column returns status column."""
        column = repository._get_sort_column("status")
        assert column is not None

    def test_get_sort_column_progress(self, repository):
        """Test _get_sort_column returns progress column."""
        column = repository._get_sort_column("progress_percentage")
        assert column is not None

    def test_get_sort_column_start_date(self, repository):
        """Test _get_sort_column returns start_date column."""
        column = repository._get_sort_column("start_date")
        assert column is not None

    def test_get_sort_column_due_date(self, repository):
        """Test _get_sort_column returns due_date column."""
        column = repository._get_sort_column("due_date")
        assert column is not None

    def test_get_sort_column_completed_at(self, repository):
        """Test _get_sort_column returns completed_at column."""
        column = repository._get_sort_column("completed_at")
        assert column is not None

    def test_get_sort_column_created_at(self, repository):
        """Test _get_sort_column returns created_at column."""
        column = repository._get_sort_column("created_at")
        assert column is not None

    def test_get_sort_column_tasks(self, repository):
        """Test _get_sort_column returns total_tasks column."""
        column = repository._get_sort_column("tasks")
        assert column is not None

    def test_get_sort_column_default(self, repository):
        """Test _get_sort_column returns created_at for unknown sort_by."""
        column = repository._get_sort_column("unknown")
        assert column is not None

    def test_get_sort_column_camel_case_variants(self, repository):
        """Test _get_sort_column handles camelCase variants."""
        column1 = repository._get_sort_column("employeeId")
        column2 = repository._get_sort_column("startDate")
        column3 = repository._get_sort_column("dueDate")
        assert column1 is not None
        assert column2 is not None
        assert column3 is not None
