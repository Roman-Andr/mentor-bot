"""Main notification service."""

import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.models import Notification, ScheduledNotification
from notification_service.repositories.unit_of_work import IUnitOfWork
from notification_service.schemas import NotificationCreate, ScheduledNotificationCreate
from notification_service.services.email import EmailService
from notification_service.services.telegram import TelegramService
from notification_service.services.template import (
    MissingTemplateVariablesError,
    TemplateNotFoundError,
    TemplateRenderError,
    TemplateService,
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending and managing notifications."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize the service with Unit of Work."""
        self._uow = uow
        self._telegram = TelegramService()
        self._email = EmailService()
        self._template_service = TemplateService(uow)

    async def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Notification]:
        """Retrieve notifications for a specific user."""
        return await self._uow.notifications.get_user_notifications(user_id, skip, limit)

    async def find_notifications(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: int | None = None,
        notification_type: NotificationType | None = None,
        status: NotificationStatus | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Notification], int]:
        """Find notifications with filtering and sorting."""
        items, total = await self._uow.notifications.find_notifications(
            skip=skip,
            limit=limit,
            user_id=user_id,
            notification_type=notification_type,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return list(items), total

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

    async def send_template(
        self,
        template_name: str,
        user_id: int,
        recipient_telegram_id: int | None,
        recipient_email: str | None,
        variables: dict[str, Any],
        channel: NotificationChannel,
        notification_type: NotificationType = NotificationType.GENERAL,
        language: str = "en",
    ) -> Notification:
        """Send a notification using a template.

        Args:
            template_name: Name of the template to use
            user_id: ID of the recipient user
            recipient_telegram_id: Telegram ID for telegram notifications
            recipient_email: Email address for email notifications
            variables: Template variables to substitute
            channel: Notification channel
            notification_type: Type of notification
            language: Language code for template selection

        Returns:
            The created and sent Notification

        Raises:
            TemplateNotFoundError: If template is not found
            MissingTemplateVariablesError: If required variables are missing
        """
        # Render template
        channel_str = "email" if channel == NotificationChannel.EMAIL else "telegram"

        try:
            rendered = await self._template_service.render(
                template_name=template_name,
                channel=channel_str,
                language=language,
                variables=variables,
            )
        except TemplateNotFoundError:
            logger.exception("Template not found: %s for channel %s", template_name, channel_str)
            raise
        except MissingTemplateVariablesError:
            logger.exception("Missing variables for template: %s", template_name)
            raise
        except TemplateRenderError as e:
            logger.exception("Template rendering failed: %s", template_name)
            msg = f"Template rendering failed: {e}"
            raise ValueError(msg) from e

        # Create notification
        notification = Notification(
            user_id=user_id,
            recipient_telegram_id=recipient_telegram_id,
            recipient_email=recipient_email,
            type=notification_type,
            channel=channel,
            subject=rendered.subject,
            body=rendered.body,
            data={"template_name": template_name, "variables": variables},
            status=NotificationStatus.PENDING,
            scheduled_for=None,
        )

        saved = await self._uow.notifications.create(notification)

        # Send immediately
        success, error_msg = await self._send_to_channel(saved)

        saved.status = NotificationStatus.SENT if success else NotificationStatus.FAILED
        saved.error_message = error_msg
        saved.sent_at = datetime.now(UTC) if success else None

        updated = await self._uow.notifications.update(saved)
        await self._uow.commit()
        return updated

    async def schedule_template(
        self,
        template_name: str,
        user_id: int,
        recipient_telegram_id: int | None,
        recipient_email: str | None,
        variables: dict[str, Any],
        channel: NotificationChannel,
        scheduled_time: datetime,
        notification_type: NotificationType = NotificationType.GENERAL,
        language: str = "en",
    ) -> ScheduledNotification:
        """Schedule a template-based notification for future sending.

        Args:
            template_name: Name of the template to use
            user_id: ID of the recipient user
            recipient_telegram_id: Telegram ID for telegram notifications
            recipient_email: Email address for email notifications
            variables: Template variables to substitute
            channel: Notification channel
            scheduled_time: When to send the notification
            notification_type: Type of notification
            language: Language code for template selection

        Returns:
            The created ScheduledNotification
        """
        # Render template
        channel_str = "email" if channel == NotificationChannel.EMAIL else "telegram"

        try:
            rendered = await self._template_service.render(
                template_name=template_name,
                channel=channel_str,
                language=language,
                variables=variables,
            )
        except TemplateNotFoundError:
            logger.exception("Template not found: %s for channel %s", template_name, channel_str)
            raise
        except MissingTemplateVariablesError:
            logger.exception("Missing variables for template: %s", template_name)
            raise
        except TemplateRenderError as e:
            logger.exception("Template rendering failed: %s", template_name)
            msg = f"Template rendering failed: {e}"
            raise ValueError(msg) from e

        # Create scheduled notification
        scheduled = ScheduledNotification(
            user_id=user_id,
            recipient_telegram_id=recipient_telegram_id,
            recipient_email=recipient_email,
            type=notification_type,
            channel=channel,
            subject=rendered.subject,
            body=rendered.body,
            data={"template_name": template_name, "variables": variables},
            scheduled_time=scheduled_time,
            processed=False,
        )

        saved = await self._uow.scheduled_notifications.create(scheduled)
        await self._uow.commit()
        return saved

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
        except Exception:
            logger.exception("Telegram send failed for notification %s", notification.id)
            return False, "Telegram send failed"
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
        except Exception:
            logger.exception("Email send failed for notification %s", notification.id)
            return False, "Email send failed"
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
