"""Unit tests for Department repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import Department
from auth_service.repositories.implementations.department import DepartmentRepository


class TestDepartmentRepository:
    """Tests for DepartmentRepository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        return session

    @pytest.fixture
    def mock_result(self):
        """Create a mock SQLAlchemy result."""
        result = MagicMock()
        result.scalar_one_or_none = MagicMock()
        result.scalar_one = MagicMock()
        result.scalars = MagicMock()
        result.all = MagicMock()
        return result

    @pytest.fixture
    def sample_department(self):
        """Create a sample department."""
        return Department(
            id=1,
            name="Engineering",
            description="Software Engineering Department",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

    async def test_get_by_name_success(self, mock_session, mock_result, sample_department):
        """Test getting department by name."""
        mock_result.scalar_one_or_none.return_value = sample_department
        mock_session.execute.return_value = mock_result

        repo = DepartmentRepository(mock_session)
        result = await repo.get_by_name("Engineering")

        assert result == sample_department
        mock_session.execute.assert_awaited_once()

    async def test_get_by_name_not_found(self, mock_session, mock_result):
        """Test getting department by name when not found."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = DepartmentRepository(mock_session)
        result = await repo.get_by_name("NonExistent")

        assert result is None

    async def test_find_departments_without_filters(self, mock_session, mock_result):
        """Test finding departments without any filters."""
        dept1 = Department(id=1, name="Engineering", description="Eng", created_at=datetime.now(UTC))
        dept2 = Department(id=2, name="Marketing", description="Mkt", created_at=datetime.now(UTC))

        # First call is for count, second for results
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [dept1, dept2]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = DepartmentRepository(mock_session)
        departments, total = await repo.find_departments(skip=0, limit=100)

        assert total == 2
        assert len(departments) == 2
        assert departments[0].name == "Engineering"
        assert departments[1].name == "Marketing"

    async def test_find_departments_with_search(self, mock_session, mock_result):
        """Test finding departments with search filter."""
        dept = Department(id=1, name="Engineering", description="Eng", created_at=datetime.now(UTC))

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [dept]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = DepartmentRepository(mock_session)
        departments, total = await repo.find_departments(skip=0, limit=100, search="Eng")

        assert total == 1
        assert len(departments) == 1

    async def test_find_departments_pagination(self, mock_session, mock_result):
        """Test finding departments with pagination."""
        dept = Department(id=3, name="HR", description="HR Dept", created_at=datetime.now(UTC))

        count_result = MagicMock()
        count_result.scalar_one.return_value = 10

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [dept]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = DepartmentRepository(mock_session)
        departments, total = await repo.find_departments(skip=5, limit=1)

        assert total == 10
        assert len(departments) == 1

    async def test_init_calls_super(self, mock_session):
        """Test that __init__ properly initializes the repository."""
        repo = DepartmentRepository(mock_session)

        assert repo._session is mock_session
        assert repo._model_class == Department

    async def test_find_departments_with_empty_result(self, mock_session, mock_result):
        """Test finding departments when no results match."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = DepartmentRepository(mock_session)
        departments, total = await repo.find_departments(skip=0, limit=100, search="XYZ")

        assert total == 0
        assert len(departments) == 0

    async def test_find_departments_search_in_description(self, mock_session, mock_result):
        """Test that search filter applies to description field."""
        dept = Department(id=1, name="IT", description="Information Technology", created_at=datetime.now(UTC))

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [dept]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = DepartmentRepository(mock_session)
        departments, total = await repo.find_departments(skip=0, limit=100, search="Technology")

        assert total == 1
        assert departments[0].description == "Information Technology"

    async def test_find_departments_descending_sort(self, mock_session, mock_result):
        """Test finding departments with descending sort order."""
        dept1 = Department(id=1, name="Engineering", description="Eng", created_at=datetime.now(UTC))
        dept2 = Department(id=2, name="Marketing", description="Mkt", created_at=datetime.now(UTC))

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [dept2, dept1]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = DepartmentRepository(mock_session)
        departments, total = await repo.find_departments(skip=0, limit=100, sort_by="name", sort_order="desc")

        assert total == 2
        assert len(departments) == 2

    async def test_has_users_true(self, mock_session, mock_result):
        """Test has_users when department has users (covers lines 72-75)."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 5  # 5 users in this department
        mock_session.execute.return_value = count_result

        repo = DepartmentRepository(mock_session)
        result = await repo.has_users(department_id=1)

        assert result is True
        mock_session.execute.assert_awaited_once()

    async def test_has_users_false(self, mock_session, mock_result):
        """Test has_users when department has no users (covers lines 72-75)."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0  # No users
        mock_session.execute.return_value = count_result

        repo = DepartmentRepository(mock_session)
        result = await repo.has_users(department_id=1)

        assert result is False
        mock_session.execute.assert_awaited_once()
