"""HTTP client for escalation service integration."""

from typing import Any, ClassVar

import httpx
from fastapi import status as http_status
from loguru import logger

from telegram_bot.config import settings


class EscalationServiceClient:
    """HTTP client for escalation service integration.

    Maps old telegram_bot fields to escalation_service schema:
    - title -> reason
    - description -> context.description
    - category -> type (via mapping)
    """

    # Map old category values to escalation types
    CATEGORY_TO_TYPE: ClassVar[dict[str, str]] = {
        "HR": "HR",
        "Mentor": "MENTOR",
        "Technical": "IT",
        "General": "GENERAL",
        "technical": "IT",
        "hr": "HR",
        "mentor": "MENTOR",
        "general": "GENERAL",
    }

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize escalation service HTTP client."""
        self.base_url = base_url or settings.ESCALATION_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT
        )

    def _map_category_to_type(self, category: str) -> str:
        """Map old category values to escalation service types."""
        return self.CATEGORY_TO_TYPE.get(category, "GENERAL")

    def _build_payload(
        self,
        user_id: int,
        title: str,
        description: str,
        category: str,
        priority: str = "normal",
    ) -> dict[str, Any]:
        """Build payload matching escalation_service schema.

        Maps:
        - title -> reason
        - description -> context.description
        - category -> type
        - priority -> context.priority (stored for reference)
        """
        return {
            "user_id": user_id,
            "type": self._map_category_to_type(category),
            "source": "MANUAL",  # Telegram bot uses MANUAL source
            "reason": title,
            "context": {
                "description": description,
                "priority": priority,
                "category": category,
            },
            "assigned_to": None,
            "related_entity_type": None,
            "related_entity_id": None,
        }

    async def create_escalation(
        self,
        user_id: int,
        title: str,
        description: str,
        category: str,
        auth_token: str,
        priority: str = "normal",
    ) -> dict | None:
        """Create escalation request with correct schema."""
        logger.info("Creating escalation (user_id={}, category={})", user_id, category)
        try:
            payload = self._build_payload(
                user_id=user_id,
                title=title,
                description=description,
                category=category,
                priority=priority,
            )

            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/escalations",
                json=payload,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == http_status.HTTP_201_CREATED:
                logger.info("Escalation created (user_id={})", user_id)
                return response.json()
            logger.warning("Escalation creation failed (user_id={}, status={})", user_id, response.status_code)
        except httpx.RequestError:
            logger.exception("Escalation service request failed (user_id={})", user_id)
        return None

    async def get_user_escalations(
        self, user_id: int, auth_token: str, limit: int = 10
    ) -> list[dict]:
        """Get user escalations."""
        logger.debug("Fetching user escalations (user_id={}, limit={})", user_id, limit)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/escalations/user/{user_id}",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == http_status.HTTP_200_OK:
                data = response.json()
                if isinstance(data, list):
                    logger.debug("User escalations fetched (user_id={}, count={})", user_id, len(data))
                    return data
                result = data.get("escalations", [])
                logger.debug("User escalations fetched (user_id={}, count={})", user_id, len(result))
                return result
        except httpx.RequestError:
            logger.exception("Escalation service get escalations failed (user_id={})", user_id)
        return []

    async def get_escalation_status(
        self, escalation_id: int, auth_token: str
    ) -> dict | None:
        """Get escalation status."""
        logger.debug("Fetching escalation status (escalation_id={})", escalation_id)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/escalations/{escalation_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == http_status.HTTP_200_OK:
                logger.debug("Escalation status fetched (escalation_id={})", escalation_id)
                return response.json()
            logger.warning("Escalation not found (escalation_id={})", escalation_id)
        except httpx.RequestError:
            logger.exception("Escalation service get status failed (escalation_id={})", escalation_id)
        return None

    async def update_escalation_status(
        self, escalation_id: int, status: str, auth_token: str, notes: str | None = None
    ) -> dict | None:
        """Update escalation status."""
        logger.info("Updating escalation status (escalation_id={}, status={})", escalation_id, status)
        try:
            json_data: dict[str, str | None] = {"status": status}
            if notes:
                json_data["notes"] = notes

            response = await self.client.patch(
                f"{settings.API_V1_PREFIX}/escalations/{escalation_id}",
                json=json_data,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == http_status.HTTP_200_OK:
                logger.info("Escalation status updated (escalation_id={})", escalation_id)
                return response.json()
            logger.warning("Escalation status update failed (escalation_id={}, status={})", escalation_id, response.status_code)
        except httpx.RequestError:
            logger.exception("Escalation service update status failed (escalation_id={})", escalation_id)
        return None


# Singleton instance
escalation_client = EscalationServiceClient()
