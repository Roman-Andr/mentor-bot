"""Unit tests for Invitation repository implementation."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.enums import EmployeeLevel, InvitationStatus, UserRole
from auth_service.models import Department, Invitation
from auth_service.repositories.implementations.invitation import InvitationRepository


class TestInvitationRepository:
    """Tests for InvitationRepository implementation."""

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
        result.scalar_one = MagicMock()
        result.scalars = MagicMock()
        result.all = MagicMock()
        return result

    @pytest.fixture
    def sample_department(self):
        """Create a sample department."""
        return Department(
            id=1,
            name="Engineering",
            description="Eng Dept",
            created_at=datetime.now(UTC),
        )

    @pytest.fixture
    def sample_invitation(self, sample_department):
        """Create a sample invitation."""
        return Invitation(
            id=1,
            token="invite-token-123",
            email="newuser@example.com",
            employee_id="EMP005",
            first_name="New",
            last_name="User",
            department_id=1,
            position="Developer",
            level=EmployeeLevel.MIDDLE,
            role=UserRole.NEWBIE,
            status=InvitationStatus.PENDING,
            expires_at=datetime.now(UTC) + timedelta(days=7),
            created_at=datetime.now(UTC),
        )

    @pytest.fixture
    def expired_invitation(self, sample_department):
        """Create an expired invitation."""
        return Invitation(
            id=2,
            token="expired-token",
            email="expired@example.com",
            employee_id="EMP006",
            first_name="Expired",
            last_name="User",
            department_id=1,
            position="Developer",
            level=EmployeeLevel.JUNIOR,
            role=UserRole.NEWBIE,
            status=InvitationStatus.PENDING,
            expires_at=datetime.now(UTC) - timedelta(days=1),
            created_at=datetime.now(UTC),
        )

    async def test_get_by_id_with_department(self, mock_session, mock_result, sample_invitation):
        """Test getting invitation by ID with department loaded."""
        mock_result.scalar_one_or_none.return_value = sample_invitation
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)
        result = await repo.get_by_id(1)

        assert result == sample_invitation

    async def test_get_by_token_success(self, mock_session, mock_result, sample_invitation):
        """Test getting invitation by token."""
        mock_result.scalar_one_or_none.return_value = sample_invitation
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)
        result = await repo.get_by_token("invite-token-123")

        assert result == sample_invitation
        assert result.token == "invite-token-123"

    async def test_get_by_token_not_found(self, mock_session, mock_result):
        """Test getting invitation by token when not found."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)
        result = await repo.get_by_token("nonexistent-token")

        assert result is None

    async def test_get_valid_by_token_success(self, mock_session, mock_result, sample_invitation):
        """Test getting valid invitation by token."""
        mock_result.scalar_one_or_none.return_value = sample_invitation
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)
        result = await repo.get_valid_by_token("invite-token-123")

        assert result == sample_invitation
        assert result.status == InvitationStatus.PENDING

    async def test_get_valid_by_token_expired(self, mock_session, mock_result, expired_invitation):
        """Test getting expired invitation returns None."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)
        result = await repo.get_valid_by_token("expired-token")

        assert result is None

    async def test_get_by_email(self, mock_session, mock_result, sample_invitation):
        """Test getting invitations by email."""
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_invitation]
        mock_result.scalars.return_value = scalars_mock
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)
        result = await repo.get_by_email("newuser@example.com")

        assert len(result) == 1
        assert result[0].email == "newuser@example.com"

    async def test_get_by_email_empty(self, mock_session, mock_result):
        """Test getting invitations by email when none exist."""
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        mock_result.scalars.return_value = scalars_mock
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)
        result = await repo.get_by_email("no-invites@example.com")

        assert result == []

    async def test_find_invitations_without_filters(self, mock_session, mock_result, sample_invitation):
        """Test finding invitations without filters."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_invitation]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = InvitationRepository(mock_session)
        invitations, total = await repo.find_invitations(skip=0, limit=100)

        assert total == 1
        assert len(invitations) == 1

    async def test_find_invitations_with_email_filter(self, mock_session, mock_result, sample_invitation):
        """Test finding invitations with email filter."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_invitation]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = InvitationRepository(mock_session)
        invitations, total = await repo.find_invitations(skip=0, limit=100, email="newuser")

        assert total == 1
        assert len(invitations) == 1

    async def test_find_invitations_with_role_filter(self, mock_session, mock_result, sample_invitation):
        """Test finding invitations with role filter."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_invitation]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = InvitationRepository(mock_session)
        invitations, total = await repo.find_invitations(skip=0, limit=100, role=UserRole.NEWBIE)

        assert total == 1

    async def test_find_invitations_with_status_filter(self, mock_session, mock_result, sample_invitation):
        """Test finding invitations with status filter."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_invitation]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = InvitationRepository(mock_session)
        invitations, total = await repo.find_invitations(skip=0, limit=100, status=InvitationStatus.PENDING)

        assert total == 1

    async def test_find_invitations_with_department_filter(self, mock_session, mock_result, sample_invitation):
        """Test finding invitations with department filter."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_invitation]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = InvitationRepository(mock_session)
        invitations, total = await repo.find_invitations(skip=0, limit=100, department_id=1)

        assert total == 1

    async def test_find_invitations_expired_only(self, mock_session, mock_result, expired_invitation):
        """Test finding only expired invitations."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [expired_invitation]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = InvitationRepository(mock_session)
        invitations, total = await repo.find_invitations(skip=0, limit=100, expired_only=True)

        assert total == 1

    async def test_create_reloads_with_department(self, mock_session, mock_result, sample_invitation):
        """Test that create reloads invitation with department."""
        mock_result.scalar_one_or_none.return_value = sample_invitation
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()

        repo = InvitationRepository(mock_session)
        result = await repo.create(sample_invitation)

        mock_session.add.assert_called_once_with(sample_invitation)
        mock_session.flush.assert_awaited_once()
        assert result == sample_invitation

    async def test_mark_as_used_success(self, mock_session, mock_result, sample_invitation):
        """Test marking invitation as used."""
        mock_result.scalar_one_or_none.return_value = sample_invitation
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()

        repo = InvitationRepository(mock_session)
        result = await repo.mark_as_used(1, 10)

        assert result.status == InvitationStatus.USED
        assert result.user_id == 10
        assert result.used_at is not None
        mock_session.flush.assert_awaited_once()

    async def test_mark_as_used_not_found(self, mock_session, mock_result):
        """Test marking non-existent invitation as used."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)

        with pytest.raises(ValueError, match="Invitation with ID 999 not found"):
            await repo.mark_as_used(999, 10)

    async def test_mark_as_used_not_pending(self, mock_session, mock_result, sample_invitation):
        """Test marking already used invitation as used."""
        sample_invitation.status = InvitationStatus.USED
        mock_result.scalar_one_or_none.return_value = sample_invitation
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)

        with pytest.raises(ValueError, match="Invitation is not pending"):
            await repo.mark_as_used(1, 10)

    async def test_mark_as_used_expired(self, mock_session, mock_result, expired_invitation):
        """Test marking expired invitation as used."""
        mock_result.scalar_one_or_none.return_value = expired_invitation
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)

        with pytest.raises(ValueError, match="Invitation has expired"):
            await repo.mark_as_used(2, 10)

    async def test_update_status_success(self, mock_session, mock_result, sample_invitation):
        """Test updating invitation status."""
        mock_result.scalar_one_or_none.return_value = sample_invitation
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()

        repo = InvitationRepository(mock_session)
        result = await repo.update_status(1, InvitationStatus.REVOKED)

        assert result.status == InvitationStatus.REVOKED
        mock_session.flush.assert_awaited_once()

    async def test_update_status_not_found(self, mock_session, mock_result):
        """Test updating status of non-existent invitation."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = InvitationRepository(mock_session)

        with pytest.raises(ValueError, match="Invitation with ID 999 not found"):
            await repo.update_status(999, InvitationStatus.REVOKED)

    async def test_get_statistics(self, mock_session, mock_result):
        """Test getting invitation statistics."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 10

        status_result = MagicMock()
        status_result.all.return_value = [
            (InvitationStatus.PENDING, 5),
            (InvitationStatus.USED, 3),
            (InvitationStatus.REVOKED, 2),
        ]

        expired_result = MagicMock()
        expired_result.scalar_one.return_value = 1

        recent_result = MagicMock()
        recent_result.all.return_value = []

        mock_session.execute.side_effect = [count_result, status_result, expired_result, recent_result]

        repo = InvitationRepository(mock_session)
        stats = await repo.get_statistics()

        assert stats.total == 10
        assert stats.pending == 5
        assert stats.used == 3
        assert stats.revoked == 2
        assert stats.expired == 1

    async def test_get_statistics_zero_total(self, mock_session, mock_result):
        """Test statistics when there are no invitations."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        status_result = MagicMock()
        status_result.all.return_value = []

        expired_result = MagicMock()
        expired_result.scalar_one.return_value = 0

        recent_result = MagicMock()
        recent_result.all.return_value = []

        mock_session.execute.side_effect = [count_result, status_result, expired_result, recent_result]

        repo = InvitationRepository(mock_session)
        stats = await repo.get_statistics()

        assert stats.total == 0
        assert stats.conversion_rate == 0.0

    async def test_exists_pending_for_email_true(self, mock_session, mock_result):
        """Test checking if pending invitation exists for email."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1
        mock_session.execute.return_value = count_result

        repo = InvitationRepository(mock_session)
        result = await repo.exists_pending_for_email("test@example.com")

        assert result is True

    async def test_exists_pending_for_email_false(self, mock_session, mock_result):
        """Test checking if pending invitation exists when it doesn't."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        mock_session.execute.return_value = count_result

        repo = InvitationRepository(mock_session)
        result = await repo.exists_pending_for_email("no-invite@example.com")

        assert result is False

    async def test_find_invitations_ascending_sort(self, mock_session, mock_result, sample_invitation):
        """Test finding invitations with ascending sort order."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_invitation]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = InvitationRepository(mock_session)
        invitations, total = await repo.find_invitations(skip=0, limit=100, sort_by="email", sort_order="asc")

        assert total == 1
        assert len(invitations) == 1
