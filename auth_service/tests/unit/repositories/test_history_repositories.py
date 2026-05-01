"""Unit tests for history repositories to achieve 100% coverage."""

import pytest

pytestmark = pytest.mark.usefixtures("mock_uow")  # Use our own mock, not the autouse override

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from auth_service.core.enums import UserRole
from auth_service.models import (
    InvitationStatusHistory,
    LoginHistory,
    MentorAssignmentHistory,
    PasswordChangeHistory,
    RoleChangeHistory,
)
from auth_service.repositories.implementations.invitation_status_history import InvitationStatusHistoryRepository
from auth_service.repositories.implementations.login_history import LoginHistoryRepository
from auth_service.repositories.implementations.mentor_assignment_history import MentorAssignmentHistoryRepository
from auth_service.repositories.implementations.password_change_history import PasswordChangeHistoryRepository
from auth_service.repositories.implementations.role_change_history import RoleChangeHistoryRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TestLoginHistoryRepository:
    """Tests for LoginHistoryRepository."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_result(self):
        result = MagicMock()
        result.scalars = MagicMock()
        result.scalars.return_value.all = MagicMock(return_value=[])
        result.scalar_one = MagicMock(return_value=0)
        return result

    @pytest.fixture
    def sample_history(self):
        return LoginHistory(id=1, user_id=1, login_at=datetime.now(UTC), ip_address="1.1.1.1", user_agent="test")

    async def test_create(self, mock_session, sample_history):
        repo = LoginHistoryRepository(mock_session)
        result = await repo.create(sample_history)
        mock_session.add.assert_called_once_with(sample_history)
        mock_session.flush.assert_awaited_once()
        assert result == sample_history

    async def test_get_by_user_id_with_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = LoginHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        result = await repo.get_by_user_id(1, from_date=from_date, to_date=to_date)
        assert len(result) == 1
        assert result[0] == sample_history
        mock_session.execute.assert_awaited_once()

    async def test_get_by_user_id_no_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = LoginHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1)
        assert len(result) == 1
        assert result[0] == sample_history
        mock_session.execute.assert_awaited_once()

    async def test_get_all_with_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result
        repo = LoginHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        _result, total = await repo.get_all(from_date=from_date, to_date=to_date)
        assert total == 1

    async def test_get_all_no_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result
        repo = LoginHistoryRepository(mock_session)
        result, total = await repo.get_all()
        assert total == 1
        assert len(result) == 1
        assert result[0] == sample_history
        assert mock_session.execute.call_count == 2


class TestPasswordChangeHistoryRepository:
    """Tests for PasswordChangeHistoryRepository."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_result(self):
        result = MagicMock()
        result.scalars = MagicMock()
        result.scalars.return_value.all = MagicMock(return_value=[])
        result.scalar_one = MagicMock(return_value=0)
        return result

    @pytest.fixture
    def sample_history(self):
        return PasswordChangeHistory(id=1, user_id=1, changed_at=datetime.now(UTC), changed_by=1)

    async def test_create(self, mock_session, sample_history):
        repo = PasswordChangeHistoryRepository(mock_session)
        result = await repo.create(sample_history)
        mock_session.add.assert_called_once_with(sample_history)
        mock_session.flush.assert_awaited_once()
        assert result == sample_history

    async def test_get_by_user_id_with_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = PasswordChangeHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        result = await repo.get_by_user_id(1, from_date=from_date, to_date=to_date)
        assert len(result) == 1

    async def test_get_by_user_id_no_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = PasswordChangeHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1)
        assert len(result) == 1

    async def test_get_all_with_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result
        repo = PasswordChangeHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        _result, total = await repo.get_all(from_date=from_date, to_date=to_date)
        assert total == 1

    async def test_get_all_no_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result
        repo = PasswordChangeHistoryRepository(mock_session)
        result, total = await repo.get_all()
        assert total == 1
        assert len(result) == 1
        assert result[0] == sample_history
        assert mock_session.execute.call_count == 2


class TestRoleChangeHistoryRepository:
    """Tests for RoleChangeHistoryRepository."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_result(self):
        result = MagicMock()
        result.scalars = MagicMock()
        result.scalars.return_value.all = MagicMock(return_value=[])
        result.scalar_one = MagicMock(return_value=0)
        return result

    @pytest.fixture
    def sample_history(self):
        return RoleChangeHistory(
            id=1,
            user_id=1,
            old_role=UserRole.NEWBIE,
            new_role=UserRole.MENTOR,
            changed_at=datetime.now(UTC),
            changed_by=1,
        )

    async def test_create(self, mock_session, sample_history):
        repo = RoleChangeHistoryRepository(mock_session)
        result = await repo.create(sample_history)
        assert result == sample_history

    async def test_get_by_user_id_with_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = RoleChangeHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        result = await repo.get_by_user_id(1, from_date=from_date, to_date=to_date)
        assert len(result) == 1

    async def test_get_by_user_id_no_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = RoleChangeHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1)
        assert len(result) == 1

    async def test_get_all_with_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result
        repo = RoleChangeHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        _result, total = await repo.get_all(from_date=from_date, to_date=to_date)
        assert total == 1

    async def test_get_all_no_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result
        repo = RoleChangeHistoryRepository(mock_session)
        _result, total = await repo.get_all()
        assert total == 1


class TestMentorAssignmentHistoryRepository:
    """Tests for MentorAssignmentHistoryRepository."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_result(self):
        result = MagicMock()
        result.scalars = MagicMock()
        result.scalars.return_value.all = MagicMock(return_value=[])
        result.scalar_one = MagicMock(return_value=0)
        return result

    @pytest.fixture
    def sample_history(self):
        return MentorAssignmentHistory(
            id=1,
            user_id=1,
            mentor_id=2,
            action="assigned",
            changed_at=datetime.now(UTC),
            changed_by=1,
        )

    async def test_create(self, mock_session, sample_history):
        repo = MentorAssignmentHistoryRepository(mock_session)
        result = await repo.create(sample_history)
        assert result == sample_history

    async def test_get_by_user_id_with_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = MentorAssignmentHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        result = await repo.get_by_user_id(1, from_date=from_date, to_date=to_date)
        assert len(result) == 1

    async def test_get_by_user_id_no_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = MentorAssignmentHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1)
        assert len(result) == 1

    async def test_get_all_with_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result
        repo = MentorAssignmentHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        _result, total = await repo.get_all(from_date=from_date, to_date=to_date)
        assert total == 1

    async def test_get_all_no_dates(self, mock_session, mock_result, sample_history):
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result
        repo = MentorAssignmentHistoryRepository(mock_session)
        _result, total = await repo.get_all()
        assert total == 1

    async def test_get_by_mentor_id_with_dates(self, mock_session, mock_result, sample_history):
        """Test get_by_mentor_id with date filtering (covers lines 57-66)."""
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = MentorAssignmentHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        result = await repo.get_by_mentor_id(2, from_date=from_date, to_date=to_date)
        assert len(result) == 1
        assert result[0] == sample_history

    async def test_get_by_mentor_id_no_dates(self, mock_session, mock_result, sample_history):
        """Test get_by_mentor_id without date filtering."""
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = MentorAssignmentHistoryRepository(mock_session)
        result = await repo.get_by_mentor_id(2)
        assert len(result) == 1
        assert result[0] == sample_history


class TestInvitationStatusHistoryRepository:
    """Tests for InvitationStatusHistoryRepository (covers lines 26-28, 38-47, 58-73)."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_result(self):
        result = MagicMock()
        result.scalars = MagicMock()
        result.scalars.return_value.all = MagicMock(return_value=[])
        result.scalar_one = MagicMock(return_value=0)
        return result

    @pytest.fixture
    def sample_history(self):
        return InvitationStatusHistory(
            id=1,
            invitation_id=10,
            old_status="PENDING",
            new_status="ACCEPTED",
            changed_at=datetime.now(UTC),
            changed_by=1,
            metadata={"auto_created": True},
        )

    async def test_create(self, mock_session, sample_history):
        """Test create method (covers lines 26-28)."""
        repo = InvitationStatusHistoryRepository(mock_session)
        result = await repo.create(sample_history)
        mock_session.add.assert_called_once_with(sample_history)
        mock_session.flush.assert_awaited_once()
        assert result == sample_history

    async def test_get_by_invitation_id_with_dates(self, mock_session, mock_result, sample_history):
        """Test get_by_invitation_id with date filtering (covers lines 38-47)."""
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = InvitationStatusHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        result = await repo.get_by_invitation_id(10, from_date=from_date, to_date=to_date)
        assert len(result) == 1
        assert result[0] == sample_history
        mock_session.execute.assert_awaited_once()

    async def test_get_by_invitation_id_no_dates(self, mock_session, mock_result, sample_history):
        """Test get_by_invitation_id without date filtering."""
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result
        repo = InvitationStatusHistoryRepository(mock_session)
        result = await repo.get_by_invitation_id(10)
        assert len(result) == 1
        assert result[0] == sample_history

    async def test_get_all_with_dates(self, mock_session, mock_result, sample_history):
        """Test get_all with date filtering (covers lines 58-73)."""
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result
        repo = InvitationStatusHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(days=7)
        to_date = datetime.now(UTC)
        result, total = await repo.get_all(from_date=from_date, to_date=to_date)
        assert total == 1
        assert len(result) == 1
        assert mock_session.execute.call_count == 2

    async def test_get_all_no_dates(self, mock_session, mock_result, sample_history):
        """Test get_all without date filtering."""
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result
        repo = InvitationStatusHistoryRepository(mock_session)
        result, total = await repo.get_all()
        assert total == 1
        assert len(result) == 1
        assert result[0] == sample_history
        assert mock_session.execute.call_count == 2
