"""Unit tests for Meeting repository implementation."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from meeting_service.core.enums import EmployeeLevel, MeetingType
from meeting_service.models.meeting import Meeting
from meeting_service.repositories.implementations.meeting import MeetingRepository
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = MagicMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Create a repository instance with mock session."""
    return MeetingRepository(mock_session)


class TestFindMeetings:
    """Tests for find_meetings method (lines 35-69)."""

    async def test_find_meetings_with_no_filters(self, mock_session, repository):
        """Test find_meetings without any filters."""
        # Arrange
        meetings = [
            Meeting(id=1, title="Meeting 1", type=MeetingType.HR),
            Meeting(id=2, title="Meeting 2", type=MeetingType.SECURITY),
        ]

        # First call for count, second for results
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 2

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = meetings
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.find_meetings(skip=0, limit=10)

        # Assert
        assert len(result) == 2
        assert total == 2
        assert mock_session.execute.call_count == 2

    async def test_find_meetings_with_meeting_type_filter(self, mock_session, repository):
        """Test find_meetings with meeting_type filter."""
        # Arrange
        meetings = [Meeting(id=1, title="HR Meeting", type=MeetingType.HR)]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = meetings
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.find_meetings(skip=0, limit=10, meeting_type=MeetingType.HR)

        # Assert
        assert len(result) == 1
        assert result[0].type == MeetingType.HR
        assert total == 1

    async def test_find_meetings_with_department_id_filter(self, mock_session, repository):
        """Test find_meetings with department_id filter."""
        # Arrange
        meetings = [Meeting(id=1, title="Dept Meeting", type=MeetingType.HR, department_id=5)]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = meetings
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, _total = await repository.find_meetings(skip=0, limit=10, department_id=5)

        # Assert
        assert len(result) == 1
        assert result[0].department_id == 5

    async def test_find_meetings_with_position_filter(self, mock_session, repository):
        """Test find_meetings with position filter."""
        # Arrange
        meetings = [Meeting(id=1, title="Dev Meeting", type=MeetingType.HR, position="Developer")]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = meetings
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, _total = await repository.find_meetings(skip=0, limit=10, position="Developer")

        # Assert
        assert len(result) == 1
        assert result[0].position == "Developer"

    async def test_find_meetings_with_level_filter(self, mock_session, repository):
        """Test find_meetings with level filter."""
        # Arrange
        meetings = [Meeting(id=1, title="Junior Meeting", type=MeetingType.HR, level=EmployeeLevel.JUNIOR)]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = meetings
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, _total = await repository.find_meetings(skip=0, limit=10, level=EmployeeLevel.JUNIOR)

        # Assert
        assert len(result) == 1
        assert result[0].level == EmployeeLevel.JUNIOR

    async def test_find_meetings_with_is_mandatory_filter(self, mock_session, repository):
        """Test find_meetings with is_mandatory filter."""
        # Arrange
        meetings = [
            Meeting(id=1, title="Mandatory Meeting", type=MeetingType.HR, is_mandatory=True),
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = meetings
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, _total = await repository.find_meetings(skip=0, limit=10, is_mandatory=True)

        # Assert
        assert len(result) == 1
        assert result[0].is_mandatory is True

    async def test_find_meetings_with_search(self, mock_session, repository):
        """Test find_meetings with search filter."""
        # Arrange
        meetings = [
            Meeting(id=1, title="Security Training", description="Important security info", type=MeetingType.SECURITY)
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = meetings
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.find_meetings(skip=0, limit=10, search="security")

        # Assert
        assert len(result) == 1
        assert total == 1

    async def test_find_meetings_with_all_filters(self, mock_session, repository):
        """Test find_meetings with all filters combined."""
        # Arrange
        meetings = [
            Meeting(
                id=1,
                title="HR Onboarding",
                type=MeetingType.HR,
                department_id=1,
                position="Developer",
                level=EmployeeLevel.JUNIOR,
                is_mandatory=True,
            ),
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = meetings
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, _total = await repository.find_meetings(
            skip=0,
            limit=10,
            meeting_type=MeetingType.HR,
            department_id=1,
            position="Developer",
            level=EmployeeLevel.JUNIOR,
            is_mandatory=True,
        )

        # Assert
        assert len(result) == 1
        assert mock_session.execute.call_count == 2

    async def test_find_meetings_pagination(self, mock_session, repository):
        """Test find_meetings with pagination."""
        # Arrange
        meetings = []

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 100  # Total count

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = meetings
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act
        result, total = await repository.find_meetings(skip=20, limit=10)

        # Assert
        assert len(result) == 0
        assert total == 100

    async def test_find_meetings_with_desc_sort_order(self, mock_session, repository):
        """Test find_meetings with descending sort order (line 89 coverage)."""
        # Arrange
        meetings = [
            Meeting(id=2, title="Meeting 2", type=MeetingType.SECURITY),
            Meeting(id=1, title="Meeting 1", type=MeetingType.HR),
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 2

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = meetings
        mock_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        # Act - use descending sort order
        result, total = await repository.find_meetings(skip=0, limit=10, sort_by="title", sort_order="desc")

        # Assert
        assert len(result) == 2
        assert total == 2
        assert mock_session.execute.call_count == 2
