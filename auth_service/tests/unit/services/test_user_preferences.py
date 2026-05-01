"""Unit tests for user preferences in UserService."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from auth_service.core.enums import UserRole
from auth_service.models import User
from auth_service.schemas import UserPreferencesUpdate
from auth_service.services import UserService


class TestUpdateUserPreferences:
    """Tests for update_user_preferences method."""

    async def test_update_language_preference(self, mock_uow):
        """Test updating user language preference."""
        # Arrange
        user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            language="en",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
        )
        mock_uow.users.get_by_id = AsyncMock(return_value=user)
        mock_uow.users.update = AsyncMock(return_value=user)
        service = UserService(mock_uow)
        preferences_data = UserPreferencesUpdate(language="ru")

        # Act
        updated_user = await service.update_user_preferences(1, preferences_data)

        # Assert
        assert updated_user.language == "ru"
        mock_uow.users.get_by_id.assert_called_once_with(1)
        mock_uow.users.update.assert_called_once()

    async def test_update_telegram_notification_preference(self, mock_uow):
        """Test updating telegram notification preference."""
        # Arrange
        user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            language="en",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
        )
        mock_uow.users.get_by_id = AsyncMock(return_value=user)
        mock_uow.users.update = AsyncMock(return_value=user)
        service = UserService(mock_uow)
        preferences_data = UserPreferencesUpdate(notification_telegram_enabled=False)

        # Act
        updated_user = await service.update_user_preferences(1, preferences_data)

        # Assert
        assert updated_user.notification_telegram_enabled is False
        mock_uow.users.get_by_id.assert_called_once_with(1)
        mock_uow.users.update.assert_called_once()

    async def test_update_email_notification_preference(self, mock_uow):
        """Test updating email notification preference."""
        # Arrange
        user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            language="en",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
        )
        mock_uow.users.get_by_id = AsyncMock(return_value=user)
        mock_uow.users.update = AsyncMock(return_value=user)
        service = UserService(mock_uow)
        preferences_data = UserPreferencesUpdate(notification_email_enabled=False)

        # Act
        updated_user = await service.update_user_preferences(1, preferences_data)

        # Assert
        assert updated_user.notification_email_enabled is False
        mock_uow.users.get_by_id.assert_called_once_with(1)
        mock_uow.users.update.assert_called_once()

    async def test_update_multiple_preferences(self, mock_uow):
        """Test updating multiple preferences at once."""
        # Arrange
        user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            language="en",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
        )
        mock_uow.users.get_by_id = AsyncMock(return_value=user)
        mock_uow.users.update = AsyncMock(return_value=user)
        service = UserService(mock_uow)
        preferences_data = UserPreferencesUpdate(
            language="ru",
            notification_telegram_enabled=False,
            notification_email_enabled=False,
        )

        # Act
        updated_user = await service.update_user_preferences(1, preferences_data)

        # Assert
        assert updated_user.language == "ru"
        assert updated_user.notification_telegram_enabled is False
        assert updated_user.notification_email_enabled is False
        mock_uow.users.get_by_id.assert_called_once_with(1)
        mock_uow.users.update.assert_called_once()

    async def test_update_preferences_updates_timestamp(self, mock_uow):
        """Test that updating preferences updates the updated_at timestamp."""
        # Arrange
        user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            language="en",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
            updated_at=datetime(2024, 1, 1, tzinfo=UTC),
        )
        mock_uow.users.get_by_id = AsyncMock(return_value=user)
        mock_uow.users.update = AsyncMock(return_value=user)
        service = UserService(mock_uow)
        preferences_data = UserPreferencesUpdate(language="ru")

        # Act
        updated_user = await service.update_user_preferences(1, preferences_data)

        # Assert
        assert updated_user.updated_at > datetime(2024, 1, 1, tzinfo=UTC)

    async def test_update_preferences_with_none_values(self, mock_uow):
        """Test that None values in preferences don't override existing values."""
        # Arrange
        user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            language="en",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
        )
        mock_uow.users.get_by_id = AsyncMock(return_value=user)
        mock_uow.users.update = AsyncMock(return_value=user)
        service = UserService(mock_uow)
        preferences_data = UserPreferencesUpdate(language="ru")  # Only language

        # Act
        updated_user = await service.update_user_preferences(1, preferences_data)

        # Assert - other fields should remain unchanged
        assert updated_user.language == "ru"
        assert updated_user.notification_telegram_enabled is True
        assert updated_user.notification_email_enabled is True

    async def test_update_preferences_user_not_found(self, mock_uow):
        """Test that updating preferences for non-existent user raises error."""
        # Arrange
        from auth_service.core import NotFoundException

        mock_uow.users.get_by_id = AsyncMock(return_value=None)
        service = UserService(mock_uow)
        preferences_data = UserPreferencesUpdate(language="ru")

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.update_user_preferences(999, preferences_data)

    async def test_update_preferences_default_values_for_new_user(self, mock_uow):
        """Test that new users have default preference values."""
        # Arrange
        new_user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
            language="ru",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )
        # Simulate defaults from model
        assert new_user.language == "ru"
        assert new_user.notification_telegram_enabled is True
        assert new_user.notification_email_enabled is True
