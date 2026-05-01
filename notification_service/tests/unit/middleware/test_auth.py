"""Tests for notification_service middleware/auth.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request, Response
from notification_service.middleware.auth import AuthTokenMiddleware
from starlette.testclient import TestClient


class TestAuthTokenMiddleware:
    """Tests for AuthTokenMiddleware."""

    def test_init(self):
        """Test middleware initialization."""
        mock_app = MagicMock()
        middleware = AuthTokenMiddleware(mock_app)
        assert middleware.app is mock_app

    @pytest.mark.asyncio
    async def test_dispatch_with_valid_bearer_token(self):
        """Test middleware extracts valid Bearer token."""
        app = FastAPI()
        middleware = AuthTokenMiddleware(app)

        # Create mock request and response
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer valid_token_123"}
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        # Call dispatch
        await middleware.dispatch(mock_request, mock_call_next)

        # Verify token was extracted and stored
        assert mock_request.state.auth_token == "valid_token_123"
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_with_missing_token(self):
        """Test middleware handles missing Authorization header."""
        app = FastAPI()
        middleware = AuthTokenMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}  # No Authorization header
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        await middleware.dispatch(mock_request, mock_call_next)

        # Verify token is None when no Authorization header
        assert mock_request.state.auth_token is None
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_with_empty_auth_header(self):
        """Test middleware handles empty Authorization header."""
        app = FastAPI()
        middleware = AuthTokenMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": ""}
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        await middleware.dispatch(mock_request, mock_call_next)

        assert mock_request.state.auth_token is None
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_with_non_bearer_auth(self):
        """Test middleware handles non-Bearer Authorization header."""
        app = FastAPI()
        middleware = AuthTokenMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": "Basic dXNlcjpwYXNzd29yZA=="}
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        await middleware.dispatch(mock_request, mock_call_next)

        # Should not extract token from Basic auth
        assert mock_request.state.auth_token is None
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_with_malformed_bearer(self):
        """Test middleware handles malformed Bearer token."""
        app = FastAPI()
        middleware = AuthTokenMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": "Bearertoken123"}  # No space
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        await middleware.dispatch(mock_request, mock_call_next)

        # Should not extract token without proper format
        assert mock_request.state.auth_token is None
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_with_bearer_prefix_only(self):
        """Test middleware handles Bearer without token."""
        app = FastAPI()
        middleware = AuthTokenMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer "}  # Empty token after space
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        await middleware.dispatch(mock_request, mock_call_next)

        # Should extract empty string as token (may be handled by downstream)
        assert mock_request.state.auth_token == ""
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_with_service_api_key_bypass(self):
        """
        Test middleware allows service-to-service auth to pass through.

        Service API key headers are handled differently and should
        be passed through without modification.
        """
        app = FastAPI()
        middleware = AuthTokenMiddleware(app)

        mock_request = MagicMock(spec=Request)
        # Service-to-service auth uses different header
        mock_request.headers = {
            "X-Service-Api-Key": "service_secret_key",
            "Authorization": "Bearer user_token",
        }
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        await middleware.dispatch(mock_request, mock_call_next)

        # Should still extract the Bearer token for downstream use
        assert mock_request.state.auth_token == "user_token"
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_returns_response(self):
        """Test middleware returns the response from call_next."""
        app = FastAPI()
        middleware = AuthTokenMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer token123"}
        mock_request.state = MagicMock()

        expected_response = MagicMock(spec=Response)
        mock_call_next = AsyncMock(return_value=expected_response)

        result = await middleware.dispatch(mock_request, mock_call_next)

        # Should return the response from the next handler
        assert result is expected_response


class TestVerifyServiceApiKey:
    """Tests for verify_service_api_key function."""

    def test_valid_api_key(self):
        """Accept valid API key."""
        from notification_service.middleware.auth import verify_service_api_key

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = False
            mock_settings.SERVICE_API_KEY = "secret-key-123"

            result = verify_service_api_key("secret-key-123")
            assert result is True

    def test_invalid_api_key(self):
        """Reject invalid API key."""
        from notification_service.middleware.auth import verify_service_api_key

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = False
            mock_settings.SERVICE_API_KEY = "secret-key-123"

            result = verify_service_api_key("wrong-key")
            assert result is False

    def test_debug_mode_no_key_configured_accepts_any(self):
        """In DEBUG mode with no SERVICE_API_KEY, accept any non-empty key."""
        from notification_service.middleware.auth import verify_service_api_key

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = True
            mock_settings.SERVICE_API_KEY = ""  # No key configured

            result = verify_service_api_key("any-key")
            assert result is True

    def test_debug_mode_no_key_configured_rejects_empty(self):
        """In DEBUG mode with no SERVICE_API_KEY, reject empty key."""
        from notification_service.middleware.auth import verify_service_api_key

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = True
            mock_settings.SERVICE_API_KEY = ""  # No key configured

            result = verify_service_api_key("")
            assert result is False

    def test_debug_mode_with_configured_key_requires_match(self):
        """In DEBUG mode with SERVICE_API_KEY set, still require matching key."""
        from notification_service.middleware.auth import verify_service_api_key

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = True
            mock_settings.SERVICE_API_KEY = "configured-key"

            # Should accept matching key
            result = verify_service_api_key("configured-key")
            assert result is True

            # Should reject non-matching key
            result = verify_service_api_key("wrong-key")
            assert result is False


class TestAuthTokenMiddlewareIntegration:
    """Integration tests for AuthTokenMiddleware."""

    def test_middleware_in_request_pipeline(self):
        """Test middleware is active in the request pipeline."""
        from unittest.mock import AsyncMock, patch

        # Mock init_db and scheduler to avoid real connections
        with (
            patch("notification_service.main.init_db", new_callable=AsyncMock),
            patch("notification_service.main.scheduler") as mock_scheduler,
        ):
            mock_scheduler.run = MagicMock(return_value=AsyncMock())

            from notification_service.main import app

            client = TestClient(app)

            # Make a request with Authorization header
            headers = {"Authorization": "Bearer test_token"}
            response = client.get("/health", headers=headers)

            # Request should succeed
            assert response.status_code == 200

    def test_middleware_without_auth_header(self):
        """Test middleware allows requests without Authorization header."""
        from unittest.mock import AsyncMock, patch

        with (
            patch("notification_service.main.init_db", new_callable=AsyncMock),
            patch("notification_service.main.scheduler") as mock_scheduler,
        ):
            mock_scheduler.run = MagicMock(return_value=AsyncMock())

            from notification_service.main import app

            client = TestClient(app)

            # Request without Authorization header should still work
            response = client.get("/health")

            assert response.status_code == 200
