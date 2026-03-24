"""HTTP client for feedback service integration."""

import logging

import httpx
from fastapi import status

from telegram_bot.config import settings

logger = logging.getLogger(__name__)


class FeedbackServiceClient:
    """HTTP client for feedback service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize feedback service HTTP client."""
        self.base_url = base_url or settings.FEEDBACK_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT
        )

    async def submit_pulse_survey(
        self, user_id: int, rating: int, auth_token: str
    ) -> bool:
        """Submit pulse survey rating."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/feedback/pulse",
                json={"user_id": user_id, "rating": rating},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
        except httpx.RequestError:
            logger.exception("Feedback service pulse survey request failed")
            return False
        else:
            return response.status_code == status.HTTP_201_CREATED

    async def submit_experience_rating(
        self, user_id: int, rating: int, auth_token: str
    ) -> bool:
        """Submit experience rating."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/feedback/experience",
                json={"user_id": user_id, "rating": rating},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
        except httpx.RequestError:
            logger.exception("Feedback service experience rating request failed")
            return False
        else:
            return response.status_code == status.HTTP_201_CREATED

    async def submit_comment(self, user_id: int, comment: str, auth_token: str) -> bool:
        """Submit comment or suggestion."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/feedback/comments",
                json={"user_id": user_id, "comment": comment},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
        except httpx.RequestError:
            logger.exception("Feedback service comment request failed")
            return False
        else:
            return response.status_code == status.HTTP_201_CREATED


# Singleton instance
feedback_client = FeedbackServiceClient()
