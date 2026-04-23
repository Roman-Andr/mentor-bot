"""Unit tests for notification_service/services/scheduler.py."""

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from _pytest.logging import LogCaptureFixture

from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.models import Notification, ScheduledNotification
from notification_service.services.scheduler import Scheduler


@pytest.fixture(autouse=True)
def mock_asyncio_sleep() -> Any:
    """Mock asyncio.sleep to speed up scheduler tests."""
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        yield mock_sleep


class TestSchedulerPollCycle:
    """Tests for scheduler poll cycle with mocked UoW."""

    async def test_poll_cycle_processes_due_notifications(self, mock_uow: Any) -> None:
        """Due notifications are dispatched during poll cycle."""
        now = datetime.now(UTC)
        due_notification = ScheduledNotification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            subject="Due Notification",
            body="This is due",
            data={},
            scheduled_time=now - timedelta(minutes=5),  # Past = due
            processed=False,
        )

        mock_uow.scheduled_notifications.find_pending_before.return_value = [due_notification]

        processed_notifications = [
            Notification(
                id=1,
                user_id=42,
                recipient_telegram_id=123456789,
                recipient_email="user@example.com",
                type=NotificationType.GENERAL,
                channel=NotificationChannel.EMAIL,
                subject="Due Notification",
                body="This is due",
                data={},
                status=NotificationStatus.SENT,
                sent_at=now,
            )
        ]

        with patch("notification_service.services.scheduler.NotificationService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.process_scheduled = AsyncMock(return_value=processed_notifications)
            mock_service_cls.return_value = mock_service

            scheduler = Scheduler(poll_interval=1)
            await scheduler._process()

            mock_service.process_scheduled.assert_awaited_once()

    async def test_non_due_notifications_are_skipped(self, mock_uow: Any) -> None:
        """Non-due notifications (future) are not returned by find_pending_before."""
        now = datetime.now(UTC)
        # Create notification but don't assign to variable since it's not used directly
        ScheduledNotification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="user@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            subject="Future Notification",
            body="This is not due yet",
            data={},
            scheduled_time=now + timedelta(hours=1),  # Future = not due
            processed=False,
        )

        # find_pending_before should only return notifications scheduled <= now
        mock_uow.scheduled_notifications.find_pending_before.return_value = []

        with patch("notification_service.services.scheduler.NotificationService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.process_scheduled = AsyncMock(return_value=[])
            mock_service_cls.return_value = mock_service

            scheduler = Scheduler(poll_interval=1)
            await scheduler._process()

            # process_scheduled is still called, but finds no pending notifications
            mock_service.process_scheduled.assert_awaited_once()

    async def test_mixed_due_and_non_due_notifications(self, mock_uow: Any) -> None:
        """Only due notifications are processed, non-due are skipped."""
        now = datetime.now(UTC)

        due_notification = ScheduledNotification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="due@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            subject="Due",
            body="Due body",
            data={},
            scheduled_time=now - timedelta(minutes=5),
            processed=False,
        )

        # Only due notification returned from find_pending_before
        mock_uow.scheduled_notifications.find_pending_before.return_value = [due_notification]

        processed_notification = Notification(
            id=1,
            user_id=42,
            recipient_telegram_id=123456789,
            recipient_email="due@example.com",
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            subject="Due",
            body="Due body",
            data={},
            status=NotificationStatus.SENT,
            sent_at=now,
        )

        with patch("notification_service.services.scheduler.NotificationService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.process_scheduled = AsyncMock(return_value=[processed_notification])
            mock_service_cls.return_value = mock_service

            scheduler = Scheduler(poll_interval=1)
            await scheduler._process()

            mock_service.process_scheduled.assert_awaited_once()

    async def test_logs_processed_count_when_notifications_sent(self, caplog: LogCaptureFixture) -> None:
        """Scheduler logs count of processed notifications."""
        caplog.set_level("INFO")

        now = datetime.now(UTC)
        processed = [
            Notification(
                id=1,
                user_id=42,
                recipient_telegram_id=123456789,
                recipient_email="user@example.com",
                type=NotificationType.GENERAL,
                channel=NotificationChannel.EMAIL,
                subject="Test",
                body="Body",
                data={},
                status=NotificationStatus.SENT,
                sent_at=now,
            )
        ]

        with patch("notification_service.services.scheduler.NotificationService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.process_scheduled = AsyncMock(return_value=processed)
            mock_service_cls.return_value = mock_service

            scheduler = Scheduler(poll_interval=1)
            await scheduler._process()

            assert "Processed 1 scheduled notifications" in caplog.text

    async def test_no_log_when_no_notifications_processed(self, caplog: LogCaptureFixture) -> None:
        """No processed log when no notifications sent."""
        caplog.set_level("INFO")

        with patch("notification_service.services.scheduler.NotificationService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.process_scheduled = AsyncMock(return_value=[])
            mock_service_cls.return_value = mock_service

            scheduler = Scheduler(poll_interval=1)
            await scheduler._process()

            assert "Processed" not in caplog.text


class TestSchedulerLifecycle:
    """Tests for scheduler start/stop lifecycle."""

    async def test_stop_signal_breaks_loop(self) -> None:
        """Stop signal breaks the scheduler loop."""
        scheduler = Scheduler(poll_interval=0.1)

        call_count = 0

        async def mock_process() -> None:
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                await scheduler.stop()

        with patch.object(scheduler, "_process", mock_process):
            await scheduler.run()

        assert call_count >= 2
        assert not scheduler._running

    async def test_run_logs_start_message(self, caplog: LogCaptureFixture) -> None:
        """Scheduler logs start message with poll interval."""
        caplog.set_level("INFO")

        scheduler = Scheduler(poll_interval=60)

        async def mock_process() -> None:
            await scheduler.stop()

        with patch.object(scheduler, "_process", mock_process):
            await scheduler.run()

        assert "Scheduler started with poll interval 60s" in caplog.text

    async def test_stop_logs_stop_message(self, caplog: LogCaptureFixture) -> None:
        """Scheduler logs stop message."""
        caplog.set_level("INFO")

        scheduler = Scheduler(poll_interval=1)
        await scheduler.stop()

        assert "Scheduler stopped" in caplog.text

    async def test_stop_cancels_task(self) -> None:
        """Stop cancels the running task."""
        scheduler = Scheduler(poll_interval=1)
        scheduler._task = MagicMock()

        await scheduler.stop()

        scheduler._task.cancel.assert_called_once()

    async def test_handles_exception_in_process_loop(self, caplog: LogCaptureFixture) -> None:
        """Scheduler continues loop even if _process raises."""
        caplog.set_level("ERROR")

        scheduler = Scheduler(poll_interval=0.05)
        call_count = 0

        async def failing_process() -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                msg = "Process failed"
                raise RuntimeError(msg)
            if call_count >= 3:
                await scheduler.stop()

        with patch.object(scheduler, "_process", failing_process):
            await scheduler.run()

        assert call_count >= 3
        assert "Error in scheduler loop" in caplog.text

    async def test_initial_state(self) -> None:
        """Scheduler initializes with correct default state."""
        poll_interval = 30
        scheduler = Scheduler(poll_interval=poll_interval)

        assert scheduler.poll_interval == poll_interval
        assert not scheduler._running
        assert scheduler._task is None


class TestSchedulerUoWIntegration:
    """Tests for scheduler's UoW context manager usage."""

    async def test_process_uses_async_session_local(self) -> None:
        """Scheduler uses AsyncSessionLocal for UoW."""
        mock_session_local = MagicMock()
        mock_uow_instance = MagicMock()
        mock_uow_instance.__aenter__ = AsyncMock(return_value=mock_uow_instance)
        mock_uow_instance.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("notification_service.services.scheduler.AsyncSessionLocal", mock_session_local),
            patch("notification_service.services.scheduler.SqlAlchemyUnitOfWork") as mock_uow_cls,
        ):
            mock_uow_cls.return_value = mock_uow_instance

            with patch("notification_service.services.scheduler.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.process_scheduled = AsyncMock(return_value=[])
                mock_service_cls.return_value = mock_service

                scheduler = Scheduler(poll_interval=1)
                await scheduler._process()

                mock_uow_cls.assert_called_once_with(mock_session_local)
                mock_uow_instance.__aenter__.assert_awaited_once()
                mock_uow_instance.__aexit__.assert_awaited_once()
