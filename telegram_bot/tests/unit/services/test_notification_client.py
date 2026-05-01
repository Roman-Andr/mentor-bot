"""Unit tests for telegram_bot NotificationServiceClient."""

from typing import Never

import pytest
from fastapi import status
from httpx import RequestError, Response
from telegram_bot.services.notification_client import NotificationServiceClient


@pytest.fixture
def notification_client():
    """Create a notification client with test base URL."""
    return NotificationServiceClient(base_url="http://test-notification:8004")


class TestSendTelegramNotification:
    """Test cases for send_telegram_notification method."""

    async def test_send_telegram_notification_success(self, notification_client, monkeypatch):
        """Test successful Telegram notification sending."""
        mock_data = {"id": 1, "status": "sent"}

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_telegram_notification(
            user_id=1,
            title="Test Notification",
            message="Test message",
            auth_token="test-token",
        )
        assert result is not None
        assert result["status"] == "sent"

    async def test_send_telegram_notification_with_priority(self, notification_client, monkeypatch):
        """Test Telegram notification with custom priority."""
        captured_json = {}

        async def mock_post(*args, **kwargs):
            captured_json["data"] = kwargs.get("json", {})
            return Response(status_code=status.HTTP_200_OK, json={"id": 1})

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_telegram_notification(
            user_id=1,
            title="Test",
            message="Test",
            auth_token="test-token",
            priority="high",
        )
        assert result is not None
        assert captured_json["data"].get("priority") == "high"

    async def test_send_telegram_notification_failure(self, notification_client, monkeypatch):
        """Test failed Telegram notification sending."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_telegram_notification(
            user_id=1,
            title="Test",
            message="Test",
            auth_token="test-token",
        )
        assert result is None

    async def test_send_telegram_notification_request_error(self, notification_client, monkeypatch):
        """Test Telegram notification with request error."""

        async def mock_post(*args, **kwargs) -> Never:
            msg = "Connection failed"
            raise RequestError(msg)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_telegram_notification(
            user_id=1,
            title="Test",
            message="Test",
            auth_token="test-token",
        )
        assert result is None


class TestSendEmailNotification:
    """Test cases for send_email_notification method."""

    async def test_send_email_notification_success(self, notification_client, monkeypatch):
        """Test successful email notification sending."""
        mock_data = {"id": 1, "status": "sent"}

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_email_notification(
            email="test@example.com",
            subject="Test Subject",
            message="Test body",
            auth_token="test-token",
        )
        assert result is not None

    async def test_send_email_notification_failure(self, notification_client, monkeypatch):
        """Test failed email notification sending."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_email_notification(
            email="test@example.com",
            subject="Test",
            message="Test",
            auth_token="test-token",
        )
        assert result is None

    async def test_send_email_notification_request_error(self, notification_client, monkeypatch):
        """Test email notification with request error."""

        async def mock_post(*args, **kwargs) -> Never:
            msg = "Connection failed"
            raise RequestError(msg)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_email_notification(
            email="test@example.com",
            subject="Test",
            message="Test",
            auth_token="test-token",
        )
        assert result is None


class TestScheduleNotification:
    """Test cases for schedule_notification method."""

    async def test_schedule_notification_success(self, notification_client, monkeypatch):
        """Test successful notification scheduling."""
        mock_data = {"id": 1, "scheduled": True}

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.schedule_notification(
            user_id=1,
            message="Test message",
            send_at="2024-01-01T10:00:00",
            auth_token="test-token",
        )
        assert result is not None
        assert result["scheduled"] is True

    async def test_schedule_notification_with_channel(self, notification_client, monkeypatch):
        """Test notification scheduling with custom channel."""
        captured_json = {}

        async def mock_post(*args, **kwargs):
            captured_json["data"] = kwargs.get("json", {})
            return Response(status_code=status.HTTP_200_OK, json={"id": 1})

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.schedule_notification(
            user_id=1,
            message="Test",
            send_at="2024-01-01T10:00:00",
            auth_token="test-token",
            channel="email",
        )
        assert result is not None
        assert captured_json["data"].get("channel") == "email"

    async def test_schedule_notification_failure(self, notification_client, monkeypatch):
        """Test failed notification scheduling."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.schedule_notification(
            user_id=1,
            message="Test",
            send_at="2024-01-01T10:00:00",
            auth_token="test-token",
        )
        assert result is None

    async def test_schedule_notification_request_error(self, notification_client, monkeypatch):
        """Test notification scheduling with request error."""

        async def mock_post(*args, **kwargs) -> Never:
            msg = "Connection failed"
            raise RequestError(msg)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.schedule_notification(
            user_id=1,
            message="Test",
            send_at="2024-01-01T10:00:00",
            auth_token="test-token",
        )
        assert result is None


class TestGetUserNotifications:
    """Test cases for get_user_notifications method."""

    async def test_get_user_notifications_success(self, notification_client, monkeypatch):
        """Test successful user notifications retrieval."""
        mock_data = {"notifications": [{"id": 1, "message": "Test"}]}

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(notification_client.client, "get", mock_get)

        result = await notification_client.get_user_notifications(1, "test-token")
        assert len(result) == 1

    async def test_get_user_notifications_empty(self, notification_client, monkeypatch):
        """Test user notifications retrieval with empty result."""

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json={"notifications": []})

        monkeypatch.setattr(notification_client.client, "get", mock_get)

        result = await notification_client.get_user_notifications(1, "test-token")
        assert result == []

    async def test_get_user_notifications_failure(self, notification_client, monkeypatch):
        """Test failed user notifications retrieval."""

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        monkeypatch.setattr(notification_client.client, "get", mock_get)

        result = await notification_client.get_user_notifications(1, "test-token")
        assert result == []

    async def test_get_user_notifications_request_error(self, notification_client, monkeypatch):
        """Test user notifications retrieval with request error."""

        async def mock_get(*args, **kwargs) -> Never:
            msg = "Connection failed"
            raise RequestError(msg)

        monkeypatch.setattr(notification_client.client, "get", mock_get)

        result = await notification_client.get_user_notifications(1, "test-token")
        assert result == []


class TestSendTaskReminder:
    """Test cases for send_task_reminder method."""

    async def test_send_task_reminder_success(self, notification_client, monkeypatch):
        """Test successful task reminder sending."""
        mock_data = {"id": 1, "status": "sent"}
        captured_json = {}

        async def mock_post(*args, **kwargs):
            captured_json["data"] = kwargs.get("json", {})
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_task_reminder(
            telegram_id=123,
            task_title="Important Task",
            due_date="2024-01-01",
            auth_token="test-token",
        )
        assert result is not None
        # Verify message contains task title and due date
        assert "Important Task" in captured_json["data"].get("message", "")
        assert captured_json["data"].get("priority") == "high"

    async def test_send_task_reminder_failure(self, notification_client, monkeypatch):
        """Test failed task reminder sending."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_task_reminder(
            telegram_id=123,
            task_title="Test",
            due_date="2024-01-01",
            auth_token="test-token",
        )
        assert result is None


class TestSendMeetingReminder:
    """Test cases for send_meeting_reminder method."""

    async def test_send_meeting_reminder_success(self, notification_client, monkeypatch):
        """Test successful meeting reminder sending."""
        mock_data = {"id": 1, "status": "sent"}

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_meeting_reminder(
            telegram_id=123,
            meeting_title="Team Standup",
            meeting_time="10:00 AM",
            auth_token="test-token",
        )
        assert result is not None

    async def test_send_meeting_reminder_failure(self, notification_client, monkeypatch):
        """Test failed meeting reminder sending."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        monkeypatch.setattr(notification_client.client, "post", mock_post)

        result = await notification_client.send_meeting_reminder(
            telegram_id=123,
            meeting_title="Test",
            meeting_time="10:00",
            auth_token="test-token",
        )
        assert result is None


class TestGetActiveReminders:
    """Test cases for get_active_reminders method."""

    async def test_get_active_reminders_success(self, notification_client, monkeypatch):
        """Test successful active reminders retrieval."""
        mock_data = [{"id": 1, "message": "Reminder 1"}, {"id": 2, "message": "Reminder 2"}]

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(notification_client.client, "get", mock_get)

        result = await notification_client.get_active_reminders("test-token")
        assert len(result) == 2

    async def test_get_active_reminders_empty(self, notification_client, monkeypatch):
        """Test active reminders retrieval with empty result."""

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=[])

        monkeypatch.setattr(notification_client.client, "get", mock_get)

        result = await notification_client.get_active_reminders("test-token")
        assert result == []

    async def test_get_active_reminders_failure(self, notification_client, monkeypatch):
        """Test failed active reminders retrieval."""

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        monkeypatch.setattr(notification_client.client, "get", mock_get)

        result = await notification_client.get_active_reminders("test-token")
        assert result == []

    async def test_get_active_reminders_request_error(self, notification_client, monkeypatch):
        """Test active reminders retrieval with request error."""

        async def mock_get(*args, **kwargs) -> Never:
            msg = "Connection failed"
            raise RequestError(msg)

        monkeypatch.setattr(notification_client.client, "get", mock_get)

        result = await notification_client.get_active_reminders("test-token")
        assert result == []
