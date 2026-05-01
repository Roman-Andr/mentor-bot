"""Unit tests for notification_service/schemas/notification.py."""

from datetime import UTC, datetime, timedelta

import pytest
from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.schemas.notification import (
    NotificationBase,
    NotificationCreate,
    NotificationResponse,
    ScheduledNotificationCreate,
    ScheduledNotificationResponse,
)
from pydantic import ValidationError


class TestNotificationBase:
    """Tests for NotificationBase schema."""

    def test_valid_notification_base(self) -> None:
        """Valid data creates NotificationBase."""
        data = {
            "user_id": 42,
            "recipient_telegram_id": 123456789,
            "recipient_email": "user@example.com",
            "type": NotificationType.GENERAL,
            "channel": NotificationChannel.EMAIL,
            "subject": "Test Subject",
            "body": "Test body content",
            "data": {"key": "value"},
        }
        result = NotificationBase(**data)

        assert result.user_id == 42
        assert result.recipient_telegram_id == 123456789
        assert result.recipient_email == "user@example.com"
        assert result.type == NotificationType.GENERAL
        assert result.channel == NotificationChannel.EMAIL
        assert result.subject == "Test Subject"
        assert result.body == "Test body content"
        assert result.data == {"key": "value"}

    def test_default_empty_data(self) -> None:
        """Data defaults to empty dict."""
        data = {
            "user_id": 1,
            "type": NotificationType.GENERAL,
            "channel": NotificationChannel.EMAIL,
            "body": "Test",
        }
        result = NotificationBase(**data)
        assert result.data == {}

    def test_optional_fields(self) -> None:
        """Optional fields can be omitted."""
        data = {
            "user_id": 1,
            "type": NotificationType.GENERAL,
            "channel": NotificationChannel.TELEGRAM,
            "body": "Test without optional fields",
        }
        result = NotificationBase(**data)
        assert result.subject is None
        assert result.recipient_email is None
        assert result.recipient_telegram_id is None

    def test_body_required(self) -> None:
        """Body is required."""
        data = {
            "user_id": 1,
            "type": NotificationType.GENERAL,
            "channel": NotificationChannel.EMAIL,
        }
        with pytest.raises(ValidationError, match="body"):
            NotificationBase(**data)

    def test_body_min_length(self) -> None:
        """Body must be at least 1 character."""
        data = {
            "user_id": 1,
            "type": NotificationType.GENERAL,
            "channel": NotificationChannel.EMAIL,
            "body": "",
        }
        with pytest.raises(ValidationError, match="body"):
            NotificationBase(**data)


class TestNotificationCreate:
    """Tests for NotificationCreate schema."""

    def test_same_fields_as_base(self) -> None:
        """NotificationCreate has same fields as base."""
        data = {
            "user_id": 42,
            "type": NotificationType.MEETING_REMINDER,
            "channel": NotificationChannel.TELEGRAM,
            "body": "Meeting in 30 minutes",
            "recipient_telegram_id": 123456789,
        }
        result = NotificationCreate(**data)
        assert result.user_id == 42
        assert result.type == NotificationType.MEETING_REMINDER


class TestNotificationResponse:
    """Tests for NotificationResponse schema."""

    def test_includes_all_fields(self) -> None:
        """Response includes all base fields plus response fields."""
        now = datetime.now(UTC)
        data = {
            "id": 1,
            "user_id": 42,
            "type": NotificationType.GENERAL,
            "channel": NotificationChannel.EMAIL,
            "body": "Test",
            "status": NotificationStatus.SENT,
            "error_message": None,
            "created_at": now,
            "scheduled_for": None,
            "sent_at": now,
        }
        result = NotificationResponse(**data)

        assert result.id == 1
        assert result.status == NotificationStatus.SENT
        assert result.created_at == now
        assert result.sent_at == now


class TestScheduledNotificationCreate:
    """Tests for ScheduledNotificationCreate schema."""

    def test_includes_scheduled_time(self) -> None:
        """Requires scheduled_time field."""
        future = datetime.now(UTC) + timedelta(hours=1)
        data = {
            "user_id": 42,
            "type": NotificationType.TASK_REMINDER,
            "channel": NotificationChannel.EMAIL,
            "body": "Task due tomorrow",
            "scheduled_time": future,
        }
        result = ScheduledNotificationCreate(**data)
        assert result.scheduled_time == future

    def test_scheduled_time_required(self) -> None:
        """scheduled_time is required."""
        data = {
            "user_id": 42,
            "type": NotificationType.GENERAL,
            "channel": NotificationChannel.EMAIL,
            "body": "Test",
        }
        with pytest.raises(ValidationError, match="scheduled_time"):
            ScheduledNotificationCreate(**data)


class TestScheduledNotificationResponse:
    """Tests for ScheduledNotificationResponse schema."""

    def test_includes_response_fields(self) -> None:
        """Response includes processed status and timestamps."""
        now = datetime.now(UTC)
        future = now + timedelta(hours=1)

        data = {
            "id": 1,
            "user_id": 42,
            "type": NotificationType.GENERAL,
            "channel": NotificationChannel.EMAIL,
            "body": "Test",
            "scheduled_time": future,
            "processed": False,
            "processed_at": None,
            "created_at": now,
            "retry_count": 0,
            "max_retries": 3,
            "failed_at": None,
        }
        result = ScheduledNotificationResponse(**data)

        assert result.id == 1
        assert result.processed is False
        assert result.processed_at is None
        assert result.created_at == now
        assert result.retry_count == 0
        assert result.max_retries == 3
        assert result.failed_at is None
