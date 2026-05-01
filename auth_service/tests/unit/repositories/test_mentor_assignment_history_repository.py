"""Unit tests for Mentor Assignment History repository implementation."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import MentorAssignmentHistory
from auth_service.repositories.implementations.mentor_assignment_history import MentorAssignmentHistoryRepository


class TestMentorAssignmentHistoryRepository:
    """Tests for MentorAssignmentHistoryRepository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_result(self):
        """Create a mock SQLAlchemy result."""
        result = MagicMock()
        result.scalars = MagicMock()
        result.scalars.return_value.all = MagicMock(return_value=[])
        result.scalar_one = MagicMock(return_value=0)
        return result

    @pytest.fixture
    def sample_mentor_assignment_history(self):
        """Create a sample mentor assignment history entry."""
        return MentorAssignmentHistory(
            id=1,
            user_id=1,
            mentor_id=2,
            action="assigned",
            changed_at=datetime.now(UTC),
            changed_by=1,
        )

    async def test_create_returns_entity(self, mock_session, sample_mentor_assignment_history):
        """Test create method returns the entity after flush."""
        mock_session.execute.return_value = None

        repo = MentorAssignmentHistoryRepository(mock_session)
        result = await repo.create(sample_mentor_assignment_history)

        mock_session.add.assert_called_once_with(sample_mentor_assignment_history)
        mock_session.flush.assert_awaited_once()
        assert result == sample_mentor_assignment_history

    async def test_get_by_user_id_with_date_filters(self, mock_session, mock_result, sample_mentor_assignment_history):
        """Test get_by_user_id with from_date and to_date filters."""
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        mock_result.scalars.return_value.all.return_value = [sample_mentor_assignment_history]
        mock_session.execute.return_value = mock_result

        repo = MentorAssignmentHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1, from_date=from_date, to_date=to_date)

        assert mock_session.execute.call_count == 1
        assert len(result) == 1
        assert result[0] == sample_mentor_assignment_history

    async def test_get_by_user_id_with_from_date_only(self, mock_session, mock_result, sample_mentor_assignment_history):
        """Test get_by_user_id with from_date filter only."""
        from_date = datetime.now(UTC) - timedelta(days=7)
        mock_result.scalars.return_value.all.return_value = [sample_mentor_assignment_history]
        mock_session.execute.return_value = mock_result

        repo = MentorAssignmentHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1, from_date=from_date)

        assert mock_session.execute.call_count == 1
        assert len(result) == 1

    async def test_get_by_user_id_with_to_date_only(self, mock_session, mock_result, sample_mentor_assignment_history):
        """Test get_by_user_id with to_date filter only."""
        to_date = datetime.now(UTC)
        mock_result.scalars.return_value.all.return_value = [sample_mentor_assignment_history]
        mock_session.execute.return_value = mock_result

        repo = MentorAssignmentHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1, to_date=to_date)

        assert mock_session.execute.call_count == 1
        assert len(result) == 1

    async def test_get_all_with_date_filters(self, mock_session, mock_result, sample_mentor_assignment_history):
        """Test get_all with from_date and to_date filters."""
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        mock_result.scalars.return_value.all.return_value = [sample_mentor_assignment_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = MentorAssignmentHistoryRepository(mock_session)
        result, total = await repo.get_all(from_date=from_date, to_date=to_date)

        assert mock_session.execute.call_count == 2
        assert len(result) == 1
        assert total == 1

    async def test_get_all_with_from_date_only(self, mock_session, mock_result, sample_mentor_assignment_history):
        """Test get_all with from_date filter only."""
        from_date = datetime.now(UTC) - timedelta(days=7)
        mock_result.scalars.return_value.all.return_value = [sample_mentor_assignment_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = MentorAssignmentHistoryRepository(mock_session)
        result, total = await repo.get_all(from_date=from_date)

        assert mock_session.execute.call_count == 2
        assert len(result) == 1
        assert total == 1

    async def test_get_all_with_to_date_only(self, mock_session, mock_result, sample_mentor_assignment_history):
        """Test get_all with to_date filter only."""
        to_date = datetime.now(UTC)
        mock_result.scalars.return_value.all.return_value = [sample_mentor_assignment_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = MentorAssignmentHistoryRepository(mock_session)
        result, total = await repo.get_all(to_date=to_date)

        assert mock_session.execute.call_count == 2
        assert len(result) == 1
        assert total == 1

    async def test_get_all_with_pagination(self, mock_session, mock_result, sample_mentor_assignment_history):
        """Test get_all with pagination parameters."""
        mock_result.scalars.return_value.all.return_value = [sample_mentor_assignment_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = MentorAssignmentHistoryRepository(mock_session)
        result, total = await repo.get_all(limit=10, offset=5)

        assert mock_session.execute.call_count == 2
        assert len(result) == 1
        assert total == 1
