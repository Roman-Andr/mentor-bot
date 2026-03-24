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


# Singleton instance
checklists_service_client = ChecklistsServiceClient()
