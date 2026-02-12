"""Main notification service."""

import logging
from collections.abc import Sequence
from datetime import UTC, datetime

from notification_service.core.enums import NotificationChannel, NotificationStatus
from notification_service.models import Notification, ScheduledNotification
from notification_service.repositories.unit_of_work import IUnitOfWork
from notification_service.schemas import NotificationCreate, ScheduledNotificationCreate
from notification_service.services.email import EmailService
from notification_service.services.telegram import TelegramService

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending and managing notifications."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize the service with Unit of Work."""
        self._uow = uow
        self._telegram = TelegramService()
        self._email = EmailService()

    async def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Notification]:
        """Retrieve notifications for a specific user."""
        return await self._uow.notifications.get_user_notifications(user_id, skip, limit)

    async def send_immediate(self, notification_data: NotificationCreate) -> Notification:
        """Send a notification immediately (synchronously)."""
        # Create notification record
        notification = Notification(
            user_id=notification_data.user_id,
            recipient_telegram_id=notification_data.recipient_telegram_id,
            recipient_email=notification_data.recipient_email,
            type=notification_data.type,
            channel=notification_data.channel,
            subject=notification_data.subject,
            body=notification_data.body,
            data=notification_data.data,
            status=NotificationStatus.PENDING,
            scheduled_for=None,
        )

        saved = await self._uow.notifications.create(notification)

        # Attempt to send
        success, error_msg = await self._send_to_channel(saved)

        saved.status = NotificationStatus.SENT if success else NotificationStatus.FAILED
        saved.error_message = error_msg
        saved.sent_at = datetime.now(UTC) if success else None

        updated = await self._uow.notifications.update(saved)
        await self._uow.commit()
        return updated

    async def schedule(self, schedule_data: ScheduledNotificationCreate) -> ScheduledNotification:
        """Schedule a notification for future sending."""
        scheduled = ScheduledNotification(
            user_id=schedule_data.user_id,
            recipient_telegram_id=schedule_data.recipient_telegram_id,
            recipient_email=schedule_data.recipient_email,
            type=schedule_data.type,
            channel=schedule_data.channel,
            subject=schedule_data.subject,
            body=schedule_data.body,
            data=schedule_data.data,
            scheduled_time=schedule_data.scheduled_time,
            processed=False,
        )
        saved = await self._uow.scheduled_notifications.create(scheduled)
        await self._uow.commit()
        return saved

    async def process_scheduled(self) -> list[Notification]:
        """Process all pending scheduled notifications whose time has come."""
        now = datetime.now(UTC)
        pending = await self._uow.scheduled_notifications.find_pending_before(now)
        sent_notifications = []

        for scheduled in pending:
            # Create notification record from scheduled data
            notification = Notification(
                user_id=scheduled.user_id,
                recipient_telegram_id=scheduled.recipient_telegram_id,
                recipient_email=scheduled.recipient_email,
                type=scheduled.type,
                channel=scheduled.channel,
                subject=scheduled.subject,
                body=scheduled.body,
                data=scheduled.data,
                status=NotificationStatus.PENDING,
                scheduled_for=scheduled.scheduled_time,
            )
            saved = await self._uow.notifications.create(notification)

            # Send
            success, error_msg = await self._send_to_channel(saved)
            saved.status = NotificationStatus.SENT if success else NotificationStatus.FAILED
            saved.error_message = error_msg
            saved.sent_at = datetime.now(UTC) if success else None

            await self._uow.notifications.update(saved)

            # Mark scheduled as processed
            await self._uow.scheduled_notifications.mark_processed(scheduled.id)

            sent_notifications.append(saved)

        if sent_notifications:
            await self._uow.commit()

        return sent_notifications

    async def _send_to_channel(self, notification: Notification) -> tuple[bool, str | None]:
        """Send notification to the appropriate channel."""
        channel = notification.channel

        if channel == NotificationChannel.TELEGRAM:
            return await self._send_telegram(notification)
        if channel == NotificationChannel.EMAIL:
            return await self._send_email(notification)
        if channel == NotificationChannel.BOTH:
            return await self._send_both(notification)
        return False, f"Unsupported channel: {channel}"

    async def _send_telegram(self, notification: Notification) -> tuple[bool, str | None]:
        """Send notification via Telegram."""
        if not notification.recipient_telegram_id:
            return False, "No telegram_id provided"
        try:
            success = await self._telegram.send_message(
                chat_id=notification.recipient_telegram_id,
                text=notification.body,
            )
        except Exception as e:
            logger.exception(f"Telegram send failed for notification {notification.id}: {e}")
            return False, str(e)
        else:
            return success, None if success else "Telegram send failed"

    async def _send_email(self, notification: Notification) -> tuple[bool, str | None]:
        """Send notification via Email."""
        if not notification.recipient_email:
            return False, "No email provided"
        try:
            await self._email.send_email(
                to_email=notification.recipient_email,
                subject=notification.subject or "Notification",
                body=notification.body,
            )
        except Exception as e:
            logger.exception(f"Email send failed for notification {notification.id}: {e}")
            return False, str(e)
        else:
            return True, None

    async def _send_both(self, notification: Notification) -> tuple[bool, str | None]:
        """Send notification via both Telegram and Email."""
        telegram_success, telegram_error = await self._send_telegram(notification)
        email_success, email_error = await self._send_email(notification)

        errors = []
        if telegram_error:
            errors.append(telegram_error)
        if email_error:
            errors.append(email_error)

        overall_success = telegram_success and email_success
        error_msg = "; ".join(errors) if errors else None
        return overall_success, error_msg
