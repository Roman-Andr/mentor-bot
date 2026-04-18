"""Unit tests for UserMeeting repository implementation."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.core.enums import MeetingStatus
from meeting_service.models.user_meeting import UserMeeting
from meeting_service.repositories.implementations.user_meeting import UserMeetingRepository


@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Create a repository instance with mock session."""
    return UserMeetingRepository(mock_session)


class TestFindByUser:
    """Tests for find_by_user method (lines 31-45)."""

    async def test_find_by_user_without_status(self, mock_session, repository):
        """Test find_by_user without status filter."""
        # Arrange
        assignments = [
            UserMeeting(id=1, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED),
            UserMeeting(id=2, user_id=100, meeting_id=2, status=MeetingStatus.COMPLETED),
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 2

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = assignments
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.find_by_user(user_id=100, skip=0, limit=10)

        # Assert
        assert len(result) == 2
        assert total == 2
        assert mock_session.execute.call_count == 2

    async def test_find_by_user_with_status_filter(self, mock_session, repository):
        """Test find_by_user with status filter."""
        # Arrange
        assignments = [UserMeeting(id=1, user_id=100, meeting_id=1, status=MeetingStatus.COMPLETED)]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = assignments
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.find_by_user(user_id=100, skip=0, limit=10, status=MeetingStatus.COMPLETED)

        # Assert
        assert len(result) == 1
        assert result[0].status == MeetingStatus.COMPLETED

    async def test_find_by_user_pagination(self, mock_session, repository):
        """Test find_by_user with pagination."""
        # Arrange
        assignments = []

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 50

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = assignments
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.find_by_user(user_id=100, skip=10, limit=5)

        # Assert
        assert len(result) == 0
        assert total == 50


class TestFindByMeeting:
    """Tests for find_by_meeting method (lines 56-70)."""

    async def test_find_by_meeting_without_status(self, mock_session, repository):
        """Test find_by_meeting without status filter."""
        # Arrange
        assignments = [
            UserMeeting(id=1, user_id=100, meeting_id=5, status=MeetingStatus.SCHEDULED),
            UserMeeting(id=2, user_id=101, meeting_id=5, status=MeetingStatus.COMPLETED),
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 2

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = assignments
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.find_by_meeting(meeting_id=5, skip=0, limit=10)

        # Assert
        assert len(result) == 2
        assert total == 2

    async def test_find_by_meeting_with_status_filter(self, mock_session, repository):
        """Test find_by_meeting with status filter."""
        # Arrange
        assignments = [UserMeeting(id=1, user_id=100, meeting_id=5, status=MeetingStatus.SCHEDULED)]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = assignments
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.find_by_meeting(meeting_id=5, skip=0, limit=10, status=MeetingStatus.SCHEDULED)

        # Assert
        assert len(result) == 1
        assert result[0].status == MeetingStatus.SCHEDULED


class TestGetUserMeeting:
    """Tests for get_user_meeting method (lines 72-81)."""

    async def test_get_user_meeting_returns_assignment(self, mock_session, repository):
        """Test get_user_meeting returns assignment when found."""
        # Arrange
        assignment = UserMeeting(id=1, user_id=100, meeting_id=5, status=MeetingStatus.SCHEDULED)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = assignment
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_user_meeting(user_id=100, meeting_id=5)

        # Assert
        assert result == assignment
        assert result.user_id == 100
        assert result.meeting_id == 5
        mock_session.execute.assert_called_once()

        # Verify query contains both user_id and meeting_id
        call_args = mock_session.execute.call_args[0][0]
        query_str = str(call_args)
        assert "user_id" in query_str.lower()
        assert "meeting_id" in query_str.lower()

    async def test_get_user_meeting_returns_none_when_not_found(self, mock_session, repository):
        """Test get_user_meeting returns None when assignment not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_user_meeting(user_id=999, meeting_id=999)

        # Assert
        assert result is None

    async def test_get_user_meeting_wrong_user(self, mock_session, repository):
        """Test get_user_meeting returns None for wrong user."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_user_meeting(user_id=100, meeting_id=5)

        # Assert
        assert result is None
