"""Unit tests for notification_service/services/notification.py."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from _pytest.logging import LogCaptureFixture

from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.models import Notification, ScheduledNotification
from notification_service.schemas import NotificationCreate, ScheduledNotificationCreate
from notification_service.services import NotificationService


class TestNotificationServiceGetUserNotifications:
    """Tests for get_user_notifications method."""

    async def test_get_user_notifications_calls_repository(self, mock_uow: MagicMock) -> None:
        """Method delegates to repository with correct parameters."""
        service = NotificationService(mock_uow)
        user_id = 42
        skip = 10
        limit = 20

        mock_notifications = [
            MagicMock(spec=Notification),
            MagicMock(spec=Notification),
        ]
        mock_uow.notifications.get_user_notifications.return_value = mock_notifications

        result = await service.get_user_notifications(user_id, skip, limit)

        assert result == mock_notifications
        mock_uow.notifications.get_user_notifications.assert_awaited_once_with(user_id, skip, limit)

    async def test_get_user_notifications_with_default_pagination(self, mock_uow: MagicMock) -> None:
        """Default pagination values are used when not specified."""
        service = NotificationService(mock_uow)
        user_id = 42

        await service.get_user_notifications(user_id)

        mock_uow.notifications.get_user_notifications.assert_awaited_once_with(user_id, 0, 100)


class TestNotificationServiceFindNotifications:
    """Tests for find_notifications method."""

    async def test_find_notifications_delegates_to_repository(self, mock_uow: MagicMock) -> None:
        """Method delegates to repository with correct parameters."""
        service = NotificationService(mock_uow)

        mock_items = [MagicMock(spec=Notification), MagicMock(spec=Notification)]
        mock_uow.notifications.find_notifications.return_value = (mock_items, 10)

        result = await service.find_notifications(
            skip=5,
            limit=20,
            user_id=42,
            notification_type=NotificationType.GENERAL,
            status=NotificationStatus.SENT,
            sort_by="created_at",
            sort_order="asc",
        )

        assert result == (mock_items, 10)
        mock_uow.notifications.find_notifications.assert_awaited_once_with(
            skip=5,
            limit=20,
            user_id=42,
            notification_type=NotificationType.GENERAL,
            status=NotificationStatus.SENT,
            sort_by="created_at",
            sort_order="asc",
        )

    async def test_find_notifications_returns_list(self, mock_uow: MagicMock) -> None:
        """Returns list of notifications and total count."""
        service = NotificationService(mock_uow)

        mock_items = [MagicMock(spec=Notification)]
        mock_uow.notifications.find_notifications.return_value = (mock_items, 1)

        result = await service.find_notifications()

        assert isinstance(result[0], list)
        assert result[1] == 1

    async def test_find_notifications_with_defaults(self, mock_uow: MagicMock) -> None:
        """Uses default values when parameters not provided."""
        service = NotificationService(mock_uow)

        mock_uow.notifications.find_notifications.return_value = ([], 0)

        await service.find_notifications()

        mock_uow.notifications.find_notifications.assert_awaited_once_with(
            skip=0,
            limit=100,
            user_id=None,
            notification_type=None,
            status=None,
            sort_by=None,
            sort_order="desc",
        )


class TestNotificationServiceSendImmediate:
    """Tests for send_immediate method."""

    async def test_creates_notification_record(self, mock_uow: MagicMock) -> None:
        """Creates notification record in database."""
        service = NotificationService(mock_uow)

        notification_data = NotificationCreate(
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            subject="Test Subject",
            body="Test body",
            data={"key": "value"},
        )

        now = datetime.now(UTC)
        mock_saved = Notification(
            id=1,
            user_id=notification_data.user_id,
            type=notification_data.type,
            channel=notification_data.channel,
            body=notification_data.body,
            status=NotificationStatus.PENDING,
        )

        mock_sent = Notification(
            id=1,
            status=NotificationStatus.SENT,
            sent_at=now,
        )

        mock_uow.notifications.create = AsyncMock(return_value=mock_saved)
        mock_uow.notifications.update = AsyncMock(return_value=mock_sent)

        with patch.object(service, "_send_to_channel", return_value=(True, None)):
            await service.send_immediate(notification_data)

        mock_uow.notifications.create.assert_awaited_once()
        call_notification = mock_uow.notifications.create.call_args[0][0]
        assert isinstance(call_notification, Notification)
        assert call_notification.user_id == notification_data.user_id
        assert call_notification.status == NotificationStatus.PENDING

    async def test_sends_via_email_channel(self, mock_uow: MagicMock) -> None:
        """Email channel notifications are sent via email."""
        service = NotificationService(mock_uow)

        notification_data = NotificationCreate(
            user_id=42,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test email",
        )

        mock_saved = Notification(
            id=1,
            channel=NotificationChannel.EMAIL,
            status=NotificationStatus.PENDING,
        )

        mock_uow.notifications.create = AsyncMock(return_value=mock_saved)
        mock_uow.notifications.update = AsyncMock(return_value=mock_saved)

        with patch.object(service, "_send_email", return_value=(True, None)) as mock_send_email:
            with patch.object(service, "_send_telegram", return_value=(True, None)):
                await service.send_immediate(notification_data)
                mock_send_email.assert_awaited_once()

    async def test_sends_via_telegram_channel(self, mock_uow: MagicMock) -> None:
        """Telegram channel notifications are sent via Telegram."""
        service = NotificationService(mock_uow)

        notification_data = NotificationCreate(
            user_id=42,
            recipient_telegram_id=123456789,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.TELEGRAM,
            body="Test telegram message",
        )

        mock_saved = Notification(
            id=1,
            channel=NotificationChannel.TELEGRAM,
            status=NotificationStatus.PENDING,
        )

        mock_uow.notifications.create = AsyncMock(return_value=mock_saved)
        mock_uow.notifications.update = AsyncMock(return_value=mock_saved)

        with patch.object(service, "_send_telegram", return_value=(True, None)) as mock_send_telegram:
            with patch.object(service, "_send_email", return_value=(True, None)):
                await service.send_immediate(notification_data)
                mock_send_telegram.assert_awaited_once()

    async def test_sends_via_both_channels(self, mock_uow: MagicMock) -> None:
        """BOTH channel sends via both Telegram and Email."""
        service = NotificationService(mock_uow)

        notification_data = NotificationCreate(
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.BOTH,
            body="Test both channels",
        )

        mock_saved = Notification(
            id=1,
            channel=NotificationChannel.BOTH,
            status=NotificationStatus.PENDING,
        )

        mock_uow.notifications.create = AsyncMock(return_value=mock_saved)
        mock_uow.notifications.update = AsyncMock(return_value=mock_saved)

        with patch.object(service, "_send_both", return_value=(True, None)) as mock_send_both:
            await service.send_immediate(notification_data)
            mock_send_both.assert_awaited_once()

    async def test_marks_as_sent_on_success(self, mock_uow: MagicMock) -> None:
        """Notification is marked as SENT when delivery succeeds."""
        service = NotificationService(mock_uow)

        notification_data = NotificationCreate(
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
        )

        mock_saved = Notification(
            id=1,
            status=NotificationStatus.PENDING,
        )

        mock_uow.notifications.create = AsyncMock(return_value=mock_saved)
        mock_uow.notifications.update = AsyncMock(return_value=mock_saved)

        with patch.object(service, "_send_to_channel", return_value=(True, None)):
            await service.send_immediate(notification_data)

        # Check that update was called with SENT status
        updated_notification = mock_uow.notifications.update.call_args[0][0]
        assert updated_notification.status == NotificationStatus.SENT
        assert updated_notification.sent_at is not None

    async def test_marks_as_failed_on_send_failure(self, mock_uow: MagicMock) -> None:
        """Notification is marked as FAILED when delivery fails."""
        service = NotificationService(mock_uow)

        notification_data = NotificationCreate(
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
        )

        mock_saved = Notification(
            id=1,
            status=NotificationStatus.PENDING,
        )

        mock_uow.notifications.create = AsyncMock(return_value=mock_saved)
        mock_uow.notifications.update = AsyncMock(return_value=mock_saved)

        with patch.object(service, "_send_to_channel", return_value=(False, "SMTP error")):
            await service.send_immediate(notification_data)

        updated_notification = mock_uow.notifications.update.call_args[0][0]
        assert updated_notification.status == NotificationStatus.FAILED
        assert updated_notification.error_message == "SMTP error"
        assert updated_notification.sent_at is None

    async def test_commits_after_sending(self, mock_uow: MagicMock) -> None:
        """Changes are committed after sending notification."""
        service = NotificationService(mock_uow)

        notification_data = NotificationCreate(
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
        )

        mock_saved = Notification(id=1, status=NotificationStatus.PENDING)
        mock_uow.notifications.create = AsyncMock(return_value=mock_saved)
        mock_uow.notifications.update = AsyncMock(return_value=mock_saved)

        with patch.object(service, "_send_to_channel", return_value=(True, None)):
            await service.send_immediate(notification_data)

        mock_uow.commit.assert_awaited_once()


class TestNotificationServiceSchedule:
    """Tests for schedule method."""

    async def test_creates_scheduled_notification(self, mock_uow: MagicMock) -> None:
        """Creates scheduled notification record."""
        service = NotificationService(mock_uow)

        schedule_data = ScheduledNotificationCreate(
            user_id=42,
            recipient_email="user@example.com",
            type=NotificationType.MEETING_REMINDER,
            channel=NotificationChannel.EMAIL,
            body="Meeting reminder",
            scheduled_time=datetime.now(UTC) + timedelta(hours=1),
        )

        mock_scheduled = ScheduledNotification(
            id=1,
            user_id=42,
            processed=False,
        )

        mock_uow.scheduled_notifications.create = AsyncMock(return_value=mock_scheduled)

        await service.schedule(schedule_data)

        mock_uow.scheduled_notifications.create.assert_awaited_once()
        call_scheduled = mock_uow.scheduled_notifications.create.call_args[0][0]
        assert isinstance(call_scheduled, ScheduledNotification)
        assert call_scheduled.user_id == schedule_data.user_id
        assert call_scheduled.processed is False

    async def test_commits_after_scheduling(self, mock_uow: MagicMock) -> None:
        """Changes are committed after creating scheduled notification."""
        service = NotificationService(mock_uow)

        schedule_data = ScheduledNotificationCreate(
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=datetime.now(UTC),
        )

        mock_uow.scheduled_notifications.create = AsyncMock(return_value=MagicMock())

        await service.schedule(schedule_data)

        mock_uow.commit.assert_awaited_once()


class TestNotificationServiceProcessScheduled:
    """Tests for process_scheduled method."""

    async def test_fetches_pending_notifications(self, mock_uow: MagicMock) -> None:
        """Fetches pending notifications scheduled before now."""
        service = NotificationService(mock_uow)

        mock_uow.scheduled_notifications.find_pending_before.return_value = []

        await service.process_scheduled()

        mock_uow.scheduled_notifications.find_pending_before.assert_awaited_once()
        # Should be called with a datetime close to now
        call_time = mock_uow.scheduled_notifications.find_pending_before.call_args[0][0]
        assert isinstance(call_time, datetime)

    async def test_creates_notification_for_each_scheduled(self, mock_uow: MagicMock) -> None:
        """Creates notification records for each due scheduled notification."""
        service = NotificationService(mock_uow)

        now = datetime.now(UTC)
        scheduled_notifications = [
            ScheduledNotification(
                id=1,
                user_id=42,
                type=NotificationType.MEETING_REMINDER,
                channel=NotificationChannel.EMAIL,
                body="Meeting in 10 min",
                scheduled_time=now - timedelta(minutes=5),
                processed=False,
                retry_count=0,
                max_retries=3,
            ),
            ScheduledNotification(
                id=2,
                user_id=43,
                type=NotificationType.TASK_REMINDER,
                channel=NotificationChannel.TELEGRAM,
                body="Task due",
                scheduled_time=now - timedelta(minutes=10),
                processed=False,
                retry_count=0,
                max_retries=3,
            ),
        ]

        mock_uow.scheduled_notifications.find_pending_before.return_value = scheduled_notifications
        mock_uow.notifications.create = AsyncMock(return_value=MagicMock())
        mock_uow.notifications.update = AsyncMock(return_value=MagicMock())
        mock_uow.scheduled_notifications.mark_processed = AsyncMock()
        mock_uow.scheduled_notifications.increment_retry = AsyncMock()

        with patch.object(service, "_send_to_channel", return_value=(True, None)):
            await service.process_scheduled()

        assert mock_uow.notifications.create.await_count == 2

    async def test_marks_scheduled_as_processed(self, mock_uow: MagicMock) -> None:
        """Marks scheduled notifications as processed after sending."""
        service = NotificationService(mock_uow)

        now = datetime.now(UTC)
        scheduled = ScheduledNotification(
            id=1,
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=now - timedelta(minutes=5),
            processed=False,
            retry_count=0,
            max_retries=3,
        )

        mock_uow.scheduled_notifications.find_pending_before.return_value = [scheduled]
        mock_uow.notifications.create = AsyncMock(return_value=Notification(id=1))
        mock_uow.notifications.update = AsyncMock(return_value=Notification(id=1))
        mock_uow.scheduled_notifications.increment_retry = AsyncMock()

        with patch.object(service, "_send_to_channel", return_value=(True, None)):
            await service.process_scheduled()

        mock_uow.scheduled_notifications.mark_processed.assert_awaited_once_with(scheduled.id)

    async def test_commits_after_processing(self, mock_uow: MagicMock) -> None:
        """Commits changes after processing scheduled notifications."""
        service = NotificationService(mock_uow)

        now = datetime.now(UTC)
        scheduled = ScheduledNotification(
            id=1,
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=now - timedelta(minutes=5),
            processed=False,
            retry_count=0,
            max_retries=3,
        )

        mock_uow.scheduled_notifications.find_pending_before.return_value = [scheduled]
        mock_uow.notifications.create = AsyncMock(return_value=Notification(id=1))
        mock_uow.notifications.update = AsyncMock(return_value=Notification(id=1))
        mock_uow.scheduled_notifications.increment_retry = AsyncMock()

        with patch.object(service, "_send_to_channel", return_value=(True, None)):
            await service.process_scheduled()

        mock_uow.commit.assert_awaited_once()

    async def test_returns_sent_notifications(self, mock_uow: MagicMock) -> None:
        """Returns list of sent notifications."""
        service = NotificationService(mock_uow)

        now = datetime.now(UTC)
        scheduled = ScheduledNotification(
            id=1,
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=now - timedelta(minutes=5),
            processed=False,
            retry_count=0,
            max_retries=3,
        )

        sent_notification = Notification(
            id=100,
            user_id=42,
            status=NotificationStatus.SENT,
            sent_at=now,
        )

        mock_uow.scheduled_notifications.find_pending_before.return_value = [scheduled]
        mock_uow.notifications.create = AsyncMock(return_value=Notification(id=100))
        mock_uow.notifications.update = AsyncMock(return_value=sent_notification)
        mock_uow.scheduled_notifications.increment_retry = AsyncMock()

        with patch.object(service, "_send_to_channel", return_value=(True, None)):
            result = await service.process_scheduled()

        assert len(result) == 1
        assert result[0].id == 100

    async def test_handles_send_failure_during_processing(self, mock_uow: MagicMock) -> None:
        """Retries failed sends with exponential backoff."""
        service = NotificationService(mock_uow)

        now = datetime.now(UTC)
        scheduled_list = [
            ScheduledNotification(
                id=1,
                user_id=42,
                type=NotificationType.GENERAL,
                channel=NotificationChannel.EMAIL,
                body="First",
                scheduled_time=now - timedelta(minutes=5),
                processed=False,
                retry_count=0,
                max_retries=3,
            ),
            ScheduledNotification(
                id=2,
                user_id=43,
                type=NotificationType.GENERAL,
                channel=NotificationChannel.EMAIL,
                body="Second",
                scheduled_time=now - timedelta(minutes=10),
                processed=False,
                retry_count=0,
                max_retries=3,
            ),
        ]

        mock_uow.scheduled_notifications.find_pending_before.return_value = scheduled_list
        mock_uow.notifications.create = AsyncMock(side_effect=[
            Notification(id=1),
            Notification(id=2),
        ])
        mock_uow.notifications.update = AsyncMock(side_effect=[
            Notification(id=1, status=NotificationStatus.FAILED, error_message="Error"),
            Notification(id=2, status=NotificationStatus.SENT, sent_at=now),
        ])
        mock_uow.scheduled_notifications.increment_retry = AsyncMock()

        # First send fails, second succeeds
        send_results = [(False, "Error"), (True, None)]
        with patch.object(service, "_send_to_channel", side_effect=send_results):
            result = await service.process_scheduled()

        assert len(result) == 2
        # First should increment retry (not yet processed), second should be marked as processed
        mock_uow.scheduled_notifications.increment_retry.assert_awaited_once()
        call_args = mock_uow.scheduled_notifications.increment_retry.await_args
        assert call_args[0][0] == 1  # First notification ID
        # Scheduled time should be ~1 minute in the future (2^0 = 1 min backoff)
        assert call_args[0][1] > now
        assert call_args[0][1] <= now + timedelta(minutes=2)
        mock_uow.scheduled_notifications.mark_processed.assert_awaited_once_with(2)

    async def test_skips_when_max_retries_exceeded(self, mock_uow: MagicMock, caplog: LogCaptureFixture) -> None:
        """Test lines 116-117: Skips processing when retry_count >= max_retries."""
        caplog.set_level("WARNING")
        service = NotificationService(mock_uow)

        now = datetime.now(UTC)
        scheduled = ScheduledNotification(
            id=1,
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=now - timedelta(minutes=5),
            processed=False,
            retry_count=3,  # Already at max_retries
            max_retries=3,
        )

        mock_uow.scheduled_notifications.find_pending_before.return_value = [scheduled]
        mock_uow.scheduled_notifications.mark_processed = AsyncMock()

        # Should skip without sending
        with patch.object(service, "_send_to_channel") as mock_send:
            result = await service.process_scheduled()

        # Should mark as processed immediately without sending
        mock_send.assert_not_called()
        mock_uow.notifications.create.assert_not_called()
        mock_uow.scheduled_notifications.mark_processed.assert_awaited_once_with(1)
        assert result == []  # No notifications sent

    async def test_marks_processed_when_max_retries_reached_on_failure(self, mock_uow: MagicMock, caplog: LogCaptureFixture) -> None:
        """Test lines 147-148: Marks as processed when max retries reached on failure."""
        caplog.set_level("WARNING")
        service = NotificationService(mock_uow)

        now = datetime.now(UTC)
        scheduled = ScheduledNotification(
            id=1,
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=now - timedelta(minutes=5),
            processed=False,
            retry_count=2,  # One away from max
            max_retries=3,
        )

        mock_uow.scheduled_notifications.find_pending_before.return_value = [scheduled]
        mock_uow.notifications.create = AsyncMock(return_value=Notification(id=1))
        mock_uow.notifications.update = AsyncMock(return_value=Notification(id=1, status=NotificationStatus.FAILED))
        mock_uow.scheduled_notifications.mark_processed = AsyncMock()

        # Send fails, and retry_count + 1 >= max_retries
        with patch.object(service, "_send_to_channel", return_value=(False, "SMTP error")):
            result = await service.process_scheduled()

        # Should mark as processed since max retries reached
        mock_uow.scheduled_notifications.mark_processed.assert_awaited_once_with(1)
        assert len(result) == 1
        assert "failed after 3 retries" in caplog.text


class TestNotificationServiceSendToChannel:
    """Tests for _send_to_channel method."""

    async def test_routes_telegram_channel(self, mock_uow: MagicMock) -> None:
        """Routes TELEGRAM channel to _send_telegram."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.TELEGRAM,
            recipient_telegram_id=123456789,
            body="Test",
        )

        with patch.object(service, "_send_telegram", return_value=(True, None)) as mock_send:
            result = await service._send_to_channel(notification)

        mock_send.assert_awaited_once_with(notification)
        assert result == (True, None)

    async def test_routes_email_channel(self, mock_uow: MagicMock) -> None:
        """Routes EMAIL channel to _send_email."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.EMAIL,
            recipient_email="user@example.com",
            body="Test",
        )

        with patch.object(service, "_send_email", return_value=(True, None)) as mock_send:
            result = await service._send_to_channel(notification)

        mock_send.assert_awaited_once_with(notification)
        assert result == (True, None)

    async def test_routes_both_channel(self, mock_uow: MagicMock) -> None:
        """Routes BOTH channel to _send_both."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.BOTH,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            body="Test",
        )

        with patch.object(service, "_send_both", return_value=(True, None)) as mock_send:
            result = await service._send_to_channel(notification)

        mock_send.assert_awaited_once_with(notification)
        assert result == (True, None)

    async def test_returns_error_for_unsupported_channel(self, mock_uow: MagicMock) -> None:
        """Returns error for unsupported channel."""
        service = NotificationService(mock_uow)

        notification = MagicMock(spec=Notification)
        notification.channel = "UNKNOWN_CHANNEL"  # type: ignore[attr-defined]

        result = await service._send_to_channel(notification)

        assert result == (False, "Unsupported channel: UNKNOWN_CHANNEL")


class TestNotificationServiceSendTelegram:
    """Tests for _send_telegram method."""

    async def test_fails_when_no_telegram_id(self, mock_uow: MagicMock) -> None:
        """Returns failure when no telegram_id provided."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.TELEGRAM,
            recipient_telegram_id=None,
            body="Test",
        )

        result = await service._send_telegram(notification)

        assert result == (False, "No telegram_id provided")

    async def test_uses_telegram_service_to_send(self, mock_uow: MagicMock) -> None:
        """Uses telegram service to send message."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.TELEGRAM,
            recipient_telegram_id=123456789,
            body="Hello Telegram",
        )

        service._telegram.send_message = AsyncMock(return_value=True)

        result = await service._send_telegram(notification)

        service._telegram.send_message.assert_awaited_once_with(
            chat_id=123456789,
            text="Hello Telegram",
        )
        assert result == (True, None)

    async def test_returns_failure_on_send_failure(self, mock_uow: MagicMock) -> None:
        """Returns failure when telegram send fails."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.TELEGRAM,
            recipient_telegram_id=123456789,
            body="Test",
        )

        service._telegram.send_message = AsyncMock(return_value=False)

        result = await service._send_telegram(notification)

        assert result == (False, "Telegram send failed")

    async def test_returns_failure_on_exception(self, mock_uow: MagicMock, caplog: LogCaptureFixture) -> None:
        """Returns failure and logs exception on error."""
        caplog.set_level("ERROR")
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.TELEGRAM,
            recipient_telegram_id=123456789,
            body="Test",
        )

        service._telegram.send_message = AsyncMock(side_effect=Exception("API Error"))

        result = await service._send_telegram(notification)

        assert result == (False, "Telegram send failed")
        assert "Telegram send failed for notification 1" in caplog.text


class TestNotificationServiceSendEmail:
    """Tests for _send_email method."""

    async def test_fails_when_no_email_provided(self, mock_uow: MagicMock) -> None:
        """Returns failure when no email provided."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.EMAIL,
            recipient_email=None,
            body="Test",
        )

        result = await service._send_email(notification)

        assert result == (False, "No email provided")

    async def test_uses_email_service_to_send(self, mock_uow: MagicMock) -> None:
        """Uses email service to send message."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.EMAIL,
            recipient_email="user@example.com",
            subject="Test Subject",
            body="Hello Email",
        )

        service._email.send_email = AsyncMock()

        result = await service._send_email(notification)

        service._email.send_email.assert_awaited_once_with(
            to_email="user@example.com",
            subject="Test Subject",
            body="Hello Email",
        )
        assert result == (True, None)

    async def test_uses_default_subject_when_none_provided(self, mock_uow: MagicMock) -> None:
        """Uses default subject when notification has no subject."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.EMAIL,
            recipient_email="user@example.com",
            subject=None,
            body="Hello",
        )

        service._email.send_email = AsyncMock()

        await service._send_email(notification)

        call_kwargs = service._email.send_email.call_args.kwargs
        assert call_kwargs["subject"] == "Notification"

    async def test_returns_failure_on_exception(self, mock_uow: MagicMock, caplog: LogCaptureFixture) -> None:
        """Returns failure and logs exception on error."""
        caplog.set_level("ERROR")
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.EMAIL,
            recipient_email="user@example.com",
            body="Test",
        )

        service._email.send_email = AsyncMock(side_effect=Exception("SMTP Error"))

        result = await service._send_email(notification)

        assert result == (False, "Email send failed")
        assert "Email send failed for notification 1" in caplog.text


class TestNotificationServiceSendBoth:
    """Tests for _send_both method."""

    async def test_sends_to_both_channels(self, mock_uow: MagicMock) -> None:
        """Sends to both telegram and email."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.BOTH,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            body="Test",
        )

        with patch.object(service, "_send_telegram", return_value=(True, None)) as mock_telegram:
            with patch.object(service, "_send_email", return_value=(True, None)) as mock_email:
                result = await service._send_both(notification)

        mock_telegram.assert_awaited_once()
        mock_email.assert_awaited_once()
        assert result == (True, None)

    async def test_partial_failure_telegram_fails(self, mock_uow: MagicMock) -> None:
        """Returns partial failure when telegram fails but email succeeds."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.BOTH,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            body="Test",
        )

        with patch.object(service, "_send_telegram", return_value=(False, "Telegram blocked")):
            with patch.object(service, "_send_email", return_value=(True, None)):
                result = await service._send_both(notification)

        assert result == (False, "Telegram blocked")  # Partial failure

    async def test_partial_failure_email_fails(self, mock_uow: MagicMock) -> None:
        """Returns partial failure when email fails but telegram succeeds."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.BOTH,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            body="Test",
        )

        with patch.object(service, "_send_telegram", return_value=(True, None)):
            with patch.object(service, "_send_email", return_value=(False, "SMTP error")):
                result = await service._send_both(notification)

        assert result == (False, "SMTP error")

    async def test_both_failures(self, mock_uow: MagicMock) -> None:
        """Returns combined errors when both channels fail."""
        service = NotificationService(mock_uow)

        notification = Notification(
            id=1,
            channel=NotificationChannel.BOTH,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            body="Test",
        )

        with patch.object(service, "_send_telegram", return_value=(False, "Telegram blocked")):
            with patch.object(service, "_send_email", return_value=(False, "SMTP error")):
                result = await service._send_both(notification)

        assert result[0] is False
        assert "Telegram blocked" in result[1]
        assert "SMTP error" in result[1]


class TestNotificationServiceSendTemplate:
    """Tests for send_template method."""

    async def test_send_template_email_channel(self, mock_uow: MagicMock) -> None:
        """Send template notification via email channel."""
        from notification_service.services.template import RenderedNotification

        service = NotificationService(mock_uow)

        rendered = RenderedNotification(
            subject="Welcome John!",
            body="<h1>Welcome John!</h1><p>Thanks for joining.</p>",
            channel="email",
            variables_used=["user_name"],
        )

        mock_uow.notifications.create = AsyncMock(return_value=Notification(id=1))
        mock_uow.notifications.update = AsyncMock(return_value=Notification(id=1, status=NotificationStatus.SENT))

        with patch.object(service._template_service, "render", return_value=rendered) as mock_render:
            with patch.object(service, "_send_to_channel", return_value=(True, None)):
                result = await service.send_template(
                    template_name="welcome",
                    user_id=42,
                    recipient_telegram_id=None,
                    recipient_email="user@example.com",
                    variables={"user_name": "John"},
                    channel=NotificationChannel.EMAIL,
                    notification_type=NotificationType.GENERAL,
                    language="en",
                )

        mock_render.assert_awaited_once_with(
            template_name="welcome",
            channel="email",
            language="en",
            variables={"user_name": "John"},
        )
        mock_uow.notifications.create.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()
        assert result.status == NotificationStatus.SENT

    async def test_send_template_telegram_channel(self, mock_uow: MagicMock) -> None:
        """Send template notification via telegram channel."""
        from notification_service.services.template import RenderedNotification

        service = NotificationService(mock_uow)

        rendered = RenderedNotification(
            subject=None,
            body="Welcome John! 🎉",
            channel="telegram",
            variables_used=["user_name"],
        )

        mock_uow.notifications.create = AsyncMock(return_value=Notification(id=1))
        mock_uow.notifications.update = AsyncMock(return_value=Notification(id=1, status=NotificationStatus.SENT))

        with patch.object(service._template_service, "render", return_value=rendered) as mock_render:
            with patch.object(service, "_send_to_channel", return_value=(True, None)):
                await service.send_template(
                    template_name="welcome",
                    user_id=42,
                    recipient_telegram_id=123456789,
                    recipient_email=None,
                    variables={"user_name": "John"},
                    channel=NotificationChannel.TELEGRAM,
                )

        mock_render.assert_awaited_once_with(
            template_name="welcome",
            channel="telegram",
            language="en",
            variables={"user_name": "John"},
        )

    async def test_send_template_not_found_raises(self, mock_uow: MagicMock) -> None:
        """Raises TemplateNotFoundError when template not found."""
        from notification_service.services.template import TemplateNotFoundError

        service = NotificationService(mock_uow)

        with patch.object(service._template_service, "render", side_effect=TemplateNotFoundError("missing", "email", "en")):
            with pytest.raises(TemplateNotFoundError):
                await service.send_template(
                    template_name="missing",
                    user_id=42,
                    recipient_telegram_id=None,
                    recipient_email="user@example.com",
                    variables={},
                    channel=NotificationChannel.EMAIL,
                )

    async def test_send_template_missing_variables_raises(self, mock_uow: MagicMock) -> None:
        """Raises MissingTemplateVariablesError when variables missing."""
        from notification_service.services.template import MissingTemplateVariablesError

        service = NotificationService(mock_uow)

        with patch.object(service._template_service, "render", side_effect=MissingTemplateVariablesError({"user_name"})):
            with pytest.raises(MissingTemplateVariablesError):
                await service.send_template(
                    template_name="welcome",
                    user_id=42,
                    recipient_telegram_id=None,
                    recipient_email="user@example.com",
                    variables={},
                    channel=NotificationChannel.EMAIL,
                )

    async def test_send_template_render_error_raises_value_error(self, mock_uow: MagicMock) -> None:
        """Raises ValueError on template render error."""
        from notification_service.services.template import TemplateRenderError

        service = NotificationService(mock_uow)

        with patch.object(service._template_service, "render", side_effect=TemplateRenderError("Parse error")):
            with pytest.raises(ValueError, match="Template rendering failed"):
                await service.send_template(
                    template_name="broken",
                    user_id=42,
                    recipient_telegram_id=None,
                    recipient_email="user@example.com",
                    variables={},
                    channel=NotificationChannel.EMAIL,
                )


class TestNotificationServiceScheduleTemplate:
    """Tests for schedule_template method."""

    async def test_schedule_template_email_channel(self, mock_uow: MagicMock) -> None:
        """Schedule template notification for email."""
        from notification_service.services.template import RenderedNotification

        service = NotificationService(mock_uow)

        rendered = RenderedNotification(
            subject="Meeting Reminder",
            body="Your meeting is in 30 minutes",
            channel="email",
            variables_used=["meeting_title"],
        )

        mock_scheduled = ScheduledNotification(id=1, user_id=42, processed=False)
        mock_uow.scheduled_notifications.create = AsyncMock(return_value=mock_scheduled)

        scheduled_time = datetime.now(UTC) + timedelta(hours=1)

        with patch.object(service._template_service, "render", return_value=rendered) as mock_render:
            result = await service.schedule_template(
                template_name="meeting_reminder",
                user_id=42,
                recipient_telegram_id=None,
                recipient_email="user@example.com",
                variables={"meeting_title": "Team Sync"},
                channel=NotificationChannel.EMAIL,
                scheduled_time=scheduled_time,
            )

        mock_render.assert_awaited_once_with(
            template_name="meeting_reminder",
            channel="email",
            language="en",
            variables={"meeting_title": "Team Sync"},
        )
        mock_uow.scheduled_notifications.create.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()
        assert result.id == 1

    async def test_schedule_template_telegram_channel(self, mock_uow: MagicMock) -> None:
        """Schedule template notification for telegram."""
        from notification_service.services.template import RenderedNotification

        service = NotificationService(mock_uow)

        rendered = RenderedNotification(
            subject=None,
            body="Don't forget your task!",
            channel="telegram",
            variables_used=["task_title"],
        )

        mock_scheduled = ScheduledNotification(id=2, user_id=43, processed=False)
        mock_uow.scheduled_notifications.create = AsyncMock(return_value=mock_scheduled)

        scheduled_time = datetime.now(UTC) + timedelta(minutes=30)

        with patch.object(service._template_service, "render", return_value=rendered) as mock_render:
            await service.schedule_template(
                template_name="task_reminder",
                user_id=43,
                recipient_telegram_id=123456789,
                recipient_email=None,
                variables={"task_title": "Complete setup"},
                channel=NotificationChannel.TELEGRAM,
                scheduled_time=scheduled_time,
            )

        mock_render.assert_awaited_once_with(
            template_name="task_reminder",
            channel="telegram",
            language="en",
            variables={"task_title": "Complete setup"},
        )

    async def test_schedule_template_not_found_raises(self, mock_uow: MagicMock) -> None:
        """Raises TemplateNotFoundError when template not found."""
        from notification_service.services.template import TemplateNotFoundError

        service = NotificationService(mock_uow)

        with patch.object(service._template_service, "render", side_effect=TemplateNotFoundError("missing", "telegram", "en")):
            with pytest.raises(TemplateNotFoundError):
                await service.schedule_template(
                    template_name="missing",
                    user_id=42,
                    recipient_telegram_id=123456789,
                    recipient_email=None,
                    variables={},
                    channel=NotificationChannel.TELEGRAM,
                    scheduled_time=datetime.now(UTC),
                )

    async def test_schedule_template_missing_variables_raises(self, mock_uow: MagicMock) -> None:
        """Raises MissingTemplateVariablesError when variables missing."""
        from notification_service.services.template import MissingTemplateVariablesError

        service = NotificationService(mock_uow)

        with patch.object(service._template_service, "render", side_effect=MissingTemplateVariablesError({"due_date"})):
            with pytest.raises(MissingTemplateVariablesError):
                await service.schedule_template(
                    template_name="task_reminder",
                    user_id=42,
                    recipient_telegram_id=123456789,
                    recipient_email=None,
                    variables={},
                    channel=NotificationChannel.TELEGRAM,
                    scheduled_time=datetime.now(UTC),
                )

    async def test_schedule_template_render_error_raises_value_error(self, mock_uow: MagicMock) -> None:
        """Raises ValueError on template render error."""
        from notification_service.services.template import TemplateRenderError

        service = NotificationService(mock_uow)

        with patch.object(service._template_service, "render", side_effect=TemplateRenderError("Parse error")):
            with pytest.raises(ValueError, match="Template rendering failed"):
                await service.schedule_template(
                    template_name="broken",
                    user_id=42,
                    recipient_telegram_id=123456789,
                    recipient_email=None,
                    variables={},
                    channel=NotificationChannel.TELEGRAM,
                    scheduled_time=datetime.now(UTC),
                )
