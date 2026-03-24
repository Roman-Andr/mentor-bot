"""HTTP client for checklists service integration."""

import logging

import httpx
from fastapi import status

from telegram_bot.config import settings
from telegram_bot.utils.cache import cached, invalidate_cache

logger = logging.getLogger(__name__)


class ChecklistsServiceClient:
    """HTTP client for checklists service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize checklists service HTTP client."""
        self.base_url = base_url or settings.CHECKLISTS_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT
        )

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
        except httpx.RequestError:
            logger.exception("Checklists service request failed")
        return []

    @cached(ttl=30, key_prefix="checklist_tasks")
    async def get_checklist_tasks(
        self, checklist_id: int, auth_token: str
    ) -> list[dict]:
        """Get tasks for checklist (cached)."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/tasks/checklist/{checklist_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Checklists service tasks request failed")
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
        except httpx.RequestError:
            logger.exception("Checklists service assigned tasks request failed")
        return []

    async def update_task_status(
        self, task_id: int, status: str, auth_token: str
    ) -> dict | None:
        """Update task status."""
        try:
            response = await self.client.put(
                f"{settings.API_V1_PREFIX}/tasks/{task_id}",
                json={"status": status},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                await invalidate_cache("checklists_user:*")
                await invalidate_cache("assigned_tasks:*")
                return response.json()
        except httpx.RequestError:
            logger.exception("Checklists service update task failed")
        return None

    async def complete_task(
        self, task_id: int, auth_token: str, notes: str | None = None
    ) -> dict | None:
        """Mark task as completed."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/tasks/{task_id}/complete",
                params={"completion_notes": notes} if notes else None,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                await invalidate_cache("checklists_user:*")
                await invalidate_cache("assigned_tasks:*")
                return response.json()
        except httpx.RequestError:
            logger.exception("Checklists service complete task failed")
        return None

    @cached(ttl=60, key_prefix="checklist_progress")
    async def get_checklist_progress(
        self, checklist_id: int, auth_token: str
    ) -> dict | None:
        """Get checklist progress details (cached)."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/checklists/{checklist_id}/progress",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Checklists service progress request failed")
        return None

    async def get_task_details(self, task_id: int, auth_token: str) -> dict | None:
        """Get detailed task information."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Checklists service task details failed")
        return None

    async def start_task(self, task_id: int, auth_token: str) -> dict | None:
        """Start working on a task (set status to in_progress)."""
        return await self.update_task_status(task_id, "in_progress", auth_token)

    @cached(ttl=120, key_prefix="checklist_templates")
    async def get_templates(self, auth_token: str) -> list[dict]:
        """Get checklist templates for admin panel."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/templates",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Checklists service templates request failed")
        return []

    async def get_overdue_tasks(self, auth_token: str) -> list[dict]:
        """Get overdue tasks for admin panel."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/tasks/overdue",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Checklists service overdue tasks failed")
        return []

    async def get_admin_stats(self, auth_token: str) -> dict:
        """Get checklist statistics for admin panel."""
        stats: dict = {"active_checklists": 0, "completed_tasks": 0, "pending_tasks": 0}
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/checklists/stats",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Checklists service stats request failed")
        return stats


# Singleton instance
checklists_client = ChecklistsServiceClient()
