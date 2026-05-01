"""Main notification service."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from loguru import logger

from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.models import Notification, ScheduledNotification
from notification_service.repositories.unit_of_work import IUnitOfWork
from notification_service.schemas import NotificationCreate, ScheduledNotificationCreate
from notification_service.services.auth_client import AuthClient, AuthClientError
from notification_service.services.email import EmailService
from notification_service.services.telegram import TelegramService
from notification_service.services.template import (
    MissingTemplateVariablesError,
    TemplateNotFoundError,
    TemplateRenderError,
    TemplateService,
)


class NotificationService:
    """Service for sending and managing notifications."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize the service with Unit of Work."""
        self._uow = uow
        self._telegram = TelegramService()
        self._email = EmailService()
        self._template_service = TemplateService(uow)
        self._auth_client = AuthClient()

    async def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Notification]:
        """Retrieve notifications for a specific user."""
        logger.debug("Fetching user notifications (user_id={}, skip={}, limit={})", user_id, skip, limit)
        notifications = await self._uow.notifications.get_user_notifications(user_id, skip, limit)
        logger.debug("User notifications fetched (user_id={}, count={})", user_id, len(list(notifications)))
        return notifications

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
        logger.debug(
            "Finding notifications (skip={}, limit={}, user_id={}, type={}, status={})",
            skip,
            limit,
            user_id,
            notification_type,
            status,
        )
        items, total = await self._uow.notifications.find_notifications(
            skip=skip,
            limit=limit,
            user_id=user_id,
            notification_type=notification_type,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        logger.debug("Notifications found (count={}, total={})", len(list(items)), total)
        return list(items), total

    async def send_immediate(self, notification_data: NotificationCreate) -> Notification:
        """Send a notification immediately (synchronously)."""
        logger.debug(
            "Sending immediate notification (user_id={}, type={}, channel={})",
            notification_data.user_id,
            notification_data.type,
            notification_data.channel,
        )
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
        if success:
            logger.info("Immediate notification sent (notification_id={}, user_id={})", updated.id, updated.user_id)
        else:
            logger.warning("Immediate notification failed (notification_id={}, user_id={}, error={})", updated.id, updated.user_id, error_msg)
        return updated

    async def schedule(self, schedule_data: ScheduledNotificationCreate) -> ScheduledNotification:
        """Schedule a notification for future sending."""
        logger.debug(
            "Scheduling notification (user_id={}, type={}, channel={}, scheduled_time={})",
            schedule_data.user_id,
            schedule_data.type,
            schedule_data.channel,
            schedule_data.scheduled_time,
        )
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
        logger.info("Notification scheduled (scheduled_id={}, user_id={})", saved.id, saved.user_id)
        return saved

    async def process_scheduled(self) -> list[Notification]:
        """Process all pending scheduled notifications whose time has come."""
        logger.debug("Processing scheduled notifications")
        now = datetime.now(UTC)
        pending = await self._uow.scheduled_notifications.find_pending_before(now)
        logger.debug("Found {} pending scheduled notifications", len(list(pending)))
        processed_notifications = []

        for scheduled in pending:
            # Skip if max retries exceeded
            if scheduled.retry_count >= scheduled.max_retries:
                logger.warning("Skipping scheduled notification: max retries exceeded (scheduled_id={})", scheduled.id)
                await self._uow.scheduled_notifications.mark_processed(scheduled.id)
                continue

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

            if success:
                # Mark scheduled as processed only on success
                await self._uow.scheduled_notifications.mark_processed(scheduled.id)
                logger.info("Scheduled notification processed successfully (scheduled_id={})", scheduled.id)
            elif scheduled.retry_count + 1 >= scheduled.max_retries:
                # Max retries reached, mark as processed (failed)
                await self._uow.scheduled_notifications.mark_processed(scheduled.id)
                logger.warning(
                    "Scheduled notification {} failed after {} retries",
                    scheduled.id,
                    scheduled.max_retries,
                )
            else:
                # Schedule retry with exponential backoff
                backoff_minutes = 2 ** scheduled.retry_count
                next_scheduled = now + timedelta(minutes=backoff_minutes)
                await self._uow.scheduled_notifications.increment_retry(
                    scheduled.id, next_scheduled
                )
                logger.info(
                    "Scheduled notification %s failed, retrying in %d minutes (attempt %d/%d)",
                    scheduled.id,
                    backoff_minutes,
                    scheduled.retry_count + 1,
                    scheduled.max_retries,
                )

            processed_notifications.append(saved)

        if processed_notifications:
            await self._uow.commit()
            logger.info("Processed {} scheduled notifications", len(processed_notifications))

        return processed_notifications

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
        """
        Send a notification using a template.

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
        logger.debug(
            "Sending template notification (template_name={}, user_id={}, channel={}, language={})",
            template_name,
            user_id,
            channel,
            language,
        )
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
            logger.warning("Template not found: %s for channel %s", template_name, channel_str)
            raise
        except MissingTemplateVariablesError:
            logger.warning("Missing variables for template: %s", template_name)
            raise
        except TemplateRenderError as e:
            logger.error("Template rendering failed: %s", template_name)
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
        if success:
            logger.info("Template notification sent (notification_id={}, template_name={})", updated.id, template_name)
        else:
            logger.warning("Template notification failed (notification_id={}, template_name={}, error={})", updated.id, template_name, error_msg)
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
        """
        Schedule a template-based notification for future sending.

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
        logger.debug(
            "Scheduling template notification (template_name={}, user_id={}, channel={}, scheduled_time={})",
            template_name,
            user_id,
            channel,
            scheduled_time,
        )
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
            logger.warning("Template not found: %s for channel %s", template_name, channel_str)
            raise
        except MissingTemplateVariablesError:
            logger.warning("Missing variables for template: %s", template_name)
            raise
        except TemplateRenderError as e:
            logger.error("Template rendering failed: %s", template_name)
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
        logger.info("Template notification scheduled (scheduled_id={}, template_name={})", saved.id, template_name)
        return saved

    async def _send_to_channel(self, notification: Notification) -> tuple[bool, str | None]:
        """Send notification to the appropriate channel."""
        channel = notification.channel
        logger.debug("Sending notification to channel (notification_id={}, channel={})", notification.id, channel)

        # Check user preferences before sending
        try:
            prefs = await self._auth_client.get_user_preferences(notification.user_id)
        except AuthClientError as e:
            logger.warning("Failed to fetch user preferences, using fail-open (user_id={}, error={})", notification.user_id, e)
            prefs = None

        if channel == NotificationChannel.TELEGRAM:
            return await self._send_telegram(notification, prefs)
        if channel == NotificationChannel.EMAIL:
            return await self._send_email(notification, prefs)
        if channel == NotificationChannel.BOTH:
            return await self._send_both(notification, prefs)
        logger.warning("Unsupported channel (notification_id={}, channel={})", notification.id, channel)
        return False, f"Unsupported channel: {channel}"

    async def _send_telegram(self, notification: Notification, prefs: Any = None) -> tuple[bool, str | None]:
        """Send notification via Telegram."""
        # Check if telegram notifications are disabled
        if prefs and not prefs.notification_telegram_enabled:
            logger.info("Telegram notification skipped: user disabled (notification_id={}, user_id={})", notification.id, notification.user_id)
            return True, None  # Return success to avoid retry

        if not notification.recipient_telegram_id:
            logger.warning("Telegram send failed: no telegram_id (notification_id={})", notification.id)
            return False, "No telegram_id provided"
        try:
            success = await self._telegram.send_message(
                chat_id=notification.recipient_telegram_id,
                text=notification.body,
            )
        except Exception as e:
            logger.error("Telegram send failed for notification {}: {}", notification.id, str(e))
            return False, "Telegram send failed"
        else:
            if success:
                logger.info("Telegram notification sent (notification_id={})", notification.id)
            return success, None if success else "Telegram send failed"

    async def _send_email(self, notification: Notification, prefs: Any = None) -> tuple[bool, str | None]:
        """Send notification via Email."""
        # Check if email notifications are disabled
        if prefs and not prefs.notification_email_enabled:
            logger.info("Email notification skipped: user disabled (notification_id={}, user_id={})", notification.id, notification.user_id)
            return True, None  # Return success to avoid retry

        if not notification.recipient_email:
            logger.warning("Email send failed: no email (notification_id={})", notification.id)
            return False, "No email provided"
        try:
            await self._email.send_email(
                to_email=notification.recipient_email,
                subject=notification.subject or "Notification",
                body=notification.body,
            )
        except Exception as e:
            logger.error("Email send failed for notification {}: {}", notification.id, str(e))
            return False, "Email send failed"
        else:
            logger.info("Email notification sent (notification_id={})", notification.id)
            return True, None

    async def _send_both(self, notification: Notification, prefs: Any = None) -> tuple[bool, str | None]:
        """Send notification via both Telegram and Email."""
        logger.debug("Sending notification via both channels (notification_id={})", notification.id)

        # Check if both channels are disabled
        if prefs and not prefs.notification_telegram_enabled and not prefs.notification_email_enabled:
            logger.warning("Both notification channels disabled, skipping (notification_id={}, user_id={})", notification.id, notification.user_id)
            return True, None  # Return success to avoid retry

        telegram_success, telegram_error = await self._send_telegram(notification, prefs)
        email_success, email_error = await self._send_email(notification, prefs)

        errors = []
        if telegram_error:
            errors.append(telegram_error)
        if email_error:
            errors.append(email_error)

        overall_success = telegram_success and email_success
        error_msg = "; ".join(errors) if errors else None
        logger.info("Both channels send result (notification_id={}, success={})", notification.id, overall_success)
        return overall_success, error_msg
