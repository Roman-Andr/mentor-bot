"""HTTP client for escalation service integration."""

import logging

import httpx
from fastapi import status

from telegram_bot.config import settings

logger = logging.getLogger(__name__)


class EscalationServiceClient:
    """HTTP client for escalation service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize escalation service HTTP client."""
        self.base_url = base_url or settings.ESCALATION_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT)

    async def create_escalation(
        self, user_id: int, title: str, description: str, category: str, priority: str = "normal"
    ) -> dict | None:
        """Create escalation request."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/escalations",
                json={
                    "user_id": user_id,
                    "title": title,
                    "description": description,
                    "category": category,
                    "priority": priority,
                },
            )
            if response.status_code == status.HTTP_201_CREATED:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Escalation service request failed: {e}")
        return None

    async def get_user_escalations(self, user_id: int, limit: int = 10) -> list[dict]:
        """Get user escalations."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/escalations/user/{user_id}",
                params={"limit": limit},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                return data.get("escalations", [])
        except httpx.RequestError as e:
            logger.exception(f"Escalation service get escalations failed: {e}")
        return []

    async def get_escalation_status(self, escalation_id: int) -> dict | None:
        """Get escalation status."""
        try:
            response = await self.client.get(f"{settings.API_V1_PREFIX}/escalations/{escalation_id}")
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Escalation service get status failed: {e}")
        return None

    async def update_escalation_status(self, escalation_id: int, status: str, notes: str | None = None) -> dict | None:
        """Update escalation status."""
        try:
            json_data = {"status": status}
            if notes:
                json_data["notes"] = notes

            response = await self.client.put(
                f"{settings.API_V1_PREFIX}/escalations/{escalation_id}/status",
                json=json_data,
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Escalation service update status failed: {e}")
        return None


# Singleton instance
escalation_client = EscalationServiceClient()
