"""Tests for integration utilities."""

import logging
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import status

from knowledge_service.utils.integrations import AuthServiceClient, auth_service_client

if TYPE_CHECKING:
    import pytest


class TestAuthServiceClientValidateToken:
    """Test AuthServiceClient.validate_token method."""

    async def test_validate_token_success(self) -> None:
        """validate_token returns user data on 200 OK."""
        client = AuthServiceClient(base_url="http://auth:8001")

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {"id": 1, "email": "test@example.com"}

        client.client = AsyncMock()
        client.client.get = AsyncMock(return_value=mock_response)

        # Mock the cached decorator to call the function directly
        with patch("knowledge_service.utils.integrations.cached") as mock_cached:
            mock_cached.side_effect = lambda **_kwargs: lambda f: f
            result = await client.validate_token("valid_token")

        assert result == {"id": 1, "email": "test@example.com"}

    async def test_validate_token_non_200_returns_none(self) -> None:
        """validate_token returns None for non-200 status."""
        client = AuthServiceClient(base_url="http://auth:8001")

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_401_UNAUTHORIZED

        client.client = AsyncMock()
        client.client.get = AsyncMock(return_value=mock_response)

        with patch("knowledge_service.utils.integrations.cached") as mock_cached:
            mock_cached.side_effect = lambda **_kwargs: lambda f: f
            result = await client.validate_token("invalid_token")

        assert result is None

    async def test_validate_token_request_error_logs_exception(self, caplog: pytest.LogCaptureFixture) -> None:
        """validate_token logs exception on httpx.RequestError."""
        client = AuthServiceClient(base_url="http://auth:8001")

        client.client = AsyncMock()
        client.client.get = AsyncMock(side_effect=httpx.RequestError("Connection failed"))

        with caplog.at_level(logging.ERROR):
            with patch("knowledge_service.utils.integrations.cached") as mock_cached:
                mock_cached.side_effect = lambda **_kwargs: lambda f: f
                result = await client.validate_token("token")

        assert result is None
        assert "Auth service request failed" in caplog.text

    async def test_validate_token_generic_exception_logs_exception(self, caplog: pytest.LogCaptureFixture) -> None:
        """validate_token logs exception on generic Exception."""
        client = AuthServiceClient(base_url="http://auth:8001")

        client.client = AsyncMock()
        client.client.get = AsyncMock(side_effect=ValueError("Unexpected error"))

        with caplog.at_level(logging.ERROR):
            with patch("knowledge_service.utils.integrations.cached") as mock_cached:
                mock_cached.side_effect = lambda **_kwargs: lambda f: f
                result = await client.validate_token("token")

        assert result is None
        assert "Token validation error" in caplog.text


class TestAuthServiceClientGetUser:
    """Test AuthServiceClient.get_user method."""

    async def test_get_user_success(self) -> None:
        """get_user returns user data on 200 OK."""
        client = AuthServiceClient(base_url="http://auth:8001")

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {"id": 1, "email": "user@example.com", "name": "Test User"}

        client.client = AsyncMock()
        client.client.get = AsyncMock(return_value=mock_response)

        with patch("knowledge_service.utils.integrations.cached") as mock_cached:
            mock_cached.side_effect = lambda **_kwargs: lambda f: f
            result = await client.get_user(1, "service_token")

        assert result == {"id": 1, "email": "user@example.com", "name": "Test User"}

    async def test_get_user_non_200_returns_none(self) -> None:
        """get_user returns None for non-200 status."""
        client = AuthServiceClient(base_url="http://auth:8001")

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_404_NOT_FOUND

        client.client = AsyncMock()
        client.client.get = AsyncMock(return_value=mock_response)

        with patch("knowledge_service.utils.integrations.cached") as mock_cached:
            mock_cached.side_effect = lambda **_kwargs: lambda f: f
            result = await client.get_user(999, "service_token")

        assert result is None

    async def test_get_user_request_error_logs_exception(self, caplog: pytest.LogCaptureFixture) -> None:
        """get_user logs exception on httpx.RequestError."""
        client = AuthServiceClient(base_url="http://auth:8001")

        client.client = AsyncMock()
        client.client.get = AsyncMock(side_effect=httpx.RequestError("Connection timeout"))

        with caplog.at_level(logging.ERROR):
            with patch("knowledge_service.utils.integrations.cached") as mock_cached:
                mock_cached.side_effect = lambda **_kwargs: lambda f: f
                result = await client.get_user(1, "token")

        assert result is None
        assert "Auth service request failed" in caplog.text

    async def test_get_user_generic_exception_logs_exception(self, caplog: pytest.LogCaptureFixture) -> None:
        """get_user logs exception on generic Exception."""
        client = AuthServiceClient(base_url="http://auth:8001")

        client.client = AsyncMock()
        client.client.get = AsyncMock(side_effect=RuntimeError("Unexpected error"))

        with caplog.at_level(logging.ERROR):
            with patch("knowledge_service.utils.integrations.cached") as mock_cached:
                mock_cached.side_effect = lambda **_kwargs: lambda f: f
                result = await client.get_user(1, "token")

        assert result is None
        assert "Get user error" in caplog.text


class TestAuthServiceClientInvalidateCache:
    """Test AuthServiceClient.invalidate_user_cache method."""

    async def test_invalidate_user_cache_calls_delete_pattern(self) -> None:
        """invalidate_user_cache calls cache.delete_pattern with correct pattern."""
        client = AuthServiceClient(base_url="http://auth:8001")

        mock_cache = AsyncMock()
        mock_cache.delete_pattern = AsyncMock()

        with patch("knowledge_service.utils.integrations.cache", mock_cache):
            await client.invalidate_user_cache(42)

        mock_cache.delete_pattern.assert_called_once_with("auth_user:*42*")


class TestAuthServiceClientInitialization:
    """Test AuthServiceClient initialization."""

    def test_init_with_custom_base_url(self) -> None:
        """AuthServiceClient accepts custom base_url."""
        client = AuthServiceClient(base_url="http://custom:8000")
        assert client.base_url == "http://custom:8000"

    def test_init_uses_settings_default(self) -> None:
        """AuthServiceClient uses settings.AUTH_SERVICE_URL as default."""
        with patch("knowledge_service.utils.integrations.settings") as mock_settings:
            mock_settings.AUTH_SERVICE_URL = "http://auth-service:8001"
            mock_settings.AUTH_SERVICE_TIMEOUT = 30.0

            client = AuthServiceClient()
            assert client.base_url == "http://auth-service:8001"


class TestAuthServiceClientSingleton:
    """Test the singleton instance."""

    def test_singleton_instance_exists(self) -> None:
        """auth_service_client is a singleton instance."""
        assert isinstance(auth_service_client, AuthServiceClient)
