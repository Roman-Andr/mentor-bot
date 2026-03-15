"""HTTP client for checklists service integration."""

import logging

import httpx
from fastapi import status

from telegram_bot.config import settings
from telegram_bot.utils.cache import cached

logger = logging.getLogger(__name__)


class ChecklistsServiceClient:
    """HTTP client for checklists service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize checklists service HTTP client."""
        self.base_url = base_url or settings.CHECKLISTS_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT)

    @cached(ttl=60, key_prefix="checklists_user")
    async def get_user_checklists(self, user_id: int, auth_token: str) -> list[dict]:
        """Get checklists for user (cached)."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/checklists/",
                params={"user_id": user_id},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                return data.get("checklists", [])
        except httpx.RequestError as e:
            logger.exception(f"Checklists service request failed: {e}")
        return []

    @cached(ttl=30, key_prefix="checklist_tasks")
    async def get_checklist_tasks(self, checklist_id: int, auth_token: str) -> list[dict]:
        """Get tasks for checklist (cached)."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/tasks/checklist/{checklist_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Checklists service tasks request failed: {e}")
        return []

    @cached(ttl=30, key_prefix="assigned_tasks")
    async def get_assigned_tasks(self, auth_token: str) -> list[dict]:
        """Get tasks assigned to user (cached)."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/tasks/assigned-to-me",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Checklists service assigned tasks request failed: {e}")
        return []

    async def update_task_status(self, task_id: int, status: str, auth_token: str) -> dict | None:
        """Update task status."""
        try:
            response = await self.client.put(
                f"{settings.API_V1_PREFIX}/tasks/{task_id}",
                json={"status": status},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                # Invalidate cache for this user's tasks
                from telegram_bot.utils.cache import invalidate_cache

                await invalidate_cache("checklists_user:*")
                await invalidate_cache("assigned_tasks:*")
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Checklists service update task failed: {e}")
        return None

    async def complete_task(self, task_id: int, auth_token: str, notes: str | None = None) -> dict | None:
        """Mark task as completed."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/tasks/{task_id}/complete",
                params={"completion_notes": notes} if notes else None,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                # Invalidate cache for this user's tasks
                from telegram_bot.utils.cache import invalidate_cache

                await invalidate_cache("checklists_user:*")
                await invalidate_cache("assigned_tasks:*")
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Checklists service complete task failed: {e}")
        return None

    @cached(ttl=60, key_prefix="checklist_progress")
    async def get_checklist_progress(self, checklist_id: int, auth_token: str) -> dict | None:
        """Get checklist progress details (cached)."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/checklists/{checklist_id}/progress",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Checklists service progress request failed: {e}")
        return None


# Singleton instance
checklists_client = ChecklistsServiceClient()
