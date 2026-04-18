"""Unit tests for auth_service/services/auth.py."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from auth_service.core import AuthException, ConflictException, NotFoundException, ValidationException
from auth_service.core.enums import EmployeeLevel, InvitationStatus, UserRole
from auth_service.core.security import create_access_token, create_refresh_token
from auth_service.models import Invitation, User, UserMentor
from auth_service.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TelegramAuthRequest,
    TelegramRegistrationRequest,
)
from auth_service.services.auth import AuthService


class TestAuthenticateUser:
    """Tests for AuthService.authenticate_user method."""

    @pytest.fixture
    def active_user(self):
        """Create an active user for testing."""
        return User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            password_hash="$2b$12$testhashedpassword",
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
        )

    async def test_login_happy_path(self, mock_uow, active_user):
        """Test successful login returns user and token."""
        # Arrange
        mock_uow.users.get_by_email.return_value = active_user
        service = AuthService(mock_uow)
        login_data = LoginRequest(email="test@example.com", password="plainpassword")

        with patch("auth_service.services.auth.verify_password", return_value=True):
            # Act
            user, token = await service.authenticate_user(login_data)

        # Assert
        assert user == active_user
        assert token.access_token is not None
        assert token.refresh_token is not None
        assert token.user_id == active_user.id
        assert token.role == active_user.role
        mock_uow.users.get_by_email.assert_called_once_with("test@example.com")
        mock_uow.users.update_last_login.assert_called_once()

    async def test_login_user_not_found_raises(self, mock_uow):
        """Test login with non-existent email raises AuthException."""
        # Arrange
        mock_uow.users.get_by_email.return_value = None
        service = AuthService(mock_uow)
        login_data = LoginRequest(email="nonexistent@example.com", password="password")

        # Act & Assert
        with pytest.raises(AuthException) as exc_info:
            await service.authenticate_user(login_data)

        assert "invalid email or password" in str(exc_info.value.detail).lower()
        mock_uow.users.get_by_email.assert_called_once_with("nonexistent@example.com")

    async def test_login_wrong_password_raises(self, mock_uow, active_user):
        """Test login with wrong password raises AuthException."""
        # Arrange
        mock_uow.users.get_by_email.return_value = active_user
        service = AuthService(mock_uow)
        login_data = LoginRequest(email="test@example.com", password="wrongpassword")

        with patch("auth_service.services.auth.verify_password", return_value=False):
            # Act & Assert
            with pytest.raises(AuthException) as exc_info:
                await service.authenticate_user(login_data)

        assert "invalid email or password" in str(exc_info.value.detail).lower()

    async def test_login_inactive_user_raises(self, mock_uow):
        """Test login with inactive user raises AuthException."""
        # Arrange
        inactive_user = User(
            id=1,
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            employee_id="EMP002",
            password_hash="$2b$12$testhashedpassword",
            is_active=False,  # Inactive!
            is_verified=True,
            role=UserRole.NEWBIE,
        )
        mock_uow.users.get_by_email.return_value = inactive_user
        service = AuthService(mock_uow)
        login_data = LoginRequest(email="inactive@example.com", password="password")

        # Act & Assert
        with pytest.raises(AuthException) as exc_info:
            await service.authenticate_user(login_data)

        assert "disabled" in str(exc_info.value.detail).lower()

    async def test_login_user_without_password_raises(self, mock_uow):
        """Test login with user that has no password (e.g., Telegram-only user)."""
        # Arrange
        telegram_user = User(
            id=1,
            email="telegram@example.com",
            first_name="Telegram",
            last_name="User",
            employee_id="EMP003",
            password_hash=None,  # No password!
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
        )
        mock_uow.users.get_by_email.return_value = telegram_user
        service = AuthService(mock_uow)
        login_data = LoginRequest(email="telegram@example.com", password="somepassword")

        # Act & Assert
        with pytest.raises(AuthException) as exc_info:
            await service.authenticate_user(login_data)

        assert "invalid email or password" in str(exc_info.value.detail).lower()


class TestRefreshAccessToken:
    """Tests for AuthService.refresh_access_token method."""

    @pytest.fixture
    def valid_refresh_token(self):
        """Create a valid refresh token for testing."""
        return create_refresh_token({"sub": "1", "user_id": 1, "role": UserRole.NEWBIE})

    @pytest.fixture
    def active_user(self):
        """Create an active user for testing."""
        return User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            password_hash="$2b$12$testhashedpassword",
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
        )

    async def test_refresh_token_happy_path(
        self, mock_uow, valid_refresh_token, active_user
    ):
        """Test successful token refresh returns new token."""
        # Arrange
        mock_uow.users.get_by_id.return_value = active_user
        service = AuthService(mock_uow)
        refresh_data = RefreshTokenRequest(refresh_token=valid_refresh_token)

        # Act
        token = await service.refresh_access_token(refresh_data)

        # Assert
        assert token.access_token is not None
        assert token.refresh_token is not None
        assert token.user_id == active_user.id
        mock_uow.users.get_by_id.assert_called_once_with(1)

    async def test_refresh_token_invalid_type_raises(self, mock_uow):
        """Test refresh with access token (wrong type) raises AuthException."""
        # Arrange - create an access token instead of refresh token
        access_token = create_access_token(
            {"sub": "1", "user_id": 1, "role": UserRole.NEWBIE}
        )
        service = AuthService(mock_uow)
        refresh_data = RefreshTokenRequest(refresh_token=access_token)

        # Act & Assert
        with pytest.raises(AuthException) as exc_info:
            await service.refresh_access_token(refresh_data)

        assert "invalid token type" in str(exc_info.value.detail).lower()

    async def test_refresh_token_user_not_found_raises(
        self, mock_uow, valid_refresh_token
    ):
        """Test refresh with valid token but non-existent user raises AuthException."""
        # Arrange
        mock_uow.users.get_by_id.return_value = None
        service = AuthService(mock_uow)
        refresh_data = RefreshTokenRequest(refresh_token=valid_refresh_token)

        # Act & Assert
        with pytest.raises(AuthException) as exc_info:
            await service.refresh_access_token(refresh_data)

        assert "not found or inactive" in str(exc_info.value.detail).lower()

    async def test_refresh_token_inactive_user_raises(
        self, mock_uow, valid_refresh_token
    ):
        """Test refresh with valid token but inactive user raises AuthException."""
        # Arrange
        inactive_user = User(
            id=1,
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            employee_id="EMP002",
            is_active=False,
            role=UserRole.NEWBIE,
        )
        mock_uow.users.get_by_id.return_value = inactive_user
        service = AuthService(mock_uow)
        refresh_data = RefreshTokenRequest(refresh_token=valid_refresh_token)

        # Act & Assert
        with pytest.raises(AuthException) as exc_info:
            await service.refresh_access_token(refresh_data)

        assert "not found or inactive" in str(exc_info.value.detail).lower()

    async def test_refresh_token_expired_raises(self, mock_uow):
        """Test refresh with expired token raises AuthException."""
        # Arrange - create an expired refresh token
        expired_token = create_refresh_token(
            {"sub": "1", "user_id": 1, "role": UserRole.NEWBIE},
            expires_delta=timedelta(seconds=-1),  # Already expired
        )
        service = AuthService(mock_uow)
        refresh_data = RefreshTokenRequest(refresh_token=expired_token)

        # Act & Assert
        with pytest.raises(AuthException) as exc_info:
            await service.refresh_access_token(refresh_data)

        assert "invalid refresh token" in str(exc_info.value.detail).lower()


class TestCreateTokenForUser:
    """Tests for AuthService.create_token_for_user method."""

    def test_create_token_for_user_returns_token_with_correct_data(self, mock_uow):
        """Test that create_token_for_user returns proper Token schema."""
        # Arrange
        user = User(
            id=42,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            role=UserRole.MENTOR,
            is_active=True,
        )
        service = AuthService(mock_uow)

        # Act
        token = service.create_token_for_user(user)

        # Assert
        assert token.user_id == 42
        assert token.role == UserRole.MENTOR
        assert token.token_type == "bearer"
        assert token.access_token is not None
        assert token.refresh_token is not None
        assert token.expires_at is not None
        assert isinstance(token.expires_at, datetime)


class TestGetCurrentUser:
    """Tests for AuthService.get_current_user method."""

    @pytest.fixture
    def valid_access_token(self):
        """Create a valid access token for testing."""
        return create_access_token({"sub": "1", "user_id": 1, "role": UserRole.NEWBIE})

    @pytest.fixture
    def active_user(self):
        """Create an active user for testing."""
        return User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            is_active=True,
            role=UserRole.NEWBIE,
        )

    async def test_get_current_user_happy_path(
        self, mock_uow, valid_access_token, active_user
    ):
        """Test successful get_current_user returns user."""
        # Arrange
        mock_uow.users.get_by_id.return_value = active_user
        service = AuthService(mock_uow)

        # Act
        user = await service.get_current_user(valid_access_token)

        # Assert
        assert user == active_user
        mock_uow.users.get_by_id.assert_called_once_with(1)

    async def test_get_current_user_not_found_raises(
        self, mock_uow, valid_access_token
    ):
        """Test get_current_user with non-existent user raises AuthException."""
        # Arrange
        mock_uow.users.get_by_id.return_value = None
        service = AuthService(mock_uow)

        # Act & Assert
        with pytest.raises(AuthException) as exc_info:
            await service.get_current_user(valid_access_token)

        assert "user not found" in str(exc_info.value.detail).lower()

    async def test_get_current_user_inactive_raises(self, mock_uow, valid_access_token):
        """Test get_current_user with inactive user raises AuthException."""
        # Arrange
        inactive_user = User(
            id=1,
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            employee_id="EMP002",
            is_active=False,
            role=UserRole.NEWBIE,
        )
        mock_uow.users.get_by_id.return_value = inactive_user
        service = AuthService(mock_uow)

        # Act & Assert
        with pytest.raises(AuthException) as exc_info:
            await service.get_current_user(valid_access_token)

        assert "disabled" in str(exc_info.value.detail).lower()


class TestAuthenticateWithTelegram:
    """Tests for AuthService.authenticate_with_telegram method."""

    @pytest.fixture
    def telegram_user(self):
        """Create a Telegram-authenticated user for testing."""
        return User(
            id=1,
            email="telegram@example.com",
            first_name="Telegram",
            last_name="User",
            employee_id="EMP001",
            telegram_id=123456789,
            username="@telegramuser",
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
        )

    async def test_telegram_auth_happy_path(self, mock_uow, telegram_user):
        """Test successful Telegram authentication."""
        # Arrange
        mock_uow.users.get_by_telegram_id.return_value = telegram_user
        mock_uow.users.update = AsyncMock()
        service = AuthService(mock_uow)
        telegram_data = TelegramAuthRequest(
            telegram_id=123456789,
            username="@telegramuser",
            first_name="Telegram",
            last_name="User",
        )

        # Act
        user, token = await service.authenticate_with_telegram(telegram_data)

        # Assert
        assert user == telegram_user
        assert token.user_id == telegram_user.id
        mock_uow.users.get_by_telegram_id.assert_called_once_with(123456789)
        mock_uow.users.update.assert_called_once()

    async def test_telegram_auth_user_not_found_raises(self, mock_uow):
        """Test Telegram auth when user not found raises NotFoundException."""
        # Arrange
        mock_uow.users.get_by_telegram_id.return_value = None
        service = AuthService(mock_uow)
        telegram_data = TelegramAuthRequest(
            telegram_id=999999999,
            username="@unknown",
            first_name="Unknown",
        )

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.authenticate_with_telegram(telegram_data)

    async def test_telegram_auth_inactive_user_raises(self, mock_uow):
        """Test Telegram auth with inactive user raises AuthException."""
        # Arrange
        inactive_user = User(
            id=1,
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            employee_id="EMP002",
            telegram_id=123456789,
            is_active=False,
            role=UserRole.NEWBIE,
        )
        mock_uow.users.get_by_telegram_id.return_value = inactive_user
        service = AuthService(mock_uow)
        telegram_data = TelegramAuthRequest(
            telegram_id=123456789,
            username="@inactive",
            first_name="Inactive",
        )

        # Act & Assert
        with pytest.raises(AuthException) as exc_info:
            await service.authenticate_with_telegram(telegram_data)

        assert "disabled" in str(exc_info.value.detail).lower()

    async def test_telegram_auth_updates_user_data(self, mock_uow, telegram_user):
        """Test that Telegram auth updates user profile data."""
        # Arrange
        mock_uow.users.get_by_telegram_id.return_value = telegram_user
        mock_uow.users.update = AsyncMock()
        service = AuthService(mock_uow)
        telegram_data = TelegramAuthRequest(
            telegram_id=123456789,
            username="@newusername",  # New username
            first_name="NewFirst",  # New first name
            last_name="NewLast",  # New last name
        )

        # Act
        await service.authenticate_with_telegram(telegram_data)

        # Assert - verify user data was updated
        assert telegram_user.username == "@newusername"
        assert telegram_user.first_name == "NewFirst"
        assert telegram_user.last_name == "NewLast"


class TestRegisterWithInvitationAndTelegram:
    """Tests for register_with_invitation_and_telegram method."""

    @pytest.fixture
    def valid_invitation(self):
        """Create a valid invitation for testing."""
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
            mentor_id=None,
        )

    @pytest.fixture
    def telegram_registration_data(self):
        """Create Telegram registration data."""
        return TelegramRegistrationRequest(
            telegram_id=123456789,
            username="@newuser",
            first_name="NewFirst",
            last_name="NewLast",
            phone="+1234567890",
        )

    async def test_register_happy_path(self, mock_uow, valid_invitation, telegram_registration_data):
        """Test successful registration with invitation and Telegram."""
        # Arrange
        mock_uow.invitations.get_valid_by_token.return_value = valid_invitation
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_telegram_id.return_value = None
        created_user = User(
            id=5,
            email=valid_invitation.email,
            first_name="New",
            last_name="User",
            telegram_id=telegram_registration_data.telegram_id,
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
        )
        mock_uow.users.create.return_value = created_user
        mock_uow.invitations.mark_as_used = AsyncMock()

        service = AuthService(mock_uow)

        # Act
        result = await service.register_with_invitation_and_telegram(
            "invite-token-123", telegram_registration_data
        )

        # Assert
        assert result == created_user
        mock_uow.invitations.get_valid_by_token.assert_called_once_with("invite-token-123")
        mock_uow.users.get_by_email.assert_called_once_with(valid_invitation.email)
        mock_uow.users.get_by_telegram_id.assert_called_once_with(telegram_registration_data.telegram_id)
        mock_uow.users.create.assert_called_once()
        mock_uow.invitations.mark_as_used.assert_called_once_with(valid_invitation.id, created_user.id)

    async def test_register_invalid_invitation_raises(self, mock_uow, telegram_registration_data):
        """Test registration with invalid invitation raises ValidationException."""
        # Arrange
        mock_uow.invitations.get_valid_by_token.return_value = None
        service = AuthService(mock_uow)

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            await service.register_with_invitation_and_telegram(
                "invalid-token", telegram_registration_data
            )

        assert "invalid or expired invitation" in str(exc_info.value.detail).lower()

    async def test_register_user_already_exists_raises(self, mock_uow, valid_invitation, telegram_registration_data):
        """Test registration when user already exists raises ConflictException."""
        # Arrange
        mock_uow.invitations.get_valid_by_token.return_value = valid_invitation
        existing_user = User(
            id=99,
            email=valid_invitation.email,
            first_name="Existing",
            last_name="User",
            is_active=True,
        )
        mock_uow.users.get_by_email.return_value = existing_user
        service = AuthService(mock_uow)

        # Act & Assert
        with pytest.raises(ConflictException) as exc_info:
            await service.register_with_invitation_and_telegram(
                "invite-token-123", telegram_registration_data
            )

        assert "user already exists" in str(exc_info.value.detail).lower()

    async def test_register_telegram_already_linked_raises(self, mock_uow, valid_invitation, telegram_registration_data):
        """Test registration when Telegram already linked raises ConflictException."""
        # Arrange
        mock_uow.invitations.get_valid_by_token.return_value = valid_invitation
        mock_uow.users.get_by_email.return_value = None
        existing_telegram_user = User(
            id=88,
            email="other@example.com",
            telegram_id=telegram_registration_data.telegram_id,
            is_active=True,
        )
        mock_uow.users.get_by_telegram_id.return_value = existing_telegram_user
        service = AuthService(mock_uow)

        # Act & Assert
        with pytest.raises(ConflictException) as exc_info:
            await service.register_with_invitation_and_telegram(
                "invite-token-123", telegram_registration_data
            )

        assert "telegram account already linked" in str(exc_info.value.detail).lower()

    async def test_register_uses_invitation_names_when_telegram_names_none(self, mock_uow, valid_invitation):
        """Test that invitation names are used when Telegram names are None."""
        # Arrange
        mock_uow.invitations.get_valid_by_token.return_value = valid_invitation
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_telegram_id.return_value = None

        # Telegram data with no names
        telegram_data = TelegramRegistrationRequest(
            telegram_id=123456789,
            username="@newuser",
            first_name=None,
            last_name=None,
        )

        created_user = User(
            id=5,
            email=valid_invitation.email,
            first_name=valid_invitation.first_name,
            last_name=valid_invitation.last_name,
            telegram_id=123456789,
            is_active=True,
        )
        mock_uow.users.create.return_value = created_user
        mock_uow.invitations.mark_as_used = AsyncMock()

        service = AuthService(mock_uow)

        # Act
        result = await service.register_with_invitation_and_telegram(
            "invite-token-123", telegram_data
        )

        # Assert - verify first_name and last_name from invitation
        call_args = mock_uow.users.create.call_args
        created_user_arg = call_args[0][0]
        assert created_user_arg.first_name == valid_invitation.first_name
        assert created_user_arg.last_name == valid_invitation.last_name

    async def test_register_uses_telegram_names_when_invitation_names_none(self, mock_uow, telegram_registration_data):
        """Test that Telegram names are used when invitation names are None."""
        # Arrange
        invitation_no_names = Invitation(
            id=1,
            token="invite-token-123",
            email="newuser@example.com",
            employee_id="EMP005",
            first_name=None,
            last_name=None,
            role=UserRole.NEWBIE,
            status=InvitationStatus.PENDING,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        mock_uow.invitations.get_valid_by_token.return_value = invitation_no_names
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_telegram_id.return_value = None

        created_user = User(
            id=5,
            email=invitation_no_names.email,
            first_name=telegram_registration_data.first_name,
            last_name=telegram_registration_data.last_name,
            telegram_id=telegram_registration_data.telegram_id,
            is_active=True,
        )
        mock_uow.users.create.return_value = created_user
        mock_uow.invitations.mark_as_used = AsyncMock()

        service = AuthService(mock_uow)

        # Act
        result = await service.register_with_invitation_and_telegram(
            "invite-token-123", telegram_registration_data
        )

        # Assert - verify first_name and last_name from Telegram
        call_args = mock_uow.users.create.call_args
        created_user_arg = call_args[0][0]
        assert created_user_arg.first_name == telegram_registration_data.first_name
        assert created_user_arg.last_name == telegram_registration_data.last_name

    async def test_register_uses_default_first_name_when_both_none(self, mock_uow):
        """Test that 'Unknown' is used when both invitation and Telegram first_name are None."""
        # Arrange
        invitation_no_names = Invitation(
            id=1,
            token="invite-token-123",
            email="newuser@example.com",
            employee_id="EMP005",
            first_name=None,
            last_name=None,
            role=UserRole.NEWBIE,
            status=InvitationStatus.PENDING,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        telegram_data_no_first_name = TelegramRegistrationRequest(
            telegram_id=123456789,
            username="@newuser",
            first_name=None,
            last_name=None,
        )
        mock_uow.invitations.get_valid_by_token.return_value = invitation_no_names
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_telegram_id.return_value = None

        created_user = User(
            id=5,
            email=invitation_no_names.email,
            first_name="Unknown",
            is_active=True,
        )
        mock_uow.users.create.return_value = created_user
        mock_uow.invitations.mark_as_used = AsyncMock()

        service = AuthService(mock_uow)

        # Act
        await service.register_with_invitation_and_telegram(
            "invite-token-123", telegram_data_no_first_name
        )

        # Assert
        call_args = mock_uow.users.create.call_args
        created_user_arg = call_args[0][0]
        assert created_user_arg.first_name == "Unknown"

    async def test_register_creates_mentor_relation(self, mock_uow, valid_invitation, telegram_registration_data):
        """Test that user-mentor relation is created when invitation has mentor_id."""
        # Arrange
        valid_invitation.mentor_id = 10
        mock_uow.invitations.get_valid_by_token.return_value = valid_invitation
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_telegram_id.return_value = None

        created_user = User(
            id=5,
            email=valid_invitation.email,
            is_active=True,
        )
        mock_uow.users.create.return_value = created_user
        mock_uow.invitations.mark_as_used = AsyncMock()
        mock_uow.user_mentors.create = AsyncMock()

        service = AuthService(mock_uow)

        # Act
        result = await service.register_with_invitation_and_telegram(
            "invite-token-123", telegram_registration_data
        )

        # Assert
        assert result == created_user
        mock_uow.user_mentors.create.assert_called_once()
        call_args = mock_uow.user_mentors.create.call_args
        user_mentor_arg = call_args[0][0]
        assert user_mentor_arg.user_id == created_user.id
        assert user_mentor_arg.mentor_id == valid_invitation.mentor_id
        assert user_mentor_arg.is_active is True

    async def test_register_no_mentor_relation_when_no_mentor_id(self, mock_uow, valid_invitation, telegram_registration_data):
        """Test that user-mentor relation is not created when invitation has no mentor_id."""
        # Arrange
        valid_invitation.mentor_id = None
        mock_uow.invitations.get_valid_by_token.return_value = valid_invitation
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_telegram_id.return_value = None

        created_user = User(
            id=5,
            email=valid_invitation.email,
            is_active=True,
        )
        mock_uow.users.create.return_value = created_user
        mock_uow.invitations.mark_as_used = AsyncMock()

        service = AuthService(mock_uow)

        # Act
        result = await service.register_with_invitation_and_telegram(
            "invite-token-123", telegram_registration_data
        )

        # Assert
        mock_uow.user_mentors.create.assert_not_called()


class TestAutoCreateUserChecklists:
    """Tests for auto_create_user_checklists method."""

    @pytest.fixture
    def user_with_dept_and_position(self):
        """Create a user with department_id and position."""
        return User(
            id=1,
            email="test@example.com",
            department_id=2,
            position="Developer",
            employee_id="EMP001",
            is_active=True,
        )

    @pytest.fixture
    def user_with_mentor_relation(self):
        """Create a user mentor relation."""
        return UserMentor(
            id=1,
            user_id=1,
            mentor_id=5,
            is_active=True,
        )

    async def test_auto_create_with_department_and_position(self, mock_uow, user_with_dept_and_position):
        """Test auto-create when user has department_id and position."""
        # Arrange
        user_with_dept_and_position.position = "Developer"
        mock_uow.user_mentors.get_active_by_user_id.return_value = None

        with patch(
            "auth_service.services.auth.checklists_service_client.auto_create_checklists",
            new_callable=AsyncMock,
        ) as mock_auto_create:
            service = AuthService(mock_uow)

            # Act
            await service.auto_create_user_checklists(user_with_dept_and_position)

            # Assert
            mock_auto_create.assert_awaited_once_with(
                user_id=1,
                employee_id="EMP001",
                department_id=2,
                position="Developer",
                mentor_id=None,
            )

    async def test_auto_create_with_mentor(self, mock_uow, user_with_dept_and_position, user_with_mentor_relation):
        """Test auto-create when user has an active mentor."""
        # Arrange
        mock_uow.user_mentors.get_active_by_user_id.return_value = user_with_mentor_relation

        with patch(
            "auth_service.services.auth.checklists_service_client.auto_create_checklists",
            new_callable=AsyncMock,
        ) as mock_auto_create:
            service = AuthService(mock_uow)

            # Act
            await service.auto_create_user_checklists(user_with_dept_and_position)

            # Assert
            mock_auto_create.assert_awaited_once_with(
                user_id=1,
                employee_id="EMP001",
                department_id=2,
                position="Developer",
                mentor_id=5,
            )

    async def test_auto_create_skips_when_no_department_and_no_position(self, mock_uow):
        """Test auto-create is skipped when user has neither department nor position."""
        # Arrange
        user_no_info = User(
            id=1,
            email="test@example.com",
            department_id=None,
            position=None,
            is_active=True,
        )

        with patch(
            "auth_service.services.auth.checklists_service_client.auto_create_checklists",
            new_callable=AsyncMock,
        ) as mock_auto_create:
            service = AuthService(mock_uow)

            # Act
            await service.auto_create_user_checklists(user_no_info)

            # Assert
            mock_auto_create.assert_not_called()
            mock_uow.user_mentors.get_active_by_user_id.assert_not_called()

    async def test_auto_create_with_only_department(self, mock_uow):
        """Test auto-create when user has only department_id."""
        # Arrange
        user_dept_only = User(
            id=1,
            email="test@example.com",
            department_id=2,
            position=None,
            employee_id="EMP001",
            is_active=True,
        )
        mock_uow.user_mentors.get_active_by_user_id.return_value = None

        with patch(
            "auth_service.services.auth.checklists_service_client.auto_create_checklists",
            new_callable=AsyncMock,
        ) as mock_auto_create:
            service = AuthService(mock_uow)

            # Act
            await service.auto_create_user_checklists(user_dept_only)

            # Assert
            mock_auto_create.assert_awaited_once_with(
                user_id=1,
                employee_id="EMP001",
                department_id=2,
                position=None,
                mentor_id=None,
            )

    async def test_auto_create_with_only_position(self, mock_uow):
        """Test auto-create when user has only position."""
        # Arrange
        user_position_only = User(
            id=1,
            email="test@example.com",
            department_id=None,
            position="Developer",
            employee_id="EMP001",
            is_active=True,
        )
        mock_uow.user_mentors.get_active_by_user_id.return_value = None

        with patch(
            "auth_service.services.auth.checklists_service_client.auto_create_checklists",
            new_callable=AsyncMock,
        ) as mock_auto_create:
            service = AuthService(mock_uow)

            # Act
            await service.auto_create_user_checklists(user_position_only)

            # Assert
            mock_auto_create.assert_awaited_once_with(
                user_id=1,
                employee_id="EMP001",
                department_id=None,
                position="Developer",
                mentor_id=None,
            )
