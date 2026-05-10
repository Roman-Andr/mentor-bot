"""Cross-service user data cleanup before account deletion."""

from dataclasses import dataclass

import httpx
from loguru import logger

from auth_service.config import settings


@dataclass(frozen=True)
class CleanupTarget:
    """Internal cleanup endpoint for a service that stores user references."""

    name: str
    base_url: str
    path: str


class UserCleanupClient:
    """Calls service-owned cleanup endpoints for a deleted user."""

    def __init__(self) -> None:
        """Initialize cleanup targets from service URLs."""
        self._targets = (
            CleanupTarget("checklists", settings.CHECKLISTS_SERVICE_URL, "/api/v1/checklists/internal/users"),
            CleanupTarget("feedback", settings.FEEDBACK_SERVICE_URL, "/api/v1/feedback/internal/users"),
            CleanupTarget("knowledge", settings.KNOWLEDGE_SERVICE_URL, "/api/v1/knowledge/internal/users"),
            CleanupTarget("meetings", settings.MEETING_SERVICE_URL, "/api/v1/meetings/internal/users"),
            CleanupTarget("escalations", settings.ESCALATION_SERVICE_URL, "/api/v1/escalations/internal/users"),
            CleanupTarget("notifications", settings.NOTIFICATION_SERVICE_URL, "/api/v1/notifications/internal/users"),
        )

    async def cleanup_user_data(self, user_id: int) -> None:
        """Remove user-owned data from all services before deactivating the account."""
        headers = {"X-Service-Api-Key": settings.SERVICE_API_KEY}
        async with httpx.AsyncClient(timeout=30) as client:
            for target in self._targets:
                url = f"{target.base_url.rstrip('/')}{target.path}/{user_id}"
                logger.info("Calling user cleanup endpoint (service={}, user_id={})", target.name, user_id)
                response = await client.delete(url, headers=headers)
                if response.status_code >= 400:
                    logger.error(
                        "User cleanup failed (service={}, user_id={}, status={}, body={})",
                        target.name,
                        user_id,
                        response.status_code,
                        response.text,
                    )
                    response.raise_for_status()
                logger.info("User cleanup completed (service={}, user_id={})", target.name, user_id)
