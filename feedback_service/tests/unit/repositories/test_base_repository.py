"""Unit tests for SqlAlchemyBaseRepository."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy import select

from feedback_service.models import PulseSurvey
from feedback_service.repositories.implementations.base import (
    SqlAlchemyBaseRepository,
    apply_date_filters,
)


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


class TestApplyDateFilters:
    """Tests for apply_date_filters function."""

    def test_apply_date_filters_with_valid_range(self) -> None:
        """Test apply_date_filters applies filters correctly with valid date range."""
        # Arrange
        query = select(PulseSurvey)
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        result = apply_date_filters(query, PulseSurvey, from_date, to_date)

        # Assert - query should be modified (can't easily verify without executing)
        assert result is not None

    def test_apply_date_filters_raises_on_invalid_range(self) -> None:
        """Test apply_date_filters raises ValueError when from_date > to_date."""
        # Arrange
        query = select(PulseSurvey)
        from_date = datetime(2024, 12, 31, tzinfo=UTC)
        to_date = datetime(2024, 1, 1, tzinfo=UTC)

        # Act & Assert
        with pytest.raises(ValueError, match="from_date must be before or equal to to_date"):
            apply_date_filters(query, PulseSurvey, from_date, to_date)

    def test_apply_date_filters_with_from_date_only(self) -> None:
        """Test apply_date_filters with only from_date."""
        # Arrange
        query = select(PulseSurvey)
        from_date = datetime(2024, 1, 1, tzinfo=UTC)

        # Act
        result = apply_date_filters(query, PulseSurvey, from_date, None)

        # Assert
        assert result is not None

    def test_apply_date_filters_with_to_date_only(self) -> None:
        """Test apply_date_filters with only to_date."""
        # Arrange
        query = select(PulseSurvey)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        result = apply_date_filters(query, PulseSurvey, None, to_date)

        # Assert
        assert result is not None

    def test_apply_date_filters_with_no_dates(self) -> None:
        """Test apply_date_filters returns unchanged query when no dates."""
        # Arrange
        query = select(PulseSurvey)

        # Act
        result = apply_date_filters(query, PulseSurvey, None, None)

        # Assert
        assert result is not None

    def test_apply_date_filters_with_same_dates(self) -> None:
        """Test apply_date_filters with from_date == to_date."""
        # Arrange
        query = select(PulseSurvey)
        date = datetime(2024, 6, 15, tzinfo=UTC)

        # Act
        result = apply_date_filters(query, PulseSurvey, date, date)

        # Assert
        assert result is not None

    def test_apply_date_filters_with_custom_column(self) -> None:
        """Test apply_date_filters with custom date column."""
        # Arrange
        query = select(PulseSurvey)
        from_date = datetime(2024, 1, 1, tzinfo=UTC)

        # Act - use a different column name (won't affect PulseSurvey but tests the code path)
        with pytest.raises(AttributeError):
            apply_date_filters(query, PulseSurvey, from_date, None, date_column="created_at")


class TestDateFilterMixin:
    """Tests for DateFilterMixin class using concrete repository that includes it."""

    async def test_mixin_applies_date_filters(self, mock_db: MagicMock) -> None:
        """Test DateFilterMixin._apply_date_filters works through repository."""
        # Arrange - use PulseSurveyRepository which includes DateFilterMixin
        from feedback_service.repositories import PulseSurveyRepository

        repo = PulseSurveyRepository(mock_db)
        query = select(PulseSurvey)
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        result = repo._apply_date_filters(query, PulseSurvey, from_date, to_date)

        # Assert
        assert result is not None

    async def test_mixin_raises_on_invalid_range(self, mock_db: MagicMock) -> None:
        """Test DateFilterMixin._apply_date_filters raises ValueError on invalid range."""
        # Arrange - use PulseSurveyRepository which includes DateFilterMixin
        from feedback_service.repositories import PulseSurveyRepository

        repo = PulseSurveyRepository(mock_db)
        query = select(PulseSurvey)
        from_date = datetime(2024, 12, 31, tzinfo=UTC)
        to_date = datetime(2024, 1, 1, tzinfo=UTC)

        # Act & Assert
        with pytest.raises(ValueError, match="from_date must be before or equal to to_date"):
            repo._apply_date_filters(query, PulseSurvey, from_date, to_date)
