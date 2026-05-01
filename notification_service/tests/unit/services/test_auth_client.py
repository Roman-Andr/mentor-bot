"""Unit tests for notification_service/services/auth_client.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from notification_service.config import settings
from notification_service.services.auth_client import AuthClient, AuthClientError, UserPreferences


class TestUserPreferences:
    """Tests for UserPreferences dataclass."""

    def test_init_with_default_values(self) -> None:
        """UserPreferences initializes with default values."""
        prefs = UserPreferences()

        assert prefs.language == "ru"
        assert prefs.notification_telegram_enabled is True
        assert prefs.notification_email_enabled is True

    def test_init_with_custom_values(self) -> None:
        """UserPreferences initializes with custom values."""
        prefs = UserPreferences(
            language="en",
            notification_telegram_enabled=False,
            notification_email_enabled=False,
        )

        assert prefs.language == "en"
        assert prefs.notification_telegram_enabled is False
        assert prefs.notification_email_enabled is False


class TestAuthClient:
    """Tests for AuthClient class."""

    def test_init_sets_attributes_from_settings(self) -> None:
        """AuthClient __init__ sets attributes from settings (lines 29-31)."""
        client = AuthClient()

        assert client._base_url == settings.AUTH_SERVICE_URL
        assert client._timeout == settings.AUTH_SERVICE_TIMEOUT
        assert client._api_key == settings.SERVICE_API_KEY

    async def test_get_user_preferences_success(self) -> None:
        """Successfully fetches user preferences from auth service (lines 46-60)."""
        client = AuthClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "language": "en",
            "notification_telegram_enabled": False,
            "notification_email_enabled": True,
        }

        mock_http_client = MagicMock()
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            result = await client.get_user_preferences(42)

        assert result.language == "en"
        assert result.notification_telegram_enabled is False
        assert result.notification_email_enabled is True

    async def test_get_user_preferences_with_defaults(self) -> None:
        """Uses default values when auth service returns partial data (lines 56-59)."""
        client = AuthClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Empty response

        mock_http_client = MagicMock()
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            result = await client.get_user_preferences(42)

        assert result.language == "ru"  # Default
        assert result.notification_telegram_enabled is True  # Default
        assert result.notification_email_enabled is True  # Default

    async def test_get_user_preferences_includes_api_key_header(self) -> None:
        """Includes X-Service-API-Key header when API key is configured (lines 48-49)."""
        client = AuthClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_http_client = MagicMock()
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            await client.get_user_preferences(42)

        # Verify the API key header was included
        call_kwargs = mock_http_client.get.call_args.kwargs
        assert "headers" in call_kwargs
        assert "X-Service-API-Key" in call_kwargs["headers"]

    async def test_get_user_preferences_without_api_key_header(self) -> None:
        """Does not include API key header when SERVICE_API_KEY is None (lines 48-49)."""
        with patch.object(settings, "SERVICE_API_KEY", None):
            client = AuthClient()

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}

            mock_http_client = MagicMock()
            mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
            mock_http_client.__aexit__ = AsyncMock(return_value=None)
            mock_http_client.get = AsyncMock(return_value=mock_response)

            with patch("httpx.AsyncClient", return_value=mock_http_client):
                await client.get_user_preferences(42)

            # Verify the API key header was not included
            call_kwargs = mock_http_client.get.call_args.kwargs
            assert "headers" in call_kwargs
            assert "X-Service-API-Key" not in call_kwargs["headers"]

    async def test_get_user_preferences_uses_correct_url(self) -> None:
        """Constructs correct URL for user preferences endpoint (line 46)."""
        client = AuthClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_http_client = MagicMock()
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            await client.get_user_preferences(42)

        expected_url = f"{settings.AUTH_SERVICE_URL}/api/v1/users/42/preferences"
        call_args = mock_http_client.get.call_args.args
        assert call_args[0] == expected_url

    async def test_get_user_preferences_raises_on_http_status_error(self) -> None:
        """Raises AuthClientError on HTTP status error (lines 61-63)."""
        client = AuthClient()

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=MagicMock(), response=MagicMock()
        )

        mock_http_client = MagicMock()
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            with pytest.raises(AuthClientError, match="Auth service request failed"):
                await client.get_user_preferences(42)

    async def test_get_user_preferences_raises_on_request_error(self) -> None:
        """Raises AuthClientError on connection error (lines 64-66)."""
        client = AuthClient()

        mock_http_client = MagicMock()
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(side_effect=httpx.RequestError("Connection error"))

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            with pytest.raises(AuthClientError, match="Auth service connection error"):
                await client.get_user_preferences(42)

    async def test_get_user_preferences_raises_on_generic_exception(self) -> None:
        """Raises AuthClientError on unexpected error (lines 67-69)."""
        client = AuthClient()

        mock_http_client = MagicMock()
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(side_effect=ValueError("Unexpected error"))

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            with pytest.raises(AuthClientError, match="Unexpected error"):
                await client.get_user_preferences(42)

    async def test_get_user_preferences_uses_timeout_from_settings(self) -> None:
        """Uses timeout from settings for HTTP request (line 52)."""
        client = AuthClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_http_client = MagicMock()
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_http_client) as mock_client_class:
            await client.get_user_preferences(42)

        # Verify timeout was passed to AsyncClient
        mock_client_class.assert_called_once_with(timeout=settings.AUTH_SERVICE_TIMEOUT)
