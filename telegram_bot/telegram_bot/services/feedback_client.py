"""HTTP client for feedback service integration."""

import httpx
from fastapi import status
from loguru import logger

from telegram_bot.config import settings


class FeedbackServiceClient:
    """HTTP client for feedback service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize feedback service HTTP client."""
        self.base_url = base_url or settings.FEEDBACK_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT)

    async def submit_pulse_survey(self, rating: int, is_anonymous: bool, auth_token: str) -> bool:
        """Submit pulse survey rating. Can be anonymous."""
        logger.info("Submitting pulse survey (rating={}, is_anonymous={})", rating, is_anonymous)
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/feedback/pulse",
                json={"rating": rating, "is_anonymous": is_anonymous},
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "X-Service-Api-Key": settings.SERVICE_API_KEY,
                },
            )
            if response.status_code == status.HTTP_201_CREATED:
                logger.info("Pulse survey submitted")
                return True
            logger.warning("Pulse survey submission failed (status={})", response.status_code)
        except httpx.RequestError:
            logger.exception("Feedback service pulse survey request failed")
            return False
        return False

    async def submit_experience_rating(self, rating: int, is_anonymous: bool, auth_token: str) -> bool:
        """Submit experience rating. Can be anonymous."""
        logger.info("Submitting experience rating (rating={}, is_anonymous={})", rating, is_anonymous)
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/feedback/experience",
                json={"rating": rating, "is_anonymous": is_anonymous},
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "X-Service-Api-Key": settings.SERVICE_API_KEY,
                },
            )
            if response.status_code == status.HTTP_201_CREATED:
                logger.info("Experience rating submitted")
                return True
            logger.warning("Experience rating submission failed (status={})", response.status_code)
        except httpx.RequestError:
            logger.exception("Feedback service experience rating request failed")
            return False
        return False

    async def submit_comment(
        self,
        comment: str,
        auth_token: str,
        contact_email: str | None = None,
        *,
        is_anonymous: bool,
        allow_contact: bool = False,
    ) -> bool:
        """Submit comment or suggestion. Can be anonymous."""
        logger.info("Submitting comment (is_anonymous={}, allow_contact={})", is_anonymous, allow_contact)
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
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "X-Service-Api-Key": settings.SERVICE_API_KEY,
                },
            )
            if response.status_code == status.HTTP_201_CREATED:
                logger.info("Comment submitted")
                return True
            logger.warning("Comment submission failed (status={})", response.status_code)
        except httpx.RequestError:
            logger.exception("Feedback service comment request failed")
            return False
        return False


# Singleton instance
feedback_client = FeedbackServiceClient()
