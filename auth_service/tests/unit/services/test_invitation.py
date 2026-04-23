"""Unit tests for invitation_service/services/invitation.py."""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from auth_service.core import ConflictException, NotFoundException, ValidationException
from auth_service.core.enums import InvitationStatus, UserRole
from auth_service.models import Invitation, User
from auth_service.schemas import InvitationCreate, InvitationStats
from auth_service.services.invitation import InvitationService


@pytest.fixture
def sample_invitation():
    """Create a sample invitation for testing."""
    return Invitation(
        id=1,
        token="invite-token-123",
        email="invited@example.com",
        employee_id="EMP001",
        first_name="Invited",
        last_name="User",
        department_id=1,
        position="Developer",
        role=UserRole.NEWBIE,
        mentor_id=None,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        status=InvitationStatus.PENDING,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def used_invitation():
    """Create a used invitation for testing."""
    return Invitation(
        id=2,
        token="used-token-456",
        email="used@example.com",
        employee_id="EMP002",
        first_name="Used",
        last_name="User",
        expires_at=datetime.now(UTC) - timedelta(days=1),
        status=InvitationStatus.USED,
        created_at=datetime.now(UTC) - timedelta(days=8),
        used_at=datetime.now(UTC) - timedelta(days=1),
    )


@pytest.fixture
def revoked_invitation():
    """Create a revoked invitation for testing."""
    return Invitation(
        id=3,
        token="revoked-token-789",
        email="revoked@example.com",
        employee_id="EMP003",
        first_name="Revoked",
        last_name="User",
        expires_at=datetime.now(UTC) + timedelta(days=5),
        status=InvitationStatus.REVOKED,
        created_at=datetime.now(UTC) - timedelta(days=2),
    )


class TestCreateInvitation:
    """Tests for InvitationService.create_invitation method."""

    async def test_create_invitation_success(self, mock_uow):
        """Test creating a new invitation."""
        mock_uow.invitations.exists_pending_for_email.return_value = False
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_employee_id.return_value = None

        created_invitation = Invitation(
            id=1,
            token="new-token-123",
            email="new@example.com",
            employee_id="EMP004",
            first_name="New",
            last_name="User",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            status=InvitationStatus.PENDING,
            created_at=datetime.now(UTC),
        )
        mock_uow.invitations.create.return_value = created_invitation

        with patch("auth_service.services.invitation.generate_invitation_token", return_value="new-token-123"):
            service = InvitationService(mock_uow)
            invitation_data = InvitationCreate(
                email="new@example.com",
                employee_id="EMP004",
                first_name="New",
                last_name="User",
                department_id=1,
                position="Developer",
                role=UserRole.NEWBIE,
                expires_in_days=7,
            )

            invitation = await service.create_invitation(invitation_data)

        assert invitation.email == "new@example.com"
        assert invitation.token == "new-token-123"
        mock_uow.invitations.create.assert_called_once()
        mock_uow.commit.assert_awaited_once()  # Verify transaction committed

    async def test_create_invitation_pending_exists_raises(self, mock_uow):
        """Test creating invitation when pending exists raises ConflictException."""
        mock_uow.invitations.exists_pending_for_email.return_value = True
        service = InvitationService(mock_uow)

        invitation_data = InvitationCreate(
            email="invited@example.com",  # Same email as pending
            employee_id="EMP004",
            first_name="New",
        )

        with pytest.raises(ConflictException) as exc_info:
            await service.create_invitation(invitation_data)

        assert "pending invitation already exists" in str(exc_info.value.detail).lower()

    async def test_create_invitation_user_exists_raises(self, mock_uow):
        """Test creating invitation when user exists raises ConflictException."""
        mock_uow.invitations.exists_pending_for_email.return_value = False
        mock_uow.users.get_by_email.return_value = User(id=1, email="invited@example.com", employee_id="EMP001")
        service = InvitationService(mock_uow)

        invitation_data = InvitationCreate(
            email="invited@example.com",  # User with this email exists
            employee_id="EMP004",
            first_name="New",
        )

        with pytest.raises(ConflictException) as exc_info:
            await service.create_invitation(invitation_data)

        assert "user with this email already exists" in str(exc_info.value.detail).lower()

    async def test_create_invitation_employee_id_exists_raises(self, mock_uow):
        """Test creating invitation when employee_id exists raises ConflictException."""
        mock_uow.invitations.exists_pending_for_email.return_value = False
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_employee_id.return_value = User(id=1, email="existing@example.com", employee_id="EMP001")
        service = InvitationService(mock_uow)

        invitation_data = InvitationCreate(
            email="new@example.com",
            employee_id="EMP001",  # Already in use
            first_name="New",
        )

        with pytest.raises(ConflictException) as exc_info:
            await service.create_invitation(invitation_data)

        assert "employee id already in use" in str(exc_info.value.detail).lower()

    async def test_create_invitation_with_invalid_mentor_raises(self, mock_uow):
        """Test creating invitation with non-existent mentor raises NotFoundException."""
        mock_uow.invitations.exists_pending_for_email.return_value = False
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_employee_id.return_value = None
        mock_uow.users.get_by_id.return_value = None  # Mentor not found
        service = InvitationService(mock_uow)

        invitation_data = InvitationCreate(
            email="new@example.com",
            employee_id="EMP004",
            first_name="New",
            mentor_id=999,  # Non-existent mentor
        )

        with pytest.raises(NotFoundException) as exc_info:
            await service.create_invitation(invitation_data)

        assert "mentor not found" in str(exc_info.value.detail).lower()
        mock_uow.invitations.create.assert_not_called()
        mock_uow.commit.assert_not_awaited()


class TestGetInvitationById:
    """Tests for InvitationService.get_invitation_by_id method."""

    async def test_get_invitation_by_id_success(self, mock_uow, sample_invitation):
        """Test getting invitation by ID."""
        mock_uow.invitations.get_by_id.return_value = sample_invitation
        service = InvitationService(mock_uow)

        invitation = await service.get_invitation_by_id(1)

        assert invitation == sample_invitation
        mock_uow.invitations.get_by_id.assert_called_once_with(1)

    async def test_get_invitation_by_id_not_found_raises(self, mock_uow):
        """Test getting non-existent invitation raises NotFoundException."""
        mock_uow.invitations.get_by_id.return_value = None
        service = InvitationService(mock_uow)

        with pytest.raises(NotFoundException) as exc_info:
            await service.get_invitation_by_id(999)

        assert "not found" in str(exc_info.value.detail).lower()


class TestGetValidInvitation:
    """Tests for InvitationService.get_valid_invitation method."""

    async def test_get_valid_invitation_success(self, mock_uow, sample_invitation):
        """Test getting valid invitation by token."""
        mock_uow.invitations.get_valid_by_token.return_value = sample_invitation
        service = InvitationService(mock_uow)

        invitation = await service.get_valid_invitation("invite-token-123")

        assert invitation == sample_invitation
        mock_uow.invitations.get_valid_by_token.assert_called_once_with("invite-token-123")

    async def test_get_valid_invitation_invalid_raises(self, mock_uow):
        """Test getting invalid/expired invitation raises ValidationException."""
        mock_uow.invitations.get_valid_by_token.return_value = None
        service = InvitationService(mock_uow)

        with pytest.raises(ValidationException) as exc_info:
            await service.get_valid_invitation("invalid-token")

        assert "invalid or expired invitation" in str(exc_info.value.detail).lower()


class TestResendInvitation:
    """Tests for InvitationService.resend_invitation method."""

    async def test_resend_invitation_success(self, mock_uow, sample_invitation):
        """Test resending a pending invitation."""
        mock_uow.invitations.get_by_id.return_value = sample_invitation
        mock_uow.invitations.update.return_value = sample_invitation

        with patch("auth_service.services.invitation.generate_invitation_token", return_value="new-token-456"):
            service = InvitationService(mock_uow)
            invitation = await service.resend_invitation(1)

        assert invitation.token == "new-token-456"
        mock_uow.invitations.update.assert_called_once()

    async def test_resend_non_pending_raises(self, mock_uow, used_invitation):
        """Test resending non-pending invitation raises ValidationException."""
        mock_uow.invitations.get_by_id.return_value = used_invitation
        service = InvitationService(mock_uow)

        with pytest.raises(ValidationException) as exc_info:
            await service.resend_invitation(2)

        assert "can only resend pending invitations" in str(exc_info.value.detail).lower()


class TestRevokeInvitation:
    """Tests for InvitationService.revoke_invitation method."""

    async def test_revoke_invitation_success(self, mock_uow, sample_invitation):
        """Test revoking a pending invitation."""
        mock_uow.invitations.get_by_id.return_value = sample_invitation
        mock_uow.invitations.update.return_value = sample_invitation
        service = InvitationService(mock_uow)

        invitation = await service.revoke_invitation(1)

        assert invitation.status == InvitationStatus.REVOKED
        mock_uow.invitations.update.assert_called_once()

    async def test_revoke_non_pending_raises(self, mock_uow, used_invitation):
        """Test revoking non-pending invitation raises ValidationException."""
        mock_uow.invitations.get_by_id.return_value = used_invitation
        service = InvitationService(mock_uow)

        with pytest.raises(ValidationException) as exc_info:
            await service.revoke_invitation(2)

        assert "can only revoke pending invitations" in str(exc_info.value.detail).lower()


class TestGetInvitations:
    """Tests for InvitationService.get_invitations method."""

    async def test_get_invitations_success(self, mock_uow, sample_invitation, used_invitation):
        """Test getting paginated list of invitations."""
        invitations = [sample_invitation, used_invitation]
        mock_uow.invitations.find_invitations.return_value = (invitations, 2)
        service = InvitationService(mock_uow)

        result, total = await service.get_invitations(skip=0, limit=10)

        assert len(result) == 2
        assert total == 2

    async def test_get_invitations_with_filters(self, mock_uow, sample_invitation):
        """Test getting invitations with filters."""
        mock_uow.invitations.find_invitations.return_value = ([sample_invitation], 1)
        service = InvitationService(mock_uow)

        _result, _total = await service.get_invitations(
            skip=0,
            limit=10,
            email="invited@example.com",
            role=UserRole.NEWBIE,
            status=InvitationStatus.PENDING,
            department_id=1,
            expired_only=False,
        )

        mock_uow.invitations.find_invitations.assert_called_once_with(
            skip=0,
            limit=10,
            email="invited@example.com",
            role=UserRole.NEWBIE,
            status=InvitationStatus.PENDING,
            department_id=1,
            expired_only=False,
            sort_by=None,
            sort_order="desc",
        )


class TestGetInvitationStats:
    """Tests for InvitationService.get_invitation_stats method."""

    async def test_get_invitation_stats_success(self, mock_uow):
        """Test getting invitation statistics."""
        stats = InvitationStats(
            total=10,
            pending=5,
            used=3,
            revoked=1,
            expired=1,
            conversion_rate=30.0,
            by_status={InvitationStatus.PENDING: 5, InvitationStatus.USED: 3, InvitationStatus.REVOKED: 1},
            recent_activity=[],
        )
        mock_uow.invitations.get_statistics.return_value = stats
        service = InvitationService(mock_uow)

        result = await service.get_invitation_stats()

        assert result.total == 10
        assert result.pending == 5
        assert result.conversion_rate == 30.0


class TestDeleteInvitation:
    """Tests for InvitationService.delete_invitation method."""

    async def test_delete_invitation_success(self, mock_uow, sample_invitation):
        """Test deleting an invitation."""
        mock_uow.invitations.get_by_id.return_value = sample_invitation
        mock_uow.invitations.delete.return_value = True
        service = InvitationService(mock_uow)

        result = await service.delete_invitation(1)

        assert result is True
        mock_uow.invitations.delete.assert_called_once_with(1)

    async def test_delete_invitation_not_found_raises(self, mock_uow):
        """Test deleting non-existent invitation raises NotFoundException."""
        mock_uow.invitations.get_by_id.return_value = None
        service = InvitationService(mock_uow)

        with pytest.raises(NotFoundException) as exc_info:
            await service.delete_invitation(999)

        assert "not found" in str(exc_info.value.detail).lower()


class TestGenerateInvitationUrl:
    """Tests for InvitationService.generate_invitation_url method."""

    def test_generate_invitation_url_returns_valid_url(self, mock_uow):
        """Test generating invitation URL returns valid Telegram bot URL."""
        service = InvitationService(mock_uow)

        url = service.generate_invitation_url("test-token-123")

        assert "t.me/" in str(url)
        assert "test-token-123" in str(url)
