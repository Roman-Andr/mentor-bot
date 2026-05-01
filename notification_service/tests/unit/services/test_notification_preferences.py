"""Unit tests for notification service preferences integration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.models import Notification
from notification_service.services import NotificationService
from notification_service.services.auth_client import AuthClientError, UserPreferences


class TestNotificationPreferences:
    """Tests for notification service checking user preferences."""

    async def test_skip_telegram_when_disabled(self, mock_uow):
        """Test that telegram notifications are skipped when user disabled them."""
        # Arrange
        notification = Notification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.TELEGRAM,
            subject="Test Subject",
            body="Test body content",
            data={},
            status=NotificationStatus.PENDING,
        )

        service = NotificationService(mock_uow)

        # Mock auth_client to return disabled telegram preference
        mock_prefs = UserPreferences(
            language="en",
            notification_telegram_enabled=False,
            notification_email_enabled=True,
        )

        with patch.object(service._auth_client, "get_user_preferences", new_callable=AsyncMock, return_value=mock_prefs):
            # Act
            success, error = await service._send_telegram(notification, mock_prefs)

        # Assert
        assert success is True  # Returns success to avoid retry
        assert error is None

    async def test_skip_email_when_disabled(self, mock_uow):
        """Test that email notifications are skipped when user disabled them."""
        # Arrange
        notification = Notification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            subject="Test Subject",
            body="Test body content",
            data={},
            status=NotificationStatus.PENDING,
        )

        service = NotificationService(mock_uow)

        # Mock auth_client to return disabled email preference
        mock_prefs = UserPreferences(
            language="en",
            notification_telegram_enabled=True,
            notification_email_enabled=False,
        )

        with patch.object(service._auth_client, "get_user_preferences", new_callable=AsyncMock, return_value=mock_prefs):
            # Act
            success, error = await service._send_email(notification, mock_prefs)

        # Assert
        assert success is True  # Returns success to avoid retry
        assert error is None

    async def test_skip_both_when_disabled(self, mock_uow):
        """Test that both channels are skipped when user disabled both."""
        # Arrange
        notification = Notification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.BOTH,
            subject="Test Subject",
            body="Test body content",
            data={},
            status=NotificationStatus.PENDING,
        )

        service = NotificationService(mock_uow)

        # Mock auth_client to return both disabled
        mock_prefs = UserPreferences(
            language="en",
            notification_telegram_enabled=False,
            notification_email_enabled=False,
        )

        with patch.object(service._auth_client, "get_user_preferences", new_callable=AsyncMock, return_value=mock_prefs):
            # Act
            success, error = await service._send_both(notification, mock_prefs)

        # Assert
        assert success is True  # Returns success to avoid retry
        assert error is None

    async def test_send_telegram_when_enabled(self, mock_uow):
        """Test that telegram notifications are sent when user enabled them."""
        # Arrange
        notification = Notification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.TELEGRAM,
            subject="Test Subject",
            body="Test body content",
            data={},
            status=NotificationStatus.PENDING,
        )

        service = NotificationService(mock_uow)

        # Mock auth_client to return enabled telegram preference
        mock_prefs = UserPreferences(
            language="en",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )

        # Mock telegram service to succeed
        with patch.object(service._telegram, "send_message", new_callable=AsyncMock, return_value=True):
            with patch.object(service._auth_client, "get_user_preferences", new_callable=AsyncMock, return_value=mock_prefs):
                # Act
                success, error = await service._send_telegram(notification, mock_prefs)

        # Assert
        assert success is True
        assert error is None

    async def test_send_email_when_enabled(self, mock_uow):
        """Test that email notifications are sent when user enabled them."""
        # Arrange
        notification = Notification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            subject="Test Subject",
            body="Test body content",
            data={},
            status=NotificationStatus.PENDING,
        )

        service = NotificationService(mock_uow)

        # Mock auth_client to return enabled email preference
        mock_prefs = UserPreferences(
            language="en",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )

        # Mock email service to succeed
        with patch.object(service._email, "send_email", new_callable=AsyncMock):
            with patch.object(service._auth_client, "get_user_preferences", new_callable=AsyncMock, return_value=mock_prefs):
                # Act
                success, error = await service._send_email(notification, mock_prefs)

        # Assert
        assert success is True
        assert error is None

    async def test_fail_open_on_auth_error(self, mock_uow):
        """Test that notifications are sent even if auth service fails (fail-open)."""
        # Arrange
        notification = Notification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.TELEGRAM,
            subject="Test Subject",
            body="Test body content",
            data={},
            status=NotificationStatus.PENDING,
        )

        service = NotificationService(mock_uow)

        # Mock auth_client to raise error
        with patch.object(service._auth_client, "get_user_preferences", new_callable=AsyncMock, side_effect=AuthClientError("Auth service error")):
            # Mock telegram service to succeed
            with patch.object(service._telegram, "send_message", new_callable=AsyncMock, return_value=True):
                # Act
                success, error = await service._send_to_channel(notification)

        # Assert - should still send (fail-open)
        assert success is True
        assert error is None

    async def test_send_to_channel_fetches_preferences(self, mock_uow):
        """Test that _send_to_channel fetches user preferences."""
        # Arrange
        notification = Notification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.TELEGRAM,
            subject="Test Subject",
            body="Test body content",
            data={},
            status=NotificationStatus.PENDING,
        )

        service = NotificationService(mock_uow)

        # Mock auth_client to return preferences
        mock_prefs = UserPreferences(
            language="en",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )

        with patch.object(service._auth_client, "get_user_preferences", new_callable=AsyncMock, return_value=mock_prefs):
            with patch.object(service._telegram, "send_message", new_callable=AsyncMock, return_value=True):
                # Act
                await service._send_to_channel(notification)

        # Assert
        service._auth_client.get_user_preferences.assert_called_once_with(42)

    async def test_default_preferences_when_none(self, mock_uow):
        """Test that default preferences are used when auth returns None."""
        # Arrange
        notification = Notification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.TELEGRAM,
            subject="Test Subject",
            body="Test body content",
            data={},
            status=NotificationStatus.PENDING,
        )

        service = NotificationService(mock_uow)

        # Mock auth_client to return None (fail-open)
        with patch.object(service._auth_client, "get_user_preferences", new_callable=AsyncMock, return_value=None):
            # Mock telegram service to succeed
            with patch.object(service._telegram, "send_message", new_callable=AsyncMock, return_value=True):
                # Act
                success, error = await service._send_to_channel(notification)

        # Assert - should still send (fail-open with None = default enabled)
        assert success is True
        assert error is None
