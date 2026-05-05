"""Tests for notification_service models."""

from datetime import UTC, datetime, timedelta

from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.models import Notification, NotificationTemplate, ScheduledNotification


class TestNotificationModel:
    """Tests for the Notification model."""

    def test_notification_creation(self):
        """Test creating a Notification instance."""
        notification = Notification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            subject="Test Subject",
            body="Test body content",
            data={"key": "value"},
            status=NotificationStatus.PENDING,
        )

        assert notification.id == 1
        assert notification.user_id == 42
        assert notification.recipient_telegram_id == 123456789
        assert notification.recipient_email == "user@example.com"
        assert notification.type == NotificationType.GENERAL
        assert notification.channel == NotificationChannel.EMAIL
        assert notification.subject == "Test Subject"
        assert notification.body == "Test body content"
        assert notification.data == {"key": "value"}
        assert notification.status == NotificationStatus.PENDING

    def test_notification_repr(self):
        """Test Notification __repr__ method."""
        notification = Notification(
            id=1,
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            status=NotificationStatus.PENDING,
        )

        repr_str = repr(notification)

        assert "Notification" in repr_str
        assert "id=1" in repr_str
        assert "type=GENERAL" in repr_str
        assert "status=PENDING" in repr_str

    def test_notification_repr_different_status(self):
        """Test Notification __repr__ with different status."""
        notification = Notification(
            id=2,
            user_id=43,
            type=NotificationType.TASK_REMINDER,
            channel=NotificationChannel.TELEGRAM,
            body="Task reminder",
            status=NotificationStatus.SENT,
        )

        repr_str = repr(notification)

        assert "id=2" in repr_str
        assert "type=TASK_REMINDER" in repr_str
        assert "status=SENT" in repr_str

    def test_notification_repr_failed_status(self):
        """Test Notification __repr__ with FAILED status."""
        notification = Notification(
            id=3,
            user_id=44,
            type=NotificationType.ESCALATION,
            channel=NotificationChannel.BOTH,
            body="Escalation",
            status=NotificationStatus.FAILED,
        )

        repr_str = repr(notification)

        assert "id=3" in repr_str
        assert "status=FAILED" in repr_str

    def test_notification_optional_fields(self):
        """Test Notification with optional fields as None."""
        notification = Notification(
            user_id=1,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
        )

        assert notification.recipient_telegram_id is None
        assert notification.recipient_email is None
        assert notification.subject is None
        assert notification.error_message is None
        assert notification.scheduled_for is None
        assert notification.sent_at is None


class TestScheduledNotificationModel:
    """Tests for the ScheduledNotification model."""

    def test_scheduled_notification_creation(self):
        """Test creating a ScheduledNotification instance."""
        scheduled_time = datetime.now(UTC) + timedelta(hours=1)

        notification = ScheduledNotification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.MEETING_REMINDER,
            channel=NotificationChannel.EMAIL,
            subject="Meeting Reminder",
            body="You have a meeting in 15 minutes",
            data={"meeting_id": 123},
            scheduled_time=scheduled_time,
            processed=False,
        )

        assert notification.id == 1
        assert notification.user_id == 42
        assert notification.recipient_telegram_id == 123456789
        assert notification.recipient_email == "user@example.com"
        assert notification.type == NotificationType.MEETING_REMINDER
        assert notification.channel == NotificationChannel.EMAIL
        assert notification.subject == "Meeting Reminder"
        assert notification.body == "You have a meeting in 15 minutes"
        assert notification.data == {"meeting_id": 123}
        assert notification.scheduled_time == scheduled_time
        assert notification.processed is False
        assert notification.processed_at is None

    def test_scheduled_notification_repr(self):
        """Test ScheduledNotification __repr__ method."""
        scheduled_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)

        notification = ScheduledNotification(
            id=1,
            user_id=42,
            type=NotificationType.MEETING_REMINDER,
            channel=NotificationChannel.EMAIL,
            body="Meeting",
            scheduled_time=scheduled_time,
            processed=False,
        )

        repr_str = repr(notification)

        assert "ScheduledNotification" in repr_str
        assert "id=1" in repr_str
        assert "scheduled_time=" in repr_str

    def test_scheduled_notification_repr_processed(self):
        """Test ScheduledNotification __repr__ with processed=True."""
        scheduled_time = datetime(2024, 1, 15, 11, 0, 0, tzinfo=UTC)

        notification = ScheduledNotification(
            id=5,
            user_id=45,
            type=NotificationType.ONBOARDING_EVENT,
            channel=NotificationChannel.TELEGRAM,
            body="Onboarding",
            scheduled_time=scheduled_time,
            processed=True,
            processed_at=datetime.now(UTC),
        )

        repr_str = repr(notification)

        assert "id=5" in repr_str

    def test_scheduled_notification_optional_fields(self):
        """Test ScheduledNotification with optional fields as None."""
        scheduled_time = datetime.now(UTC)

        notification = ScheduledNotification(
            user_id=1,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=scheduled_time,
        )

        assert notification.recipient_telegram_id is None
        assert notification.recipient_email is None
        assert notification.subject is None
        assert notification.processed_at is None

    def test_scheduled_notification_processed_field(self):
        """Test that processed field exists and can be set."""
        scheduled_time = datetime.now(UTC)

        # Test with processed=False
        notification1 = ScheduledNotification(
            user_id=1,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=scheduled_time,
            processed=False,
        )
        assert notification1.processed is False

        # Test with processed=True
        notification2 = ScheduledNotification(
            user_id=1,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=scheduled_time,
            processed=True,
        )
        assert notification2.processed is True

    def test_scheduled_notification_data_jsonb(self):
        """Test ScheduledNotification data field with various types."""
        scheduled_time = datetime.now(UTC)

        # Test with empty dict
        notification1 = ScheduledNotification(
            user_id=1,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=scheduled_time,
            data={},
        )
        assert notification1.data == {}

        # Test with nested data
        notification2 = ScheduledNotification(
            user_id=1,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=scheduled_time,
            data={
                "task_id": 123,
                "nested": {"key": "value"},
                "list": [1, 2, 3],
            },
        )
        assert notification2.data["task_id"] == 123
        assert notification2.data["nested"]["key"] == "value"
        assert notification2.data["list"] == [1, 2, 3]


class TestNotificationTemplateModel:
    """Tests for the NotificationTemplate model."""

    def test_notification_template_repr(self):
        """Test NotificationTemplate __repr__ method (line 49)."""
        template = NotificationTemplate(
            id=1,
            name="welcome_email",
            channel="email",
            language="en",
            subject="Welcome!",
            body_html="<h1>Welcome</h1>",
            body_text="Welcome!",
        )

        repr_str = repr(template)

        assert "NotificationTemplate" in repr_str
        assert "id=1" in repr_str
        assert "name=welcome_email" in repr_str
        assert "channel=email" in repr_str
        assert "lang=en" in repr_str

    def test_notification_template_repr_with_id_none(self):
        """Test NotificationTemplate __repr__ when id is None (before save)."""
        template = NotificationTemplate(
            name="test_template",
            channel="telegram",
            language="ru",
        )

        repr_str = repr(template)

        assert "NotificationTemplate" in repr_str
        assert "id=None" in repr_str
        assert "name=test_template" in repr_str
        assert "channel=telegram" in repr_str
        assert "lang=ru" in repr_str
