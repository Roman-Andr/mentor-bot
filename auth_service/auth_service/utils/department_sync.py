"""Department sync client for inter-service communication."""

import logging

import httpx

from auth_service.config import settings

logger = logging.getLogger(__name__)


class DepartmentSyncClient:
    """Client for syncing departments to other services."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=30.0)
        self._headers = {"X-Service-Api-Key": settings.SERVICE_API_KEY}

    async def close(self) -> None:
        await self._client.aclose()

    async def create_department_in_service(
        self,
        service_url: str,
        name: str,
        description: str | None,
    ) -> bool:
        """Create department in a specific service."""
        try:
            response = await self._client.post(
                f"{service_url}/api/v1/departments/",
                json={"name": name, "description": description},
                headers=self._headers,
            )
            if response.status_code in (200, 201):
                logger.info(f"Department '{name}' created in {service_url}")
                return True
            if response.status_code == 409:
                logger.info(f"Department '{name}' already exists in {service_url}")
                return True
            logger.warning(f"Failed to create department in {service_url}: {response.status_code} - {response.text}")
        except httpx.RequestError:
            logger.exception(f"Request to {service_url} failed")
        except Exception:
            logger.exception(f"Error creating department in {service_url}")
        return False

    async def sync_department(
        self,
        name: str,
        description: str | None,
    ) -> dict[str, bool]:
        """Sync department to all other services."""
        results: dict[str, bool] = {}

        services = {
            "checklists": settings.CHECKLISTS_SERVICE_URL,
            "knowledge": settings.KNOWLEDGE_SERVICE_URL,
            "meeting": settings.MEETING_SERVICE_URL,
        }

        for service_name, service_url in services.items():
            results[service_name] = await self.create_department_in_service(service_url, name, description)

        return results


department_sync_client = DepartmentSyncClient()
