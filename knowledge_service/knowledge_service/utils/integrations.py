"""Integration services for external APIs with caching."""

import logging
from typing import Any

import httpx
from fastapi import status

from knowledge_service.config import settings
from knowledge_service.utils import cache, cached

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """HTTP client for auth service integration with caching."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize auth service HTTP client."""
        self.base_url = base_url or settings.AUTH_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.AUTH_SERVICE_TIMEOUT)

    @cached(ttl=settings.AUTH_TOKEN_CACHE_TTL, key_prefix="auth_user")
    async def validate_token(self, token: str) -> dict[str, Any] | None:
        """Validate JWT token with auth service (cached)."""
        try:
            response = await self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Auth service request failed")
        except Exception:
            logger.exception("Token validation error")
        return None

    @cached(ttl=settings.AUTH_USER_CACHE_TTL, key_prefix="auth_user")
    async def get_user(self, user_id: int, token: str) -> dict[str, Any] | None:
        """Get user details from auth service (cached)."""
        try:
            response = await self.client.get(
                f"/api/v1/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Auth service request failed")
        except Exception:
            logger.exception("Get user error")
        return None

    async def invalidate_user_cache(self, user_id: int) -> None:
        """Invalidate cache for specific user."""
        await cache.delete_pattern(f"auth_user:*{user_id}*")

    @cached(ttl=settings.AUTH_USER_CACHE_TTL, key_prefix="auth_departments")
    async def get_departments(self, token: str) -> list[dict[str, Any]] | None:
        """Get all departments from auth service (cached)."""
        try:
            response = await self.client.get(
                "/api/v1/departments/",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                return data.get("departments", [])
        except httpx.RequestError:
            logger.exception("Auth service request failed")
        except Exception:
            logger.exception("Get departments error")
        return None


# Singleton instance
auth_service_client = AuthServiceClient()
