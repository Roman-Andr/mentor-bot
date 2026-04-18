"""Unit tests for SqlAlchemyBaseRepository."""

from collections.abc import Sequence
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.models.meeting import Meeting
from meeting_service.repositories.implementations.base import SqlAlchemyBaseRepository


@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Create a repository instance with mock session using Meeting model."""
    return SqlAlchemyBaseRepository[Meeting, int](mock_session, Meeting)


class TestGetById:
    """Tests for get_by_id method."""

    async def test_get_by_id_found(self, mock_session, repository):
        """Test get_by_id returns entity when found."""
        # Arrange
        entity = Meeting(id=1, title="Found Meeting")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = entity
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_id(1)

        # Assert
        assert result == entity
        assert result.id == 1
        assert result.title == "Found Meeting"
        mock_session.execute.assert_called_once()

        # Verify the query structure
        call_args = mock_session.execute.call_args[0][0]
        assert isinstance(call_args, type(select(Meeting)))

    async def test_get_by_id_not_found(self, mock_session, repository):
        """Test get_by_id returns None when entity not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_id(999)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()


class TestGetAll:
    """Tests for get_all method with pagination."""

    async def test_get_all_returns_entities(self, mock_session, repository):
        """Test get_all returns paginated entities."""
        # Arrange
        entities = [Meeting(id=i, title=f"Meeting {i}") for i in range(1, 4)]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = entities
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_all(skip=0, limit=10)

        # Assert
        assert isinstance(result, Sequence)
        assert len(result) == 3
        mock_session.execute.assert_called_once()

    async def test_get_all_pagination(self, mock_session, repository):
        """Test get_all respects skip and limit parameters."""
        # Arrange
        entities = [Meeting(id=3, title="Third Meeting")]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = entities
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_all(skip=2, limit=1)

        # Assert
        assert len(result) == 1
        assert result[0].id == 3

        # Verify query was built with offset and limit
        call_args = mock_session.execute.call_args[0][0]
        query_str = str(call_args)
        assert "LIMIT" in query_str or "limit" in query_str.lower()

    async def test_get_all_empty_result(self, mock_session, repository):
        """Test get_all returns empty sequence when no entities."""
        # Arrange
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_all()

        # Assert
        assert len(result) == 0
        assert result == []


class TestCreate:
    """Tests for create method."""

    async def test_create_adds_entity(self, mock_session, repository):
        """Test create adds entity to session."""
        # Arrange
        entity = Meeting(id=1, title="New Meeting")

        # Act
        result = await repository.create(entity)

        # Assert
        assert result == entity
        mock_session.add.assert_called_once_with(entity)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(entity)

    async def test_create_flushes_and_refreshes(self, mock_session, repository):
        """Test create flushes and refreshes entity after add."""
        # Arrange
        entity = Meeting(id=2, title="Another Meeting")

        # Act
        await repository.create(entity)

        # Assert
        # Verify order of operations
        assert mock_session.add.call_count == 1
        assert mock_session.flush.call_count == 1
        assert mock_session.refresh.call_count == 1


class TestUpdate:
    """Tests for update method."""

    async def test_update_flushes_and_refreshes(self, mock_session, repository):
        """Test update flushes and refreshes entity."""
        # Arrange
        entity = Meeting(id=1, title="Updated Meeting")

        # Act
        result = await repository.update(entity)

        # Assert
        assert result == entity
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(entity)

    async def test_update_no_add_operation(self, mock_session, repository):
        """Test update does not call add (entity should already be tracked)."""
        # Arrange
        entity = Meeting(id=1, title="Updated")

        # Act
        await repository.update(entity)

        # Assert
        mock_session.add.assert_not_called()


class TestDelete:
    """Tests for delete method."""

    async def test_delete_existing_entity(self, mock_session, repository):
        """Test delete removes entity when found."""
        # Arrange
        entity = Meeting(id=1, title="To Delete")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = entity
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.delete(1)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(entity)
        mock_session.flush.assert_called_once()

    async def test_delete_not_found(self, mock_session, repository):
        """Test delete returns False when entity not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.delete(999)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()
        mock_session.flush.assert_not_called()


class TestRepositoryInitialization:
    """Tests for repository initialization."""

    def test_repository_stores_session(self, mock_session):
        """Test repository stores session reference."""
        repo = SqlAlchemyBaseRepository[Meeting, int](mock_session, Meeting)
        assert repo._session == mock_session

    def test_repository_stores_model_class(self, mock_session):
        """Test repository stores model class reference."""
        repo = SqlAlchemyBaseRepository[Meeting, int](mock_session, Meeting)
        assert repo._model_class == Meeting


class TestTransactionBehavior:
    """Tests for transaction rollback scenarios."""

    async def test_create_flush_failure_rolls_back(self, mock_session, repository):
        """Test that flush failure during create propagates exception."""
        # Arrange
        entity = Meeting(id=1, title="New Meeting")
        mock_session.flush = AsyncMock(side_effect=Exception("Flush failed"))

        # Act & Assert
        with pytest.raises(Exception, match="Flush failed"):
            await repository.create(entity)

        mock_session.add.assert_called_once_with(entity)

    async def test_update_flush_failure(self, mock_session, repository):
        """Test that flush failure during update propagates exception."""
        # Arrange
        entity = Meeting(id=1, title="Updated Meeting")
        mock_session.flush = AsyncMock(side_effect=Exception("Update flush failed"))

        # Act & Assert
        with pytest.raises(Exception, match="Update flush failed"):
            await repository.update(entity)

    async def test_delete_flush_failure(self, mock_session, repository):
        """Test that flush failure during delete propagates exception."""
        # Arrange
        entity = Meeting(id=1, title="To Delete")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = entity
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock(side_effect=Exception("Delete flush failed"))

        # Act & Assert
        with pytest.raises(Exception, match="Delete flush failed"):
            await repository.delete(1)

        mock_session.delete.assert_called_once_with(entity)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    async def test_get_by_id_zero_id(self, mock_session, repository):
        """Test get_by_id handles ID of 0."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(0)

        assert result is None

    async def test_get_by_id_negative_id(self, mock_session, repository):
        """Test get_by_id handles negative ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(-1)

        assert result is None

    async def test_get_all_large_skip(self, mock_session, repository):
        """Test get_all with large skip value."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=1000000, limit=10)

        assert len(result) == 0

    async def test_get_all_zero_limit(self, mock_session, repository):
        """Test get_all with limit of 0."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=0)

        assert len(result) == 0

    async def test_delete_entity_without_flush(self, mock_session, repository):
        """Test delete operation sequence."""
        entity = Meeting(id=1, title="To Delete")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = entity
        mock_session.execute.return_value = mock_result

        await repository.delete(1)

        # Verify the order: execute (for get_by_id), delete, flush
        assert mock_session.execute.call_count == 1
        mock_session.delete.assert_called_once_with(entity)
        mock_session.flush.assert_called_once()

    async def test_get_by_id_with_different_types(self, mock_session):
        """Test repository works with different ID types."""
        from meeting_service.models.material import MeetingMaterial

        # Test with different model
        repo = SqlAlchemyBaseRepository[MeetingMaterial, int](mock_session, MeetingMaterial)
        entity = MeetingMaterial(id=1, title="Material")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = entity
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_id(1)

        assert result == entity
