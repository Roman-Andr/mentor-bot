"""Integration services for external APIs."""

import logging
from typing import Any

import httpx

from auth_service.config import settings

logger = logging.getLogger(__name__)


class ChecklistsServiceClient:
    """HTTP client for checklists service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize checklists service HTTP client."""
        self.base_url = base_url or settings.CHECKLISTS_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def aclose(self) -> None:
        """Close the HTTP client and release resources."""
        await self.client.aclose()

    async def auto_create_checklists(
        self,
        user_id: int,
        employee_id: str,
        department_id: int | None,
        position: str | None,
        mentor_id: int | None,
    ) -> list[dict[str, Any]]:
        """Auto-create checklists for a user based on matching templates."""
        try:
            response = await self.client.post(
                "/api/v1/checklists/auto-create",
                json={
                    "user_id": user_id,
                    "employee_id": employee_id,
                    "department_id": department_id,
                    "position": position,
                    "mentor_id": mentor_id,
                },
                headers={"X-Service-Api-Key": settings.SERVICE_API_KEY},
            )
            if response.status_code in (200, 201):
                return response.json()
            logger.warning("Checklists auto-create returned %s: %s", response.status_code, response.text)
        except httpx.RequestError:
            logger.exception("Checklists service request failed")
        except Exception:
            logger.exception("Auto-create checklists error")
        return []


class NotificationServiceClient:
    """HTTP client for notification service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize notification service HTTP client."""
        # Default to localhost:8004 for notification service
        self.base_url = base_url or settings.NOTIFICATION_SERVICE_URL or "http://localhost:8004"
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def aclose(self) -> None:
        """Close the HTTP client and release resources."""
        await self.client.aclose()

    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str,
    ) -> bool:
        """Send password reset email via notification service."""
        try:
            # Build reset URL - this should be configurable
            reset_url = f"{settings.ADMIN_WEB_URL}/reset-password?token={reset_token}"

            response = await self.client.post(
                "/api/v1/notifications/email/send",
                json={
                    "to_email": to_email,
                    "template": "password_reset",
                    "variables": {
                        "user_name": user_name,
                        "reset_url": reset_url,
                        "reset_token": reset_token,
                        "expiry_hours": "24",
                    },
                },
                headers={"X-Service-Api-Key": settings.SERVICE_API_KEY},
            )
            if response.status_code in (200, 201, 202):
                logger.info("Password reset email sent to %s", to_email)
                return True
            logger.warning(
                "Failed to send password reset email - status %s: %s",
                response.status_code,
                response.text,
            )
        except httpx.RequestError:
            logger.exception("Notification service request failed for password reset")
        except Exception:
            logger.exception("Send password reset email error")
        return False

    async def send_password_reset_confirmation_email(
        self,
        to_email: str,
        user_name: str,
    ) -> bool:
        """Send password reset confirmation email via notification service."""
        try:
            response = await self.client.post(
                "/api/v1/notifications/email/send",
                json={
                    "to_email": to_email,
                    "template": "password_reset_confirmation",
                    "variables": {
                        "user_name": user_name,
                    },
                },
                headers={"X-Service-Api-Key": settings.SERVICE_API_KEY},
            )
            if response.status_code in (200, 201, 202):
                logger.info("Password reset confirmation email sent to %s", to_email)
                return True
            logger.warning(
                "Failed to send password reset confirmation - status %s: %s",
                response.status_code,
                response.text,
            )
        except httpx.RequestError:
            logger.exception("Notification service request failed for confirmation")
        except Exception:
            logger.exception("Send password reset confirmation error")
        return False


# Singleton instances
checklists_service_client = ChecklistsServiceClient()
notification_service_client = NotificationServiceClient()
