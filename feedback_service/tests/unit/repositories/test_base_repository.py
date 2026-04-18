"""Unit tests for SqlAlchemyBaseRepository."""

from unittest.mock import MagicMock

from feedback_service.models import PulseSurvey
from feedback_service.repositories.implementations.base import SqlAlchemyBaseRepository


class TestGetById:
    """Tests for get_by_id method."""

    async def test_get_by_id_returns_entity(self, mock_db: MagicMock) -> None:
        """Test get_by_id returns entity when found."""
        # Arrange
        expected_entity = MagicMock(spec=PulseSurvey)
        expected_entity.id = 1

        # Mock the execute result chain: execute() -> scalar_one_or_none()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_entity
        mock_db.execute.return_value = mock_result

        repo: SqlAlchemyBaseRepository[PulseSurvey, int] = SqlAlchemyBaseRepository(mock_db, PulseSurvey)

        # Act
        result = await repo.get_by_id(1)

        # Assert
        assert result == expected_entity
        mock_db.execute.assert_called_once()

    async def test_get_by_id_returns_none_when_not_found(self, mock_db: MagicMock) -> None:
        """Test get_by_id returns None when entity not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        repo: SqlAlchemyBaseRepository[PulseSurvey, int] = SqlAlchemyBaseRepository(mock_db, PulseSurvey)

        # Act
        result = await repo.get_by_id(999)

        # Assert
        assert result is None


class TestGetAll:
    """Tests for get_all method."""

    async def test_get_all_returns_list(self, mock_db: MagicMock) -> None:
        """Test get_all returns list of entities with pagination."""
        # Arrange
        expected_entities = [MagicMock(spec=PulseSurvey), MagicMock(spec=PulseSurvey)]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = expected_entities
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo: SqlAlchemyBaseRepository[PulseSurvey, int] = SqlAlchemyBaseRepository(mock_db, PulseSurvey)

        # Act
        result = await repo.get_all(skip=0, limit=10)

        # Assert
        assert result == expected_entities
        assert len(result) == 2

    async def test_get_all_returns_empty_list(self, mock_db: MagicMock) -> None:
        """Test get_all returns empty list when no entities."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo: SqlAlchemyBaseRepository[PulseSurvey, int] = SqlAlchemyBaseRepository(mock_db, PulseSurvey)

        # Act
        result = await repo.get_all(skip=0, limit=100)

        # Assert
        assert result == []


class TestCreate:
    """Tests for create method."""

    async def test_create_adds_flushes_and_refreshes(self, mock_db: MagicMock, mock_pulse_survey: MagicMock) -> None:
        """Test create adds entity, flushes, and refreshes."""
        # Arrange
        repo: SqlAlchemyBaseRepository[PulseSurvey, int] = SqlAlchemyBaseRepository(mock_db, PulseSurvey)

        # Act
        result = await repo.create(mock_pulse_survey)

        # Assert
        mock_db.add.assert_called_once_with(mock_pulse_survey)
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_pulse_survey)
        assert result == mock_pulse_survey


class TestUpdate:
    """Tests for update method."""

    async def test_update_flushes_and_refreshes(self, mock_db: MagicMock, mock_pulse_survey: MagicMock) -> None:
        """Test update flushes and refreshes entity."""
        # Arrange
        repo: SqlAlchemyBaseRepository[PulseSurvey, int] = SqlAlchemyBaseRepository(mock_db, PulseSurvey)

        # Act
        result = await repo.update(mock_pulse_survey)

        # Assert
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_pulse_survey)
        assert result == mock_pulse_survey


class TestDelete:
    """Tests for delete method."""

    async def test_delete_returns_true_when_entity_exists(self, mock_db: MagicMock) -> None:
        """Test delete returns True when entity exists and is deleted."""
        # Arrange
        expected_entity = MagicMock(spec=PulseSurvey)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_entity
        mock_db.execute.return_value = mock_result

        repo: SqlAlchemyBaseRepository[PulseSurvey, int] = SqlAlchemyBaseRepository(mock_db, PulseSurvey)

        # Act
        result = await repo.delete(1)

        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(expected_entity)
        mock_db.flush.assert_called_once()

    async def test_delete_returns_false_when_entity_not_found(self, mock_db: MagicMock) -> None:
        """Test delete returns False when entity not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        repo: SqlAlchemyBaseRepository[PulseSurvey, int] = SqlAlchemyBaseRepository(mock_db, PulseSurvey)

        # Act
        result = await repo.delete(999)

        # Assert
        assert result is False
        mock_db.delete.assert_not_called()
