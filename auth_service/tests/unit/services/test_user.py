"""Unit tests for user_service/services/user.py."""


import pytest

from auth_service.core import ConflictException, NotFoundException, UserRole
from auth_service.models import User
from auth_service.schemas import UserCreate, UserUpdate
from auth_service.services.user import UserService


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id=1,
        email="test@example.com",
        first_name="Test",
        last_name="User",
        employee_id="EMP001",
        password_hash="$2b$12$testhash",
        is_active=True,
        is_verified=True,
        role=UserRole.NEWBIE,
    )


@pytest.fixture
def another_user():
    """Create another user for testing."""
    return User(
        id=2,
        email="another@example.com",
        first_name="Another",
        last_name="User",
        employee_id="EMP002",
        password_hash="$2b$12$testhash",
        is_active=True,
        is_verified=True,
        role=UserRole.MENTOR,
        telegram_id=123456789,
    )


class TestGetUserById:
    """Tests for UserService.get_user_by_id method."""

    async def test_get_user_by_id_success(self, mock_uow, sample_user):
        """Test getting user by ID returns user."""
        mock_uow.users.get_by_id.return_value = sample_user
        service = UserService(mock_uow)

        user = await service.get_user_by_id(1)

        assert user == sample_user
        mock_uow.users.get_by_id.assert_called_once_with(1)

    async def test_get_user_by_id_not_found_raises(self, mock_uow):
        """Test getting non-existent user raises NotFoundException."""
        mock_uow.users.get_by_id.return_value = None
        service = UserService(mock_uow)

        with pytest.raises(NotFoundException) as exc_info:
            await service.get_user_by_id(999)

        assert "not found" in str(exc_info.value.detail).lower()


class TestGetUserByEmail:
    """Tests for UserService.get_user_by_email method."""

    async def test_get_user_by_email_success(self, mock_uow, sample_user):
        """Test getting user by email returns user."""
        mock_uow.users.get_by_email.return_value = sample_user
        service = UserService(mock_uow)

        user = await service.get_user_by_email("test@example.com")

        assert user == sample_user
        mock_uow.users.get_by_email.assert_called_once_with("test@example.com")

    async def test_get_user_by_email_not_found(self, mock_uow):
        """Test getting non-existent email returns None."""
        mock_uow.users.get_by_email.return_value = None
        service = UserService(mock_uow)

        user = await service.get_user_by_email("nonexistent@example.com")

        assert user is None


class TestGetUserByTelegramId:
    """Tests for UserService.get_user_by_telegram_id method."""

    async def test_get_user_by_telegram_id_success(self, mock_uow, another_user):
        """Test getting user by Telegram ID returns user."""
        mock_uow.users.get_by_telegram_id.return_value = another_user
        service = UserService(mock_uow)

        user = await service.get_user_by_telegram_id(123456789)

        assert user == another_user
        mock_uow.users.get_by_telegram_id.assert_called_once_with(123456789)

    async def test_get_user_by_telegram_id_not_found(self, mock_uow):
        """Test getting non-existent Telegram ID returns None."""
        mock_uow.users.get_by_telegram_id.return_value = None
        service = UserService(mock_uow)

        user = await service.get_user_by_telegram_id(999999)

        assert user is None


class TestCreateUser:
    """Tests for UserService.create_user method."""

    async def test_create_user_success(self, mock_uow):
        """Test creating a new user."""
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_employee_id.return_value = None

        created_user = User(
            id=3,
            email="new@example.com",
            first_name="New",
            last_name="User",
            employee_id="EMP003",
            password_hash="$2b$12$newhash",
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
        )
        mock_uow.users.create.return_value = created_user

        service = UserService(mock_uow)
        user_data = UserCreate(
            email="new@example.com",
            first_name="New",
            last_name="User",
            employee_id="EMP003",
            password="password123",
            role=UserRole.NEWBIE,
        )

        user = await service.create_user(user_data)

        assert user == created_user
        mock_uow.users.create.assert_called_once()
        mock_uow.commit.assert_awaited_once()  # Verify transaction committed

    async def test_create_user_duplicate_email_raises(self, mock_uow, sample_user):
        """Test creating user with duplicate email raises ConflictException."""
        mock_uow.users.get_by_email.return_value = sample_user
        service = UserService(mock_uow)

        user_data = UserCreate(
            email="test@example.com",  # Already exists
            first_name="New",
            employee_id="EMP003",
            password="password123",
        )

        with pytest.raises(ConflictException) as exc_info:
            await service.create_user(user_data)

        assert "email already registered" in str(exc_info.value.detail).lower()

    async def test_create_user_duplicate_employee_id_raises(self, mock_uow, sample_user):
        """Test creating user with duplicate employee_id raises ConflictException."""
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_employee_id.return_value = sample_user
        service = UserService(mock_uow)

        user_data = UserCreate(
            email="new@example.com",
            first_name="New",
            employee_id="EMP001",  # Already exists
            password="password123",
        )

        with pytest.raises(ConflictException) as exc_info:
            await service.create_user(user_data)

        assert "employee id already registered" in str(exc_info.value.detail).lower()

    async def test_create_user_duplicate_telegram_raises(self, mock_uow, another_user):
        """Test creating user with duplicate telegram_id raises ConflictException."""
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_employee_id.return_value = None
        mock_uow.users.get_by_telegram_id.return_value = another_user
        service = UserService(mock_uow)

        user_data = UserCreate(
            email="new@example.com",
            first_name="New",
            employee_id="EMP003",
            password="password123",
            telegram_id=123456789,  # Already linked to another_user
        )

        with pytest.raises(ConflictException) as exc_info:
            await service.create_user(user_data)

        assert "telegram account already linked" in str(exc_info.value.detail).lower()


class TestUpdateUser:
    """Tests for UserService.update_user method."""

    async def test_update_user_success(self, mock_uow, sample_user):
        """Test updating user information."""
        mock_uow.users.get_by_id.return_value = sample_user
        mock_uow.users.get_by_email.return_value = None

        updated = User(
            id=sample_user.id,
            email="updated@example.com",
            first_name="Updated",
            last_name="User",
            employee_id="EMP001",
            password_hash="$2b$12$testhash",
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
        )
        mock_uow.users.update.return_value = updated

        service = UserService(mock_uow)
        user_data = UserUpdate(
            email="updated@example.com",
            first_name="Updated",
        )

        user = await service.update_user(1, user_data)

        assert user.email == "updated@example.com"
        assert user.first_name == "Updated"

    async def test_update_user_email_conflict_raises(self, mock_uow, sample_user, another_user):
        """Test updating to duplicate email raises ConflictException."""
        mock_uow.users.get_by_id.return_value = sample_user
        mock_uow.users.get_by_email.return_value = another_user  # Different user with same email

        service = UserService(mock_uow)
        user_data = UserUpdate(email="another@example.com")

        with pytest.raises(ConflictException) as exc_info:
            await service.update_user(1, user_data)

        assert "email already registered" in str(exc_info.value.detail).lower()

    async def test_update_user_telegram_conflict_raises(self, mock_uow, sample_user, another_user):
        """Test updating to duplicate telegram_id raises ConflictException."""
        mock_uow.users.get_by_id.return_value = sample_user
        mock_uow.users.get_by_email.return_value = None
        mock_uow.users.get_by_telegram_id.return_value = another_user  # Different user with same telegram

        service = UserService(mock_uow)
        user_data = UserUpdate(telegram_id=123456789)

        with pytest.raises(ConflictException) as exc_info:
            await service.update_user(1, user_data)

        assert "telegram account already linked" in str(exc_info.value.detail).lower()


class TestDeactivateUser:
    """Tests for UserService.deactivate_user method."""

    async def test_deactivate_user_success(self, mock_uow):
        """Test deactivating a user."""
        mock_uow.users.deactivate_user.return_value = None
        service = UserService(mock_uow)

        await service.deactivate_user(1)

        mock_uow.users.deactivate_user.assert_called_once_with(1)


class TestDeleteUser:
    """Tests for UserService.delete_user method (covers lines 116-117)."""

    async def test_delete_user_success(self, mock_uow, sample_user):
        """Test deleting a user (covers lines 116-117)."""
        from unittest.mock import AsyncMock
        mock_uow.users.get_by_id.return_value = sample_user
        mock_uow.users.delete = AsyncMock(return_value=True)
        service = UserService(mock_uow)

        await service.delete_user(1)

        # Line 116: Verify user exists
        mock_uow.users.get_by_id.assert_called_once_with(1)
        # Line 117: Delete the user
        mock_uow.users.delete.assert_awaited_once_with(1)

    async def test_delete_user_not_found_raises(self, mock_uow):
        """Test deleting non-existent user raises NotFoundException."""
        mock_uow.users.get_by_id.return_value = None
        service = UserService(mock_uow)

        with pytest.raises(NotFoundException) as exc_info:
            await service.delete_user(999)

        assert "not found" in str(exc_info.value.detail).lower()
        mock_uow.users.delete.assert_not_called()


class TestGetUsers:
    """Tests for UserService.get_users method."""

    async def test_get_users_success(self, mock_uow, sample_user, another_user):
        """Test getting paginated list of users."""
        users = [sample_user, another_user]
        mock_uow.users.find_users.return_value = (users, 2)
        service = UserService(mock_uow)

        result, total = await service.get_users(skip=0, limit=10)

        assert len(result) == 2
        assert total == 2
        mock_uow.users.find_users.assert_called_once()

    async def test_get_users_with_filters(self, mock_uow, sample_user):
        """Test getting users with filters."""
        mock_uow.users.find_users.return_value = ([sample_user], 1)
        service = UserService(mock_uow)

        _result, _total = await service.get_users(
            skip=0,
            limit=10,
            search="test",
            department_id=1,
            role=UserRole.NEWBIE,
            is_active=True,
        )

        mock_uow.users.find_users.assert_called_once_with(
            skip=0,
            limit=10,
            search="test",
            department_id=1,
            role=UserRole.NEWBIE,
            is_active=True,
            sort_by=None,
            sort_order="desc",
        )


class TestUpdateUserRole:
    """Tests for UserService.update_user_role method."""

    async def test_update_user_role_success(self, mock_uow, sample_user):
        """Test updating user role."""
        updated = User(
            id=sample_user.id,
            email=sample_user.email,
            first_name=sample_user.first_name,
            employee_id=sample_user.employee_id,
            role=UserRole.MENTOR,  # Changed
        )
        mock_uow.users.update_role.return_value = updated
        service = UserService(mock_uow)

        user = await service.update_user_role(1, UserRole.MENTOR)

        assert user.role == UserRole.MENTOR
        mock_uow.users.update_role.assert_called_once_with(1, UserRole.MENTOR)


class TestLinkTelegramAccount:
    """Tests for UserService.link_telegram_account method."""

    async def test_link_telegram_success(self, mock_uow, sample_user):
        """Test linking Telegram account to user."""
        mock_uow.users.get_by_telegram_id.return_value = None  # No conflict
        mock_uow.users.get_by_id.return_value = sample_user

        updated = User(
            id=sample_user.id,
            email=sample_user.email,
            first_name=sample_user.first_name,
            employee_id=sample_user.employee_id,
            telegram_id=987654321,
            username="@testuser",
        )
        mock_uow.users.update.return_value = updated

        service = UserService(mock_uow)
        user = await service.link_telegram_account(1, 987654321, "@testuser")

        assert user.telegram_id == 987654321
        assert user.username == "@testuser"

    async def test_link_telegram_conflict_raises(self, mock_uow, another_user):
        """Test linking duplicate Telegram account raises ConflictException."""
        mock_uow.users.get_by_telegram_id.return_value = another_user  # Already linked
        service = UserService(mock_uow)

        with pytest.raises(ConflictException) as exc_info:
            await service.link_telegram_account(1, 123456789, "@anotheruser")

        assert "telegram account already linked" in str(exc_info.value.detail).lower()


class TestChangePassword:
    """Tests for UserService.change_password method."""

    async def test_change_password_success(self, mock_uow, sample_user):
        """Test changing user password."""
        mock_uow.users.get_by_id.return_value = sample_user
        mock_uow.users.update.return_value = sample_user
        service = UserService(mock_uow)

        from unittest.mock import patch
        with patch("auth_service.services.user.verify_password", return_value=True):
            with patch("auth_service.services.user.hash_password", return_value="$2b$12$newhash"):
                await service.change_password(1, "current_password", "new_password123")

        mock_uow.users.update.assert_called_once()

    async def test_change_password_no_password_hash_raises(self, mock_uow):
        """Test changing password for user without password raises ValidationException."""
        user_without_password = User(
            id=1,
            email="telegram@example.com",
            first_name="Telegram",
            employee_id="EMP003",
            password_hash=None,  # No password
        )
        mock_uow.users.get_by_id.return_value = user_without_password
        service = UserService(mock_uow)

        from auth_service.core import ValidationException
        with pytest.raises(ValidationException) as exc_info:
            await service.change_password(1, "current", "new")

        assert "password not set" in str(exc_info.value.detail).lower()

    async def test_change_password_wrong_current_raises(self, mock_uow, sample_user):
        """Test changing password with wrong current password raises ValidationException."""
        mock_uow.users.get_by_id.return_value = sample_user
        service = UserService(mock_uow)

        from unittest.mock import patch

        from auth_service.core import ValidationException
        with patch("auth_service.services.user.verify_password", return_value=False):
            with pytest.raises(ValidationException) as exc_info:
                await service.change_password(1, "wrong_password", "new_password123")

        assert "current password is incorrect" in str(exc_info.value.detail).lower()
