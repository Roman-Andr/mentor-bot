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

    async def get_assigned_tasks(self, auth_token: str) -> list[dict]:
        """Get tasks assigned to user (NO CACHE for real-time status)."""
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
        self, task_id: int, new_status: str, auth_token: str
    ) -> dict | None:
        """Update task status."""
        try:
            # Convert status to uppercase enum value expected by the service
            status_upper = new_status.upper()
            response = await self.client.put(
                f"{settings.API_V1_PREFIX}/tasks/{task_id}",
                json={"status": status_upper},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                await invalidate_cache("checklists_user:*")
                await invalidate_cache("assigned_tasks:*")
                return response.json()
            logger.error(
                "Update task %s failed: %s - %s",
                task_id,
                response.status_code,
                response.text,
            )
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
                await invalidate_cache("checklist_tasks:*")
                return response.json()
            logger.error(
                "Complete task %s failed: %s - %s",
                task_id,
                response.status_code,
                response.text,
            )
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

    async def get_task_details(
        self, task_id: int, auth_token: str, checklist_id: int | None = None
    ) -> dict | None:
        """Get detailed task information."""
        # Try to find task in assigned tasks first
        assigned_tasks = await self.get_assigned_tasks(auth_token)
        for task in assigned_tasks:
            if task.get("id") == task_id:
                return task

        # If checklist_id provided, try to find in checklist tasks
        if checklist_id:
            checklist_tasks = await self.get_checklist_tasks(checklist_id, auth_token)
            for task in checklist_tasks:
                if task.get("id") == task_id:
                    return task

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

    async def upload_task_attachment(
        self,
        task_id: int,
        file_content: bytes | object,
        filename: str,
        auth_token: str,
        description: str | None = None,
    ) -> dict | None:
        """Upload a file attachment to a task."""
        try:
            from io import BytesIO

            # Handle both bytes and file-like objects (BytesIO)
            if isinstance(file_content, bytes):
                file_obj = BytesIO(file_content)
            else:
                file_obj = file_content

            files = {"file": (filename, file_obj, "application/octet-stream")}
            data = {"description": description} if description else {}
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/tasks/{task_id}/attachments",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
            # Log error response for debugging
            logger.error(
                f"Upload failed: {response.status_code} - {response.text[:200]}"
            )
        except httpx.RequestError:
            logger.exception("Checklists service upload attachment failed")
        return None

    async def get_task_attachments(self, task_id: int, auth_token: str) -> list[dict]:
        """Get all attachments for a task."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/tasks/{task_id}/attachments",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Checklists service get attachments failed")
        return []

    async def download_task_attachment(
        self, task_id: int, filename: str, auth_token: str
    ) -> bytes | None:
        """Download a task attachment file."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/tasks/{task_id}/attachments/file/{filename}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.content
        except httpx.RequestError:
            logger.exception("Checklists service download attachment failed")
        return None

    async def invalidate_task_cache(
        self, auth_token: str, checklist_id: int | None = None
    ) -> None:
        """Invalidate task-related caches after status changes."""
        logger.info(
            f"Invalidating cache for token {auth_token[:20]}... checklist={checklist_id}"
        )
        # Invalidate assigned tasks cache - use pattern matching for full key format
        pattern1 = f"*assigned_tasks*:{auth_token}*"
        deleted1 = await invalidate_cache(pattern1)
        logger.info(
            f"Invalidated assigned_tasks cache: {deleted1} keys deleted with pattern {pattern1}"
        )
        # Invalidate checklist tasks cache if checklist_id provided
        if checklist_id is not None:
            pattern2 = f"*checklist_tasks*:{checklist_id}*{auth_token}*"
            deleted2 = await invalidate_cache(pattern2)
            logger.info(
                f"Invalidated checklist_tasks cache: {deleted2} keys deleted with pattern {pattern2}"
            )


# Singleton instance
checklists_client = ChecklistsServiceClient()
