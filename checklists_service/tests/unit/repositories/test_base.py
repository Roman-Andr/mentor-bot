"""Tests for base repository implementation."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.models import Checklist
from checklists_service.repositories.implementations.base import SqlAlchemyBaseRepository


class TestSqlAlchemyBaseRepository:
    """Test base repository implementation."""

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
        """Create a base repository instance."""
        return SqlAlchemyBaseRepository(mock_session, Checklist)

    async def test_get_by_id_success(self, repository, mock_session):
        """Test getting entity by ID."""
        # Setup mock result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(id=1, name="Test")
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(1)

        assert result is not None
        mock_session.execute.assert_called_once()

    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting non-existent entity returns None."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(999)

        assert result is None

    async def test_get_all(self, repository, mock_session):
        """Test getting all entities with pagination."""
        mock_checklist = MagicMock(id=1)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_checklist]
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=100)

        assert len(result) == 1
        assert result[0].id == 1

    async def test_get_all_with_pagination(self, repository, mock_session):
        """Test pagination parameters are applied."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        await repository.get_all(skip=10, limit=50)

        # Verify offset and limit are in the call
        call_args = mock_session.execute.call_args[0][0]
        assert "OFFSET" in str(call_args).upper() or "offset" in str(call_args)
        assert "LIMIT" in str(call_args).upper() or "limit" in str(call_args)

    async def test_create(self, repository, mock_session):
        """Test creating an entity."""
        mock_entity = MagicMock(id=1)

        result = await repository.create(mock_entity)

        mock_session.add.assert_called_once_with(mock_entity)
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(mock_entity)
        assert result == mock_entity

    async def test_update(self, repository, mock_session):
        """Test updating an entity."""
        mock_entity = MagicMock(id=1)

        result = await repository.update(mock_entity)

        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(mock_entity)
        assert result == mock_entity

    async def test_delete_success(self, repository, mock_session):
        """Test deleting an existing entity."""
        mock_entity = MagicMock(id=1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_entity
        mock_session.execute.return_value = mock_result

        result = await repository.delete(1)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_entity)
        mock_session.flush.assert_awaited_once()

    async def test_delete_not_found(self, repository, mock_session):
        """Test deleting non-existent entity returns False."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.delete(999)

        assert result is False
        mock_session.delete.assert_not_called()
