"""HTTP client for authentication service integration."""

import logging

import httpx
from fastapi import status

from telegram_bot.config import settings
from telegram_bot.utils import cache, cached

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """HTTP client for auth service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize auth service HTTP client."""
        self.base_url = base_url or settings.AUTH_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT)

    @cached(ttl=300, key_prefix="auth_user")
    async def get_user_by_telegram_id(self, telegram_id: int, auth_token: str) -> dict | None:
        """Get user by Telegram ID (cached)."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/users/by-telegram/{telegram_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Auth service request failed: {e}")
        return None

    async def authenticate_with_telegram(self, telegram_data: dict) -> dict | None:
        """Authenticate user with Telegram data."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/auth/telegram",
                json=telegram_data,
                headers={"X-API-Key": settings.TELEGRAM_API_KEY},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Auth service authentication failed: {e}")
        return None

    async def register_with_invitation(self, token: str, telegram_data: dict) -> dict | None:
        """Register user with invitation token."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/auth/register/{token}",
                json=telegram_data,
                headers={"X-API-Key": settings.TELEGRAM_API_KEY},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Auth service registration failed: {e}")
        return None

    async def validate_invitation_token(self, token: str) -> dict | None:
        """Validate invitation token."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/invitations/token/{token}",
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Auth service token validation failed: {e}")
        return None

    async def get_current_user(self, token: str) -> dict | None:
        """Get current user info by token."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError as e:
            logger.exception(f"Auth service get user failed: {e}")
        return None

    async def invalidate_user_cache(self, telegram_id: int) -> None:
        """Invalidate cache for specific user."""
        await cache.delete_pattern(f"auth_user:*{telegram_id}*")


# Singleton instance
auth_client = AuthServiceClient()
