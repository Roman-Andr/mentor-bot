"""Unit tests for base SQLAlchemy repository implementation."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from auth_service.models import Department, User
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TestSqlAlchemyBaseRepository:
    """Tests for SqlAlchemyBaseRepository implementation."""

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
        result.scalars = MagicMock()
        return result

    @pytest.fixture
    def sample_department(self):
        """Create a sample department."""
        dept = MagicMock(spec=Department)
        dept.id = 1
        return dept

    async def test_get_by_id_success(self, mock_session, mock_result, sample_department):
        """Test getting entity by ID successfully."""
        mock_result.scalar_one_or_none.return_value = sample_department
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Department)
        result = await repo.get_by_id(1)

        assert result == sample_department
        mock_session.execute.assert_awaited_once()

    async def test_get_by_id_not_found(self, mock_session, mock_result):
        """Test getting entity by ID when not found."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Department)
        result = await repo.get_by_id(999)

        assert result is None
        mock_session.execute.assert_awaited_once()

    async def test_get_all_success(self, mock_session, mock_result):
        """Test getting all entities with pagination."""
        dept1 = MagicMock(spec=Department)
        dept2 = MagicMock(spec=Department)
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [dept1, dept2]
        mock_result.scalars.return_value = scalars_mock
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Department)
        result = await repo.get_all(skip=0, limit=100)

        assert len(result) == 2
        assert result[0] == dept1
        assert result[1] == dept2

    async def test_get_all_with_pagination(self, mock_session, mock_result):
        """Test getting all entities with custom pagination."""
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        mock_result.scalars.return_value = scalars_mock
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Department)
        result = await repo.get_all(skip=10, limit=20)

        assert result == []
        # Verify offset and limit are applied in the query
        call_args = mock_session.execute.call_args
        stmt = call_args[0][0]
        assert "LIMIT 20" in str(stmt) or "limit" in str(stmt).lower()
        assert "OFFSET 10" in str(stmt) or "offset" in str(stmt).lower()

    async def test_create_success(self, mock_session, sample_department):
        """Test creating an entity."""
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        repo = SqlAlchemyBaseRepository(mock_session, Department)
        result = await repo.create(sample_department)

        mock_session.add.assert_called_once_with(sample_department)
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(sample_department)
        assert result == sample_department

    async def test_update_success(self, mock_session, sample_department):
        """Test updating an entity."""
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        repo = SqlAlchemyBaseRepository(mock_session, Department)
        result = await repo.update(sample_department)

        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(sample_department)
        assert result == sample_department

    async def test_delete_success(self, mock_session, mock_result, sample_department):
        """Test deleting an entity successfully."""
        mock_result.scalar_one_or_none.return_value = sample_department
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()

        repo = SqlAlchemyBaseRepository(mock_session, Department)
        result = await repo.delete(1)

        assert result is True
        mock_session.delete.assert_awaited_once_with(sample_department)
        mock_session.flush.assert_awaited_once()

    async def test_delete_not_found(self, mock_session, mock_result):
        """Test deleting an entity that doesn't exist."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Department)
        result = await repo.delete(999)

        assert result is False
        mock_session.delete.assert_not_called()

    async def test_init_sets_session_and_model(self, mock_session):
        """Test that __init__ properly sets session and model class."""
        repo = SqlAlchemyBaseRepository(mock_session, User)

        assert repo._session is mock_session
        assert repo._model_class is User

    async def test_get_by_id_with_string_id(self, mock_session, mock_result):
        """Test getting entity by string ID."""
        user = MagicMock(spec=User)
        mock_result.scalar_one_or_none.return_value = user
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, User)
        result = await repo.get_by_id("user-123")

        assert result == user
