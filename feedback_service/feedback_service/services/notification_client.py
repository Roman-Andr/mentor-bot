"""Client to send notifications via notification_service."""

import httpx
from loguru import logger

from feedback_service.config import settings


class NotificationClient:
    """Client to send notifications via notification_service."""

    def __init__(self) -> None:
        """Initialize notification client with service URL and API key."""
        self.base_url = settings.NOTIFICATION_SERVICE_URL
        self.api_key = settings.SERVICE_API_KEY

    async def notify_comment_reply(
        self,
        comment_id: int,
        original_comment_preview: str,
        reply_text: str,
        replied_by_name: str,
        user_id: int | None = None,
    ) -> bool:
        """Notify comment author when their comment receives a reply."""
        logger.debug(
            "Preparing comment-reply notifications (comment_id={}, user_id={})",
            comment_id,
            user_id,
        )

        # Only send notifications to authenticated users (with user_id)
        # Anonymous users with contact_email cannot be notified due to API limitations
        if not user_id:
            logger.debug("Skipping notification: no user_id provided (anonymous comment)")
            return True

        # Truncate preview if too long
        preview = (
            original_comment_preview[:100] + "..." if len(original_comment_preview) > 100 else original_comment_preview
        )

        variables = {
            "original_comment_preview": preview,
            "reply_text": reply_text,
            "replied_by_name": replied_by_name,
        }

        # Send Telegram notification
        telegram_success = await self._send_notification(
            user_id=user_id,
            template_name="comment_reply",
            variables=variables,
            channel="telegram",
        )

        # Send email notification
        email_success = await self._send_notification(
            user_id=user_id,
            template_name="comment_reply",
            variables=variables,
            channel="email",
        )

        return telegram_success and email_success

    async def _send_notification(
        self,
        user_id: int,
        template_name: str,
        variables: dict,
        channel: str = "telegram",
    ) -> bool:
        """Send notification via notification_service."""
        try:
            async with httpx.AsyncClient() as client:
                logger.debug(
                    "Sending notification template (user_id={}, template_name={}, channel={})",
                    user_id,
                    template_name,
                    channel,
                )
                payload = {
                    "user_id": user_id,
                    "template_name": template_name,
                    "variables": variables,
                    "channel": channel,
                }

                response = await client.post(
                    f"{self.base_url}/api/v1/notifications/send-template",
                    json=payload,
                    headers={"X-Service-Key": self.api_key},
                    timeout=10.0,
                )
                response.raise_for_status()
                logger.info(
                    "Notification template sent (user_id={}, template_name={}, channel={})",
                    user_id,
                    template_name,
                    channel,
                )
                return True
        except Exception:
            logger.warning(
                "Could not send notification (user_id={}, template_name={}, channel={})",
                user_id,
                template_name,
                channel,
            )
            return False
