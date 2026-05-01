"""Tests for task repository implementation."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.core.enums import TaskStatus
from checklists_service.models import Task
from checklists_service.repositories.implementations.task import TaskRepository


class TestTaskRepository:
    """Test task repository."""

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
        """Create a task repository instance."""
        return TaskRepository(mock_session)

    @pytest.fixture
    def sample_task(self):
        """Create a sample task."""
        now = datetime.now(UTC)
        task = MagicMock(spec=Task)
        task.id = 1
        task.checklist_id = 1
        task.title = "Test Task"
        task.status = TaskStatus.PENDING
        task.order = 0
        task.category = "DOCUMENTATION"
        task.due_date = now + timedelta(days=7)
        task.assignee_id = 2
        task.assignee_role = "MENTOR"
        task.depends_on = []
        task.created_at = now
        return task

    async def test_find_by_checklist_basic(self, repository, mock_session, sample_task):
        """Test finding tasks by checklist."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_task]
        mock_session.execute.return_value = mock_result

        result = await repository.find_by_checklist(1)

        assert len(result) == 1
        assert result[0].id == 1

    async def test_find_by_checklist_with_status_filter(self, repository, mock_session, sample_task):
        """Test finding tasks with status filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_task]
        mock_session.execute.return_value = mock_result

        result = await repository.find_by_checklist(1, status="PENDING")

        assert len(result) == 1

    async def test_find_by_checklist_with_category_filter(self, repository, mock_session, sample_task):
        """Test finding tasks with category filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_task]
        mock_session.execute.return_value = mock_result

        result = await repository.find_by_checklist(1, category="DOCUMENTATION")

        assert len(result) == 1

    async def test_find_by_checklist_overdue_only(self, repository, mock_session, sample_task):
        """Test finding only overdue tasks."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_task]
        mock_session.execute.return_value = mock_result

        result = await repository.find_by_checklist(1, overdue_only=True)

        assert len(result) == 1

    async def test_find_assigned_basic(self, repository, mock_session, sample_task):
        """Test finding tasks assigned to user."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_task]
        mock_session.execute.return_value = mock_result

        tasks, total = await repository.find_assigned(2)

        assert total == 1
        assert len(tasks) == 1
        assert tasks[0].assignee_id == 2

    async def test_find_assigned_with_status(self, repository, mock_session, sample_task):
        """Test finding assigned tasks with status filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_result.scalars.return_value.all.return_value = [sample_task]
        mock_session.execute.return_value = mock_result

        _tasks, total = await repository.find_assigned(2, status="PENDING")

        assert total == 5

    async def test_find_assigned_pagination(self, repository, mock_session):
        """Test assigned tasks pagination."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 20
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        _tasks, total = await repository.find_assigned(2, skip=10, limit=5)

        assert total == 20

    async def test_get_dependencies_with_task(self, repository, mock_session, sample_task):
        """Test getting dependencies for task."""
        sample_task.depends_on = [2, 3]

        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = sample_task

        # Dependencies query
        mock_dep_task = MagicMock()
        mock_dep_task.id = 2
        mock_dep_task.title = "Dependency Task"
        mock_dep_task.status = TaskStatus.COMPLETED
        mock_dep_task.completed_at = datetime.now(UTC)
        mock_result2 = MagicMock()
        mock_result2.scalars.return_value.all.return_value = [mock_dep_task]

        # Blocked tasks query
        mock_result3 = MagicMock()
        mock_result3.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [mock_result1, mock_result2, mock_result3]

        result = await repository.get_dependencies(1)

        assert result["task_id"] == 1
        assert len(result["dependencies"]) == 1
        assert result["can_complete"] is True

    async def test_get_dependencies_no_task(self, repository, mock_session):
        """Test getting dependencies for non-existent task."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_dependencies(999)

        assert result == {}

    async def test_get_dependencies_no_dependencies(self, repository, mock_session, sample_task):
        """Test getting dependencies when task has none."""
        sample_task.depends_on = None

        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = sample_task

        mock_result2 = MagicMock()
        mock_result2.scalars.return_value.all.return_value = []

        mock_result3 = MagicMock()
        mock_result3.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [mock_result1, mock_result2, mock_result3]

        result = await repository.get_dependencies(1)

        assert result["dependencies"] == []
        assert result["can_complete"] is True

    async def test_get_dependencies_with_blocked(self, repository, mock_session, sample_task):
        """Test getting dependencies with incomplete dependencies."""
        sample_task.depends_on = [2]

        mock_dep_task = MagicMock()
        mock_dep_task.id = 2
        mock_dep_task.title = "Incomplete Task"
        mock_dep_task.status = TaskStatus.PENDING
        mock_dep_task.completed_at = None

        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = sample_task

        mock_result2 = MagicMock()
        mock_result2.scalars.return_value.all.return_value = [mock_dep_task]

        mock_result3 = MagicMock()
        mock_result3.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [mock_result1, mock_result2, mock_result3]

        result = await repository.get_dependencies(1)

        assert result["can_complete"] is False

    async def test_get_incomplete_dependencies_with_deps(self, repository, mock_session, sample_task):
        """Test getting incomplete dependencies."""
        sample_task.depends_on = [2, 3]

        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = sample_task

        mock_incomplete_task = MagicMock()
        mock_incomplete_task.id = 2
        mock_result2 = MagicMock()
        mock_result2.scalars.return_value.all.return_value = [mock_incomplete_task]

        mock_session.execute.side_effect = [mock_result1, mock_result2]

        result = await repository.get_incomplete_dependencies(1)

        assert len(result) == 1
        assert result[0].id == 2

    async def test_get_incomplete_dependencies_no_task(self, repository, mock_session):
        """Test getting incomplete dependencies when task doesn't exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_incomplete_dependencies(999)

        assert result == []

    async def test_get_incomplete_dependencies_no_deps(self, repository, mock_session, sample_task):
        """Test getting incomplete dependencies when task has none."""
        sample_task.depends_on = []

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task
        mock_session.execute.return_value = mock_result

        result = await repository.get_incomplete_dependencies(1)

        assert result == []

    async def test_get_blocked_by(self, repository, mock_session):
        """Test getting tasks blocked by this task."""
        mock_blocked_task = MagicMock()
        mock_blocked_task.id = 5
        mock_blocked_task.status = TaskStatus.BLOCKED

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_blocked_task]
        mock_session.execute.return_value = mock_result

        result = await repository.get_blocked_by(1)

        assert len(result) == 1
        assert result[0].id == 5

    async def test_count_by_status(self, repository, mock_session):
        """Test counting tasks by status."""
        mock_result = MagicMock()
        mock_result.all.return_value = [("completed", 5), ("pending", 3)]
        mock_session.execute.return_value = mock_result

        result = await repository.count_by_status(1)

        assert result["completed"] == 5
        assert result["pending"] == 3

    async def test_count_by_category(self, repository, mock_session):
        """Test counting tasks by category."""
        mock_result = MagicMock()
        mock_result.all.return_value = [("DOCUMENTATION", 4), ("TECHNICAL", 6)]
        mock_session.execute.return_value = mock_result

        result = await repository.count_by_category(1)

        assert result["DOCUMENTATION"] == 4
        assert result["TECHNICAL"] == 6

    async def test_count_overdue(self, repository, mock_session):
        """Test counting overdue tasks."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        mock_session.execute.return_value = mock_result

        result = await repository.count_overdue(1)

        assert result == 3

    async def test_count_overdue_none(self, repository, mock_session):
        """Test counting overdue tasks when none exist."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.count_overdue(1)

        assert result == 0

    async def test_get_blocked_tasks(self, repository, mock_session, sample_task):
        """Test getting blocked tasks for checklist."""
        sample_task.status = TaskStatus.BLOCKED
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_task]
        mock_session.execute.return_value = mock_result

        result = await repository.get_blocked_tasks(1)

        assert len(result) == 1
        assert result[0].status == TaskStatus.BLOCKED

    async def test_find_by_ids(self, repository, mock_session):
        """Test finding tasks by list of IDs."""
        mock_task1 = MagicMock(id=1)
        mock_task2 = MagicMock(id=2)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_task1, mock_task2]
        mock_session.execute.return_value = mock_result

        result = await repository.find_by_ids([1, 2, 3])

        assert len(result) == 2

    async def test_find_by_ids_empty_list(self, repository, mock_session):
        """Test finding tasks with empty ID list."""
        result = await repository.find_by_ids([])

        assert result == []
        mock_session.execute.assert_not_called()

    async def test_find_by_checklist_combined_filters(
        self, repository, mock_session, sample_task
    ):
        """Test finding tasks with multiple filters combined."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_task]
        mock_session.execute.return_value = mock_result

        result = await repository.find_by_checklist(
            1, status="PENDING", category="DOCUMENTATION", overdue_only=True
        )

        assert len(result) == 1

    async def test_find_assigned_combined_filters(
        self, repository, mock_session, sample_task
    ):
        """Test finding assigned tasks with status filter and pagination."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_result.scalars.return_value.all.return_value = [sample_task]
        mock_session.execute.return_value = mock_result

        tasks, total = await repository.find_assigned(
            2, status="PENDING", skip=5, limit=10
        )

        assert total == 10
        assert len(tasks) == 1
