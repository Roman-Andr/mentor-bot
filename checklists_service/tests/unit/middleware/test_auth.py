"""Tests for auth middleware."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from checklists_service.middleware.auth import AuthTokenMiddleware
from fastapi import Request
from starlette.datastructures import Headers
from starlette.responses import Response


class TestAuthTokenMiddleware:
    """Test AuthTokenMiddleware."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock ASGI app."""
        return MagicMock()

    @pytest.fixture
    def middleware(self, mock_app):
        """Create middleware instance."""
        return AuthTokenMiddleware(mock_app)

    @pytest.fixture
    def mock_request(self):
        """Create a mock request."""
        request = MagicMock(spec=Request)
        request.headers = Headers()
        request.state = MagicMock()
        return request

    async def test_dispatch_no_auth_header(self, middleware):
        """Test dispatch with no auth header sets token to None."""
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        await middleware.dispatch(mock_request, mock_call_next)

        assert mock_request.state.auth_token is None
        mock_call_next.assert_awaited_once()

    async def test_dispatch_with_bearer_token(self, middleware):
        """Test dispatch extracts bearer token correctly."""
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test-token-123"}
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        await middleware.dispatch(mock_request, mock_call_next)

        assert mock_request.state.auth_token == "test-token-123"
        mock_call_next.assert_awaited_once()

    async def test_dispatch_with_invalid_auth_header(self, middleware):
        """Test dispatch with non-bearer auth header sets token to None."""
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Basic dXNlcjpwYXNz"}
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        await middleware.dispatch(mock_request, mock_call_next)

        # Basic auth doesn't start with "Bearer " so token should be None
        assert mock_request.state.auth_token is None
        mock_call_next.assert_awaited_once()

    async def test_dispatch_with_empty_bearer(self, middleware):
        """Test dispatch with 'Bearer ' but no token."""
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer "}
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=MagicMock(spec=Response))

        await middleware.dispatch(mock_request, mock_call_next)

        # Empty token after "Bearer "
        assert mock_request.state.auth_token == ""
        mock_call_next.assert_awaited_once()

    async def test_middleware_initialization(self, mock_app):
        """Test middleware initializes properly."""
        middleware = AuthTokenMiddleware(mock_app)

        assert middleware.app is mock_app

    async def test_dispatch_returns_response(self, middleware):
        """Test dispatch returns response from call_next."""
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.state = MagicMock()

        expected_response = MagicMock(spec=Response)
        mock_call_next = AsyncMock(return_value=expected_response)

        result = await middleware.dispatch(mock_request, mock_call_next)

        assert result is expected_response
