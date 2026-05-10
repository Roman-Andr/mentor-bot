"""Integration clients for external services."""

from typing import Any

import httpx
from fastapi import status
from loguru import logger

from meeting_service.config import settings


class AuthServiceClient:
    """HTTP client for auth service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize auth service HTTP client."""
        self.base_url = base_url or settings.AUTH_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.AUTH_SERVICE_TIMEOUT)

    async def get_user(self, user_id: int, auth_token: str) -> dict[str, Any] | None:
        """Get user details from auth service."""
        try:
            response = await self.client.get(
                f"/api/v1/users/{user_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()  # type: ignore[no-any-return]
            logger.warning("Auth service get_user failed (user_id={}, status={})", user_id, response.status_code)
        except httpx.RequestError:
            logger.exception("Auth service get_user request failed (user_id={})", user_id)
        return None


class NotificationServiceClient:
    """HTTP client for notification service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize notification service HTTP client."""
        self.base_url = base_url or settings.NOTIFICATION_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT)

    async def schedule_template_notification(
        self,
        *,
        template_name: str,
        user_id: int,
        variables: dict[str, Any],
        channel: str,
        scheduled_time: str,
        notification_type: str,
        recipient_telegram_id: int | None = None,
        recipient_email: str | None = None,
        language: str = "en",
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Schedule a template notification through the internal notification API."""
        try:
            response = await self.client.post(
                "/api/v1/notifications/internal/schedule-template",
                json={
                    "template_name": template_name,
                    "user_id": user_id,
                    "variables": variables,
                    "channel": channel,
                    "scheduled_time": scheduled_time,
                    "notification_type": notification_type,
                    "recipient_telegram_id": recipient_telegram_id,
                    "recipient_email": recipient_email,
                    "language": language,
                    "data": data or {},
                },
                headers={"X-Service-Api-Key": settings.SERVICE_API_KEY},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
            logger.error("Notification schedule-template error: {}", response.text)
        except httpx.RequestError:
            logger.exception("Failed to schedule template notification")
        return None

    async def cancel_scheduled_notifications(
        self,
        *,
        user_id: int,
        notification_type: str,
        data_match: dict[str, Any],
    ) -> int:
        """Cancel pending scheduled notifications through the internal notification API."""
        try:
            response = await self.client.post(
                "/api/v1/notifications/internal/scheduled/cancel",
                json={
                    "user_id": user_id,
                    "notification_type": notification_type,
                    "data_match": data_match,
                },
                headers={"X-Service-Api-Key": settings.SERVICE_API_KEY},
            )
            if response.status_code == status.HTTP_200_OK:
                return int(response.json().get("cancelled", 0))
            logger.error("Notification scheduled-cancel error: {}", response.text)
        except httpx.RequestError:
            logger.exception("Failed to cancel scheduled notifications")
        return 0


auth_service_client = AuthServiceClient()
notification_service_client = NotificationServiceClient()
