"""HTTP client for meeting service integration."""

import httpx
from fastapi import status
from loguru import logger

from telegram_bot.config import settings


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
        logger.info("Creating meeting (user_id={}, title={})", user_id, title)
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
                logger.info("Meeting created (user_id={})", user_id)
                return response.json()
            logger.warning("Meeting creation failed (user_id={}, status={})", user_id, response.status_code)
        except httpx.RequestError:
            logger.exception("Meeting service request failed (user_id={})", user_id)
        return None

    async def get_user_meetings(
        self, user_id: int, auth_token: str, limit: int = 10
    ) -> list[dict]:
        """Get user meetings."""
        logger.debug("Fetching user meetings (user_id={}, limit={})", user_id, limit)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/user-meetings",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                logger.debug("User meetings fetched (user_id={}, count={})", user_id, len(data.get("meetings", [])))
                return data.get("meetings", [])
        except httpx.RequestError:
            logger.exception("Meeting service get meetings failed (user_id={})", user_id)
        return []

    async def get_upcoming_meetings(
        self, user_id: int, auth_token: str, limit: int = 5
    ) -> list[dict]:
        """Get upcoming meetings for user."""
        logger.debug("Fetching upcoming meetings (user_id={}, limit={})", user_id, limit)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/user-meetings/upcoming",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                logger.debug("Upcoming meetings fetched (user_id={}, count={})", user_id, len(data.get("meetings", [])))
                return data.get("meetings", [])
        except httpx.RequestError:
            logger.exception("Meeting service get upcoming meetings failed (user_id={})", user_id)
        return []

    async def confirm_meeting(
        self, meeting_id: int, user_id: int, auth_token: str
    ) -> dict | None:
        """Confirm meeting attendance."""
        logger.info("Confirming meeting (meeting_id={}, user_id={})", meeting_id, user_id)
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/user-meetings/{meeting_id}/confirm",
                json={"user_id": user_id},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.info("Meeting confirmed (meeting_id={}, user_id={})", meeting_id, user_id)
                return response.json()
            logger.warning("Meeting confirmation failed (meeting_id={}, user_id={}, status={})", meeting_id, user_id, response.status_code)
        except httpx.RequestError:
            logger.exception("Meeting service confirm meeting failed (meeting_id={})", meeting_id)
        return None

    async def cancel_meeting(
        self, meeting_id: int, user_id: int, auth_token: str, reason: str | None = None
    ) -> dict | None:
        """Cancel meeting."""
        logger.info("Canceling meeting (meeting_id={}, user_id={})", meeting_id, user_id)
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
                logger.info("Meeting canceled (meeting_id={}, user_id={})", meeting_id, user_id)
                return response.json()
            logger.warning("Meeting cancellation failed (meeting_id={}, user_id={}, status={})", meeting_id, user_id, response.status_code)
        except httpx.RequestError:
            logger.exception("Meeting service cancel meeting failed (meeting_id={})", meeting_id)
        return None


# Singleton instance
meeting_client = MeetingServiceClient()
