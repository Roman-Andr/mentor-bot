"""Unit tests for FeedbackStatusChangeHistoryRepository."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from feedback_service.models import FeedbackStatusChangeHistory
from feedback_service.repositories.implementations.feedback_status_change_history import (
    FeedbackStatusChangeHistoryRepository,
)


class TestFeedbackStatusChangeHistoryRepository:
    """Tests for FeedbackStatusChangeHistoryRepository."""

    async def test_create(self) -> None:
        """Test creating a feedback status change history entry."""
        # Arrange
        mock_session = MagicMock()
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()

        repo = FeedbackStatusChangeHistoryRepository(mock_session)
        entity = MagicMock(spec=FeedbackStatusChangeHistory)

        # Act
        result = await repo.create(entity)

        # Assert
        mock_session.add.assert_called_once_with(entity)
        mock_session.flush.assert_called_once()
        assert result == entity

    async def test_get_by_feedback_id(self) -> None:
        """Test getting history by feedback_id without date filters."""
        # Arrange
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[MagicMock(spec=FeedbackStatusChangeHistory)])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = FeedbackStatusChangeHistoryRepository(mock_session)

        # Act
        result = await repo.get_by_feedback_id(feedback_id=100)

        # Assert
        mock_session.execute.assert_called_once()
        mock_result.scalars.assert_called_once()
        mock_scalars.all.assert_called_once()

    async def test_get_by_feedback_id_with_from_date(self) -> None:
        """Test getting history by feedback_id with from_date filter."""
        # Arrange
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = FeedbackStatusChangeHistoryRepository(mock_session)
        from_date = datetime(2026, 1, 1, tzinfo=UTC)

        # Act
        result = await repo.get_by_feedback_id(feedback_id=100, from_date=from_date)

        # Assert
        mock_session.execute.assert_called_once()

    async def test_get_by_feedback_id_with_to_date(self) -> None:
        """Test getting history by feedback_id with to_date filter."""
        # Arrange
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = FeedbackStatusChangeHistoryRepository(mock_session)
        to_date = datetime(2026, 1, 31, tzinfo=UTC)

        # Act
        result = await repo.get_by_feedback_id(feedback_id=100, to_date=to_date)

        # Assert
        mock_session.execute.assert_called_once()

    async def test_get_by_feedback_id_with_both_dates(self) -> None:
        """Test getting history by feedback_id with both date filters."""
        # Arrange
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = FeedbackStatusChangeHistoryRepository(mock_session)
        from_date = datetime(2026, 1, 1, tzinfo=UTC)
        to_date = datetime(2026, 1, 31, tzinfo=UTC)

        # Act
        result = await repo.get_by_feedback_id(feedback_id=100, from_date=from_date, to_date=to_date)

        # Assert
        mock_session.execute.assert_called_once()

    async def test_get_all(self) -> None:
        """Test getting all history without filters."""
        # Arrange
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[MagicMock(spec=FeedbackStatusChangeHistory)])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_result.scalar_one = MagicMock(return_value=1)
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = FeedbackStatusChangeHistoryRepository(mock_session)

        # Act
        _items, total = await repo.get_all()

        # Assert
        assert mock_session.execute.call_count == 2  # count and data queries
        assert total == 1
        mock_result.scalars.assert_called_once()
        mock_scalars.all.assert_called_once()

    async def test_get_all_with_date_filters(self) -> None:
        """Test getting all history with date filters."""
        # Arrange
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_result.scalar_one = MagicMock(return_value=0)
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = FeedbackStatusChangeHistoryRepository(mock_session)
        from_date = datetime(2026, 1, 1, tzinfo=UTC)
        to_date = datetime(2026, 1, 31, tzinfo=UTC)

        # Act
        _items, total = await repo.get_all(from_date=from_date, to_date=to_date, limit=10, offset=5)

        # Assert
        assert mock_session.execute.call_count == 2
        assert total == 0

    async def test_get_all_with_pagination(self) -> None:
        """Test getting all history with pagination."""
        # Arrange
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_result.scalar_one = MagicMock(return_value=0)
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = FeedbackStatusChangeHistoryRepository(mock_session)

        # Act
        _items, total = await repo.get_all(limit=20, offset=10)

        # Assert
        assert mock_session.execute.call_count == 2
        assert total == 0
