"""Unit tests for MeetingStatusChangeHistory repository implementation."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.models.meeting_status_change_history import MeetingStatusChangeHistory
from meeting_service.repositories.implementations.meeting_status_change_history import (
    MeetingStatusChangeHistoryRepository,
)


@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Create a repository instance with mock session."""
    return MeetingStatusChangeHistoryRepository(mock_session)


class TestCreate:
    """Tests for create method (lines 24-28)."""

    @pytest.mark.asyncio
    async def test_create_history_entry(self, mock_session, repository):
        """Test creating a meeting status change history entry."""
        # Arrange
        history_entry = MeetingStatusChangeHistory(
            id=1,
            meeting_id=5,
            user_id=100,
            action="status_changed",
            old_status="SCHEDULED",
            new_status="COMPLETED",
        )

        # Act
        result = await repository.create(history_entry)

        # Assert
        assert result == history_entry
        mock_session.add.assert_called_once_with(history_entry)
        mock_session.flush.assert_called_once()


class TestGetByMeetingId:
    """Tests for get_by_meeting_id method (lines 30-47)."""

    @pytest.mark.asyncio
    async def test_get_by_meeting_id_without_filters(self, mock_session, repository):
        """Test get_by_meeting_id without date filters."""
        # Arrange
        history_entries = [
            MeetingStatusChangeHistory(
                id=1,
                meeting_id=5,
                user_id=100,
                action="status_changed",
                old_status="SCHEDULED",
                new_status="COMPLETED",
                changed_at=datetime(2024, 1, 1, 12, 0),
            ),
            MeetingStatusChangeHistory(
                id=2,
                meeting_id=5,
                user_id=100,
                action="created",
                old_status=None,
                new_status="SCHEDULED",
                changed_at=datetime(2024, 1, 2, 12, 0),
            ),
        ]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = history_entries
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_meeting_id(meeting_id=5)

        # Assert
        assert len(result) == 2
        assert result[0].meeting_id == 5
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_meeting_id_with_from_date(self, mock_session, repository):
        """Test get_by_meeting_id with from_date filter."""
        # Arrange
        history_entries = [
            MeetingStatusChangeHistory(
                id=1,
                meeting_id=5,
                user_id=100,
                action="status_changed",
                old_status="SCHEDULED",
                new_status="COMPLETED",
                changed_at=datetime(2024, 1, 5, 12, 0),
            )
        ]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = history_entries
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, 0, 0)

        # Act
        result = await repository.get_by_meeting_id(meeting_id=5, from_date=from_date)

        # Assert
        assert len(result) == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_meeting_id_with_to_date(self, mock_session, repository):
        """Test get_by_meeting_id with to_date filter."""
        # Arrange
        history_entries = [
            MeetingStatusChangeHistory(
                id=1,
                meeting_id=5,
                user_id=100,
                action="status_changed",
                old_status="SCHEDULED",
                new_status="COMPLETED",
                changed_at=datetime(2024, 1, 1, 12, 0),
            )
        ]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = history_entries
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        to_date = datetime(2024, 1, 31, 23, 59)

        # Act
        result = await repository.get_by_meeting_id(meeting_id=5, to_date=to_date)

        # Assert
        assert len(result) == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_meeting_id_with_both_dates(self, mock_session, repository):
        """Test get_by_meeting_id with both from_date and to_date filters."""
        # Arrange
        history_entries = [
            MeetingStatusChangeHistory(
                id=1,
                meeting_id=5,
                user_id=100,
                action="status_changed",
                old_status="SCHEDULED",
                new_status="COMPLETED",
                changed_at=datetime(2024, 1, 15, 12, 0),
            )
        ]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = history_entries
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, 0, 0)
        to_date = datetime(2024, 1, 31, 23, 59)

        # Act
        result = await repository.get_by_meeting_id(meeting_id=5, from_date=from_date, to_date=to_date)

        # Assert
        assert len(result) == 1
        mock_session.execute.assert_called_once()


class TestGetAll:
    """Tests for get_all method (lines 49-73)."""

    @pytest.mark.asyncio
    async def test_get_all_without_filters(self, mock_session, repository):
        """Test get_all without date filters."""
        # Arrange
        history_entries = [
            MeetingStatusChangeHistory(
                id=1,
                meeting_id=5,
                user_id=100,
                action="status_changed",
                old_status="SCHEDULED",
                new_status="COMPLETED",
                changed_at=datetime(2024, 1, 1, 12, 0),
            ),
            MeetingStatusChangeHistory(
                id=2,
                meeting_id=6,
                user_id=101,
                action="created",
                old_status=None,
                new_status="SCHEDULED",
                changed_at=datetime(2024, 1, 2, 12, 0),
            ),
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 2

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = history_entries
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.get_all()

        # Assert
        assert len(result) == 2
        assert total == 2
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_all_with_from_date(self, mock_session, repository):
        """Test get_all with from_date filter."""
        # Arrange
        history_entries = [
            MeetingStatusChangeHistory(
                id=1,
                meeting_id=5,
                user_id=100,
                action="status_changed",
                old_status="SCHEDULED",
                new_status="COMPLETED",
                changed_at=datetime(2024, 1, 5, 12, 0),
            )
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = history_entries
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        from_date = datetime(2024, 1, 1, 0, 0)

        # Act
        result, total = await repository.get_all(from_date=from_date)

        # Assert
        assert len(result) == 1
        assert total == 1
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_all_with_to_date(self, mock_session, repository):
        """Test get_all with to_date filter."""
        # Arrange
        history_entries = [
            MeetingStatusChangeHistory(
                id=1,
                meeting_id=5,
                user_id=100,
                action="status_changed",
                old_status="SCHEDULED",
                new_status="COMPLETED",
                changed_at=datetime(2024, 1, 1, 12, 0),
            )
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = history_entries
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        to_date = datetime(2024, 1, 31, 23, 59)

        # Act
        result, total = await repository.get_all(to_date=to_date)

        # Assert
        assert len(result) == 1
        assert total == 1
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_all_with_both_dates(self, mock_session, repository):
        """Test get_all with both from_date and to_date filters."""
        # Arrange
        history_entries = [
            MeetingStatusChangeHistory(
                id=1,
                meeting_id=5,
                user_id=100,
                action="status_changed",
                old_status="SCHEDULED",
                new_status="COMPLETED",
                changed_at=datetime(2024, 1, 15, 12, 0),
            )
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = history_entries
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        from_date = datetime(2024, 1, 1, 0, 0)
        to_date = datetime(2024, 1, 31, 23, 59)

        # Act
        result, total = await repository.get_all(from_date=from_date, to_date=to_date)

        # Assert
        assert len(result) == 1
        assert total == 1
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, mock_session, repository):
        """Test get_all with pagination."""
        # Arrange
        history_entries = []

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 50

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = history_entries
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.get_all(offset=10, limit=5)

        # Assert
        assert len(result) == 0
        assert total == 50
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_all_custom_limit_offset(self, mock_session, repository):
        """Test get_all with custom limit and offset."""
        # Arrange
        history_entries = [
            MeetingStatusChangeHistory(
                id=1,
                meeting_id=5,
                user_id=100,
                action="status_changed",
                old_status="SCHEDULED",
                new_status="COMPLETED",
                changed_at=datetime(2024, 1, 1, 12, 0),
            )
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = history_entries
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.get_all(limit=25, offset=5)

        # Assert
        assert len(result) == 1
        assert total == 1
        assert mock_session.execute.call_count == 2
