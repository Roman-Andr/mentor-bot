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
        self, rating: int, is_anonymous: bool, auth_token: str
    ) -> bool:
        """Submit pulse survey rating. Can be anonymous."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/feedback/pulse",
                json={"rating": rating, "is_anonymous": is_anonymous},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
        except httpx.RequestError:
            logger.exception("Feedback service pulse survey request failed")
            return False
        else:
            return response.status_code == status.HTTP_201_CREATED

    async def submit_experience_rating(
        self, rating: int, is_anonymous: bool, auth_token: str
    ) -> bool:
        """Submit experience rating. Can be anonymous."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/feedback/experience",
                json={"rating": rating, "is_anonymous": is_anonymous},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
        except httpx.RequestError:
            logger.exception("Feedback service experience rating request failed")
            return False
        else:
            return response.status_code == status.HTTP_201_CREATED

    async def submit_comment(
        self,
        comment: str,
        is_anonymous: bool,
        auth_token: str,
        allow_contact: bool = False,
        contact_email: str | None = None,
    ) -> bool:
        """Submit comment or suggestion. Can be anonymous."""
        try:
            payload: dict = {
                "comment": comment,
                "is_anonymous": is_anonymous,
                "allow_contact": allow_contact,
            }
            if is_anonymous and allow_contact and contact_email:
                payload["contact_email"] = contact_email

            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/feedback/comments",
                json=payload,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
        except httpx.RequestError:
            logger.exception("Feedback service comment request failed")
            return False
        else:
            return response.status_code == status.HTTP_201_CREATED


# Singleton instance
feedback_client = FeedbackServiceClient()
