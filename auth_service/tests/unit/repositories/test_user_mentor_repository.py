"""Unit tests for UserMentor repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from auth_service.models import UserMentor
from auth_service.repositories.implementations.user_mentor import UserMentorRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TestUserMentorRepository:
    """Tests for UserMentorRepository implementation."""

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
    def sample_user_mentor(self):
        """Create a sample user-mentor relation."""
        return UserMentor(
            id=1,
            user_id=1,
            mentor_id=2,
            is_active=True,
            created_at=datetime.now(UTC),
        )

    @pytest.fixture
    def second_user_mentor(self):
        """Create a second user-mentor relation."""
        return UserMentor(
            id=2,
            user_id=1,
            mentor_id=3,
            is_active=False,
            created_at=datetime.now(UTC),
        )

    async def test_get_by_user_id(self, mock_session, mock_result, sample_user_mentor, second_user_mentor):
        """Test getting all mentor relations for a user."""
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_user_mentor, second_user_mentor]
        mock_result.scalars.return_value = scalars_mock
        mock_session.execute.return_value = mock_result

        repo = UserMentorRepository(mock_session)
        result = await repo.get_by_user_id(1)

        assert len(result) == 2
        assert result[0].user_id == 1
        assert result[1].user_id == 1

    async def test_get_by_mentor_id(self, mock_session, mock_result, sample_user_mentor):
        """Test getting all mentee relations for a mentor."""
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_user_mentor]
        mock_result.scalars.return_value = scalars_mock
        mock_session.execute.return_value = mock_result

        repo = UserMentorRepository(mock_session)
        result = await repo.get_by_mentor_id(2)

        assert len(result) == 1
        assert result[0].mentor_id == 2

    async def test_get_active_by_user_id_found(self, mock_session, mock_result, sample_user_mentor):
        """Test getting active mentor relation for a user when found."""
        mock_result.scalar_one_or_none.return_value = sample_user_mentor
        mock_session.execute.return_value = mock_result

        repo = UserMentorRepository(mock_session)
        result = await repo.get_active_by_user_id(1)

        assert result == sample_user_mentor
        assert result.is_active is True

    async def test_get_active_by_user_id_not_found(self, mock_session, mock_result):
        """Test getting active mentor relation when none exists."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserMentorRepository(mock_session)
        result = await repo.get_active_by_user_id(999)

        assert result is None

    async def test_get_by_user_and_mentor_found(self, mock_session, mock_result, sample_user_mentor):
        """Test getting relation by user and mentor IDs when found."""
        mock_result.scalar_one_or_none.return_value = sample_user_mentor
        mock_session.execute.return_value = mock_result

        repo = UserMentorRepository(mock_session)
        result = await repo.get_by_user_and_mentor(1, 2)

        assert result == sample_user_mentor
        assert result.user_id == 1
        assert result.mentor_id == 2

    async def test_get_by_user_and_mentor_not_found(self, mock_session, mock_result):
        """Test getting relation by user and mentor IDs when not found."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserMentorRepository(mock_session)
        result = await repo.get_by_user_and_mentor(1, 999)

        assert result is None

    async def test_get_by_user_id_empty(self, mock_session, mock_result):
        """Test getting mentor relations for user with none."""
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        mock_result.scalars.return_value = scalars_mock
        mock_session.execute.return_value = mock_result

        repo = UserMentorRepository(mock_session)
        result = await repo.get_by_user_id(999)

        assert result == []

    async def test_get_by_mentor_id_empty(self, mock_session, mock_result):
        """Test getting mentee relations for mentor with none."""
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        mock_result.scalars.return_value = scalars_mock
        mock_session.execute.return_value = mock_result

        repo = UserMentorRepository(mock_session)
        result = await repo.get_by_mentor_id(999)

        assert result == []

    async def test_inherits_base_repository(self, mock_session, mock_result, sample_user_mentor):
        """Test that UserMentorRepository inherits base repository methods."""
        mock_result.scalar_one_or_none.return_value = sample_user_mentor
        mock_session.execute.return_value = mock_result

        repo = UserMentorRepository(mock_session)

        # Test get_by_id from base repository
        result = await repo.get_by_id(1)
        assert result == sample_user_mentor

    async def test_create_inherited(self, mock_session, sample_user_mentor):
        """Test that create method from base repository works."""
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        repo = UserMentorRepository(mock_session)
        result = await repo.create(sample_user_mentor)

        mock_session.add.assert_called_once_with(sample_user_mentor)
        mock_session.flush.assert_awaited_once()

    async def test_delete_inherited(self, mock_session, mock_result, sample_user_mentor):
        """Test that delete method from base repository works."""
        mock_result.scalar_one_or_none.return_value = sample_user_mentor
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()

        repo = UserMentorRepository(mock_session)
        result = await repo.delete(1)

        assert result is True
        mock_session.delete.assert_awaited_once_with(sample_user_mentor)
