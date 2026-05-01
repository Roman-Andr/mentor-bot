"""HTTP client for authentication service integration."""

import httpx
from fastapi import status
from loguru import logger

from telegram_bot.config import settings
from telegram_bot.utils import cache, cached


class AuthServiceClient:
    """HTTP client for auth service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize auth service HTTP client."""
        self.base_url = base_url or settings.AUTH_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT
        )

    @cached(ttl=300, key_prefix="auth_user")
    async def get_user_by_telegram_id(
        self, telegram_id: int, auth_token: str
    ) -> dict | None:
        """Get user by Telegram ID (cached)."""
        logger.debug("Fetching user by telegram_id (telegram_id={})", telegram_id)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/users/by-telegram/{telegram_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("User found by telegram_id (telegram_id={})", telegram_id)
                return response.json()
            logger.warning("User not found by telegram_id (telegram_id={}, status={})", telegram_id, response.status_code)
        except httpx.RequestError:
            logger.exception("Auth service request failed (telegram_id={})", telegram_id)
        return None

    async def authenticate_with_telegram(self, telegram_data: dict) -> dict | None:
        """Authenticate user with Telegram data."""
        logger.debug("Authenticating with Telegram (telegram_id={})", telegram_data.get("telegram_id"))
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/auth/telegram",
                json=telegram_data,
                headers={"X-API-Key": settings.TELEGRAM_API_KEY},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.info("Telegram authentication successful (telegram_id={})", telegram_data.get("telegram_id"))
                return response.json()
            logger.warning("Telegram authentication failed (telegram_id={}, status={})", telegram_data.get("telegram_id"), response.status_code)
        except httpx.RequestError:
            logger.exception("Auth service authentication failed (telegram_id={})", telegram_data.get("telegram_id"))
        return None

    async def register_with_invitation(
        self, token: str, telegram_data: dict
    ) -> dict | None:
        """Register user with invitation token."""
        logger.debug("Registering with invitation (telegram_id={})", telegram_data.get("telegram_id"))
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/auth/register/{token}",
                json=telegram_data,
                headers={"X-API-Key": settings.TELEGRAM_API_KEY},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.info("Registration successful (telegram_id={})", telegram_data.get("telegram_id"))
                return response.json()
            logger.warning("Registration failed (telegram_id={}, status={})", telegram_data.get("telegram_id"), response.status_code)
        except httpx.RequestError:
            logger.exception("Auth service registration failed (telegram_id={})", telegram_data.get("telegram_id"))
        return None

    async def validate_invitation_token(self, token: str) -> dict | None:
        """Validate invitation token."""
        logger.debug("Validating invitation token")
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/invitations/token/{token}",
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("Invitation token valid")
                return response.json()
            logger.warning("Invitation token invalid (status={})", response.status_code)
        except httpx.RequestError:
            logger.exception("Auth service token validation failed")
        return None

    async def get_current_user(self, token: str) -> dict | None:
        """Get current user info by token."""
        logger.debug("Fetching current user")
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("Current user fetched")
                return response.json()
            logger.warning("Get current user failed (status={})", response.status_code)
        except httpx.RequestError:
            logger.exception("Auth service get user failed")
        return None

    async def get_mentor_info(self, mentor_id: int, auth_token: str) -> dict | None:
        """Get mentor user info by ID."""
        logger.debug("Fetching mentor info (mentor_id={})", mentor_id)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/users/{mentor_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("Mentor info fetched (mentor_id={})", mentor_id)
                return response.json()
            logger.warning("Mentor not found (mentor_id={}, status={})", mentor_id, response.status_code)
        except httpx.RequestError:
            logger.exception("Auth service get mentor failed (mentor_id={})", mentor_id)
        return None

    async def list_users(
        self, auth_token: str, *, page: int = 1, size: int = 20
    ) -> dict | None:
        """List users for admin panel."""
        logger.debug("Listing users (page={}, size={})", page, size)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/users",
                params={"page": page, "size": size},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("Users listed (page={}, size={})", page, size)
                return response.json()
            logger.warning("List users failed (status={})", response.status_code)
        except httpx.RequestError:
            logger.exception("Auth service list users failed")
        return None

    async def get_total_users(self, auth_token: str) -> int:
        """Get total user count."""
        logger.debug("Fetching total users count")
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/users",
                params={"page": 1, "size": 1},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                total = data.get("total", 0)
                logger.debug("Total users count: {}", total)
                return total
        except httpx.RequestError:
            logger.exception("Auth service total users failed")
        return 0

    async def invalidate_user_cache(self, telegram_id: int) -> None:
        """Invalidate cache for specific user."""
        logger.debug("Invalidating user cache (telegram_id={})", telegram_id)
        await cache.delete_pattern(f"auth_user:*{telegram_id}*")

    async def get_user_preferences(self, user_id: int, auth_token: str) -> dict | None:
        """Get user preferences."""
        logger.debug("Fetching user preferences (user_id={})", user_id)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/users/{user_id}/preferences",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("User preferences fetched (user_id={})", user_id)
                return response.json()
            logger.warning("Get user preferences failed (user_id={}, status={})", user_id, response.status_code)
        except httpx.RequestError:
            logger.exception("Auth service get preferences failed (user_id={})", user_id)
        return None

    async def update_user_preferences(self, user_id: int, preferences: dict, auth_token: str) -> dict | None:
        """Update user preferences."""
        logger.debug("Updating user preferences (user_id={})", user_id)
        try:
            response = await self.client.put(
                f"{settings.API_V1_PREFIX}/users/me/preferences",
                json=preferences,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.info("User preferences updated (user_id={})", user_id)
                return response.json()
            logger.warning("Update user preferences failed (user_id={}, status={})", user_id, response.status_code)
        except httpx.RequestError:
            logger.exception("Auth service update preferences failed (user_id={})", user_id)
        return None

# Singleton instance
auth_client = AuthServiceClient()
