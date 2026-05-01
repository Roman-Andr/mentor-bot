"""Unit tests for feedback notification client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from feedback_service.services.notification_client import NotificationClient


class TestNotificationClient:
    """Tests for NotificationClient class."""

    @pytest.fixture
    def notification_client(self) -> NotificationClient:
        """Create a NotificationClient instance."""
        return NotificationClient()

    async def test_notify_comment_reply_with_user_id(self, notification_client: NotificationClient) -> None:
        """Replying to comment with user_id should send both Telegram and email notifications."""
        # Arrange
        with patch.object(notification_client, "_send_notification", new=AsyncMock(return_value=True)) as mock_send:
            # Act
            result = await notification_client.notify_comment_reply(
                comment_id=1,
                original_comment_preview="Test comment",
                reply_text="Test reply",
                replied_by_name="HR Admin",
                user_id=100,
            )

            # Assert
            assert result is True
            assert mock_send.call_count == 2

            # Check Telegram call
            telegram_call = mock_send.call_args_list[0]
            assert telegram_call.kwargs["user_id"] == 100
            assert telegram_call.kwargs["template_name"] == "comment_reply"
            assert telegram_call.kwargs["channel"] == "telegram"
            assert telegram_call.kwargs["variables"]["original_comment_preview"] == "Test comment"
            assert telegram_call.kwargs["variables"]["reply_text"] == "Test reply"
            assert telegram_call.kwargs["variables"]["replied_by_name"] == "HR Admin"

            # Check email call
            email_call = mock_send.call_args_list[1]
            assert email_call.kwargs["user_id"] == 100
            assert email_call.kwargs["template_name"] == "comment_reply"
            assert email_call.kwargs["channel"] == "email"

    async def test_notify_comment_reply_without_user_id(self, notification_client: NotificationClient) -> None:
        """Replying to anonymous comment without user_id should skip notification."""
        # Arrange
        with patch.object(notification_client, "_send_notification", new=AsyncMock(return_value=True)) as mock_send:
            # Act
            result = await notification_client.notify_comment_reply(
                comment_id=1,
                original_comment_preview="Test comment",
                reply_text="Test reply",
                replied_by_name="HR Admin",
                user_id=None,
            )

            # Assert
            assert result is True
            assert mock_send.call_count == 0

    async def test_notify_comment_reply_comment_truncation(self, notification_client: NotificationClient) -> None:
        """Long comment should be truncated in notification."""
        # Arrange
        long_comment = "A" * 150

        with patch.object(notification_client, "_send_notification", new=AsyncMock(return_value=True)) as mock_send:
            # Act
            await notification_client.notify_comment_reply(
                comment_id=1,
                original_comment_preview=long_comment,
                reply_text="Test reply",
                replied_by_name="HR Admin",
                user_id=100,
            )

            # Assert
            call = mock_send.call_args
            preview = call.kwargs["variables"]["original_comment_preview"]
            assert len(preview) <= 103  # 100 + "..."
            assert preview.endswith("...")

    async def test_notify_comment_reply_notification_failure(self, notification_client: NotificationClient) -> None:
        """Notification failure should return False."""
        # Arrange
        with patch.object(notification_client, "_send_notification", new=AsyncMock(return_value=False)) as mock_send:
            # Act
            result = await notification_client.notify_comment_reply(
                comment_id=1,
                original_comment_preview="Test comment",
                reply_text="Test reply",
                replied_by_name="HR Admin",
                user_id=100,
            )

            # Assert
            assert result is False
            assert mock_send.call_count == 2  # Both channels attempted

    async def test_send_notification_success(self, notification_client: NotificationClient) -> None:
        """Test successful notification sending via HTTP."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            # Act
            result = await notification_client._send_notification(
                user_id=100,
                template_name="comment_reply",
                variables={"test": "value"},
                channel="telegram",
            )

            # Assert
            assert result is True
            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args.kwargs
            assert call_kwargs["json"]["user_id"] == 100
            assert call_kwargs["json"]["template_name"] == "comment_reply"
            assert call_kwargs["headers"]["X-Service-Key"] == notification_client.api_key
            mock_response.raise_for_status.assert_called_once()
