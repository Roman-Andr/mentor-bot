"""Auth service client for fetching user preferences."""

from dataclasses import dataclass

import httpx
from loguru import logger

from notification_service.config import settings


@dataclass
class UserPreferences:
    """User preferences from auth service."""

    language: str = "ru"
    notification_telegram_enabled: bool = True
    notification_email_enabled: bool = True


class AuthClientError(Exception):
    """Auth client error."""


class AuthClient:
    """Client for communicating with auth service."""

    def __init__(self) -> None:
        """Initialize auth client."""
        self._base_url = settings.AUTH_SERVICE_URL
        self._timeout = settings.AUTH_SERVICE_TIMEOUT
        self._api_key = settings.SERVICE_API_KEY

    async def get_user_preferences(self, user_id: int) -> UserPreferences:
        """
        Get user preferences from auth service.

        Args:
            user_id: User ID to fetch preferences for

        Returns:
            UserPreferences object

        Raises:
            AuthClientError: If request fails
        """
        url = f"{self._base_url}/api/v1/users/{user_id}/preferences"
        headers = {}
        if self._api_key:
            headers["X-Service-API-Key"] = self._api_key

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return UserPreferences(
                    language=data.get("language", "ru"),
                    notification_telegram_enabled=data.get("notification_telegram_enabled", True),
                    notification_email_enabled=data.get("notification_email_enabled", True),
                )
        except httpx.HTTPStatusError as e:
            logger.error("Auth service request failed: {}", e)
            raise AuthClientError(f"Auth service request failed: {e}") from e
        except httpx.RequestError as e:
            logger.error("Auth service connection error: {}", e)
            raise AuthClientError(f"Auth service connection error: {e}") from e
        except Exception as e:
            logger.error("Unexpected error fetching user preferences: {}", e)
            raise AuthClientError(f"Unexpected error: {e}") from e
