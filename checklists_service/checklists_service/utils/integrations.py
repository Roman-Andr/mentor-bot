"""Integration services for external APIs with caching."""

import logging
from typing import Any

import httpx
from fastapi import status

from checklists_service.config import settings
from checklists_service.services.circuit_breaker import auth_service_circuit_breaker
from checklists_service.utils import cache, cached

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """HTTP client for auth service integration with caching."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize auth service HTTP client."""
        self.base_url = base_url or settings.AUTH_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.AUTH_SERVICE_TIMEOUT)

    async def _make_validate_token_request(self, token: str) -> dict[str, Any] | None:
        """Make the actual HTTP request to validate token."""
        response = await self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == status.HTTP_200_OK:
            return response.json()
        return None

    @cached(ttl=300, key_prefix="auth_user")
    async def validate_token(self, token: str) -> dict[str, Any] | None:
        """Validate JWT token with auth service (cached) with circuit breaker protection."""
        try:
            return await auth_service_circuit_breaker.call(
                self._make_validate_token_request, token
            )
        except httpx.RequestError:
            logger.exception("Auth service request failed")
        except Exception:
            logger.exception("Token validation error")
        return None

    async def _make_get_user_request(self, user_id: int, auth_token: str) -> dict[str, Any] | None:
        """Make the actual HTTP request to get user details."""
        response = await self.client.get(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if response.status_code == status.HTTP_200_OK:
            return response.json()
        return None

    @cached(ttl=600, key_prefix="auth_user")
    async def get_user(self, user_id: int, auth_token: str) -> dict[str, Any] | None:
        """Get user details from auth service (cached) with circuit breaker protection."""
        try:
            return await auth_service_circuit_breaker.call(
                self._make_get_user_request, user_id, auth_token
            )
        except httpx.RequestError:
            logger.exception("Auth service request failed")
        except Exception:
            logger.exception("Get user error")
        return None

    async def invalidate_user_cache(self, user_id: int) -> None:
        """Invalidate cache for specific user."""
        await cache.delete_pattern(f"auth_user:*{user_id}*")


# Singleton instance
auth_service_client = AuthServiceClient()
