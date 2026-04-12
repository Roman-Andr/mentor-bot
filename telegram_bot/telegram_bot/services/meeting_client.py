"""HTTP client for meeting service integration."""

import logging

import httpx
from fastapi import status

from telegram_bot.config import settings

logger = logging.getLogger(__name__)


class MeetingServiceClient:
    """HTTP client for meeting service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize meeting service HTTP client."""
        self.base_url = base_url or settings.MEETING_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT
        )

    async def create_meeting(
        self,
        user_id: int,
        title: str,
        description: str,
        participant_ids: list[int],
        scheduled_at: str,
        auth_token: str,
        duration_minutes: int = 60,
        meeting_type: str = "onboarding",
    ) -> dict | None:
        """Create meeting."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/user-meetings",
                json={
                    "user_id": user_id,
                    "title": title,
                    "description": description,
                    "participant_ids": participant_ids,
                    "scheduled_at": scheduled_at,
                    "duration_minutes": duration_minutes,
                    "meeting_type": meeting_type,
                },
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_201_CREATED:
                return response.json()
        except httpx.RequestError:
            logger.exception("Meeting service request failed")
        return None

    async def get_user_meetings(
        self, user_id: int, auth_token: str, limit: int = 10
    ) -> list[dict]:
        """Get user meetings."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/user-meetings",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                return data.get("meetings", [])
        except httpx.RequestError:
            logger.exception("Meeting service get meetings failed")
        return []

    async def get_upcoming_meetings(
        self, user_id: int, auth_token: str, limit: int = 5
    ) -> list[dict]:
        """Get upcoming meetings for user."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/user-meetings/upcoming",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                return data.get("meetings", [])
        except httpx.RequestError:
            logger.exception("Meeting service get upcoming meetings failed")
        return []

    async def confirm_meeting(
        self, meeting_id: int, user_id: int, auth_token: str
    ) -> dict | None:
        """Confirm meeting attendance."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/user-meetings/{meeting_id}/confirm",
                json={"user_id": user_id},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Meeting service confirm meeting failed")
        return None

    async def cancel_meeting(
        self, meeting_id: int, user_id: int, auth_token: str, reason: str | None = None
    ) -> dict | None:
        """Cancel meeting."""
        try:
            json_data: dict[str, int | str] = {"user_id": user_id}
            if reason:
                json_data["reason"] = reason

            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/user-meetings/{meeting_id}/cancel",
                json=json_data,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Meeting service cancel meeting failed")
        return None


# Singleton instance
meeting_client = MeetingServiceClient()
