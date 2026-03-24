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
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT
        )

    async def send_telegram_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        auth_token: str,
        priority: str = "normal",
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
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Notification service request failed")
        return None

    async def send_email_notification(
        self, email: str, subject: str, message: str, auth_token: str
    ) -> dict | None:
        """Send email notification."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/notifications/email",
                json={
                    "email": email,
                    "subject": subject,
                    "message": message,
                },
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Notification service email request failed")
        return None

    async def schedule_notification(
        self,
        user_id: int,
        message: str,
        send_at: str,
        auth_token: str,
        channel: str = "telegram",
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
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Notification service schedule request failed")
        return None

    async def get_user_notifications(
        self, user_id: int, auth_token: str, limit: int = 10
    ) -> list[dict]:
        """Get user notifications."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/notifications/user/{user_id}",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                return data.get("notifications", [])
        except httpx.RequestError:
            logger.exception("Notification service get notifications failed")
        return []

    async def send_task_reminder(
        self, telegram_id: int, task_title: str, due_date: str, auth_token: str
    ) -> dict | None:
        """Send task reminder notification."""
        message = f'Reminder: Task "{task_title}" is due {due_date}.'
        return await self.send_telegram_notification(
            telegram_id, "Task Reminder", message, auth_token, priority="high"
        )

    async def send_meeting_reminder(
        self, telegram_id: int, meeting_title: str, meeting_time: str, auth_token: str
    ) -> dict | None:
        """Send meeting reminder notification."""
        message = f'Reminder: Meeting "{meeting_title}" at {meeting_time}.'
        return await self.send_telegram_notification(
            telegram_id, "Meeting Reminder", message, auth_token, priority="high"
        )

    async def get_active_reminders(self, auth_token: str) -> list[dict]:
        """Get all active scheduled reminders."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/notifications/scheduled",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Notification service get reminders failed")
        return []


# Singleton instance
notification_client = NotificationServiceClient()
