"""HTTP client for notification service integration."""

import logging

import httpx
from fastapi import status

from telegram_bot.config import settings

logger = logging.getLogger(__name__)


class NotificationServiceClient:
    """HTTP client for notification service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize notification service HTTP client."""
        self.base_url = base_url or settings.NOTIFICATION_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT)

    async def send_telegram_notification(
        self, user_id: int, title: str, message: str, priority: str = "normal"
    ) -> dict | None:
        """Send Telegram notification to user."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/notifications/telegram",
                json={
                    "user_id": user_id,
                    "title": title,
                    "message": message,
                    "priority": priority,
                },
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Notification service request failed: {e}")
        return None

    async def send_email_notification(self, email: str, subject: str, message: str) -> dict | None:
        """Send email notification."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/notifications/email",
                json={
                    "email": email,
                    "subject": subject,
                    "message": message,
                },
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Notification service email request failed: {e}")
        return None

    async def schedule_notification(
        self, user_id: int, message: str, send_at: str, channel: str = "telegram"
    ) -> dict | None:
        """Schedule notification for later delivery."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/notifications/schedule",
                json={
                    "user_id": user_id,
                    "message": message,
                    "send_at": send_at,
                    "channel": channel,
                },
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Notification service schedule request failed: {e}")
        return None

    async def get_user_notifications(self, user_id: int, limit: int = 10) -> list[dict]:
        """Get user notifications."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/notifications/user/{user_id}",
                params={"limit": limit},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                return data.get("notifications", [])
        except httpx.RequestError as e:
            logger.exception(f"Notification service get notifications failed: {e}")
        return []


# Singleton instance
notification_client = NotificationServiceClient()
