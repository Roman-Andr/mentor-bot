"""Tests for middleware components.

Covers:
- middleware/__init__.py lines 3-5 (AuthTokenMiddleware import)
- middleware/auth.py lines 3-27 (AuthTokenMiddleware class)
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from knowledge_service.middleware import AuthTokenMiddleware
from knowledge_service.middleware.auth import AuthTokenMiddleware as AuthMiddlewareClass


class TestMiddlewareInit:
    """Test middleware __init__.py - covers lines 3-5."""

    def test_auth_token_middleware_import(self):
        """Test AuthTokenMiddleware can be imported from middleware package.

        This covers line 3-5 in middleware/__init__.py
        """
        from knowledge_service.middleware import AuthTokenMiddleware

        assert AuthTokenMiddleware is not None
        assert issubclass(AuthTokenMiddleware, BaseHTTPMiddleware)

    def test_all_exports(self):
        """Test __all__ exports in middleware __init__.py - covers line 5."""
        from knowledge_service.middleware import __all__

        assert "AuthTokenMiddleware" in __all__


class TestAuthTokenMiddleware:
    """Test AuthTokenMiddleware class - covers lines 3-27 in middleware/auth.py."""

    def test_middleware_initialization(self):
        """Test AuthTokenMiddleware initialization - covers lines 13-15."""
        mock_app = MagicMock(spec=FastAPI)

        middleware = AuthMiddlewareClass(mock_app)

        assert middleware.app is mock_app
        assert isinstance(middleware, BaseHTTPMiddleware)

    @pytest.mark.asyncio
    async def test_dispatch_with_bearer_token(self):
        """Test dispatch with Bearer token - covers lines 17-27."""
        mock_app = MagicMock(spec=FastAPI)
        middleware = AuthMiddlewareClass(mock_app)

        # Create mock request
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer test-token-123"}
        mock_request.state = MagicMock()

        # Create mock response
        mock_response = MagicMock(spec=Response)

        # Mock call_next
        mock_call_next = AsyncMock(return_value=mock_response)

        # Call dispatch
        result = await middleware.dispatch(mock_request, mock_call_next)

        # Verify token was extracted and stored
        assert mock_request.state.auth_token == "test-token-123"
        mock_call_next.assert_called_once_with(mock_request)
        assert result is mock_response

    @pytest.mark.asyncio
    async def test_dispatch_without_auth_header(self):
        """Test dispatch without Authorization header - covers line 19-25."""
        mock_app = MagicMock(spec=FastAPI)
        middleware = AuthMiddlewareClass(mock_app)

        # Create mock request without auth header
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.state = MagicMock()

        # Create mock response
        mock_response = MagicMock(spec=Response)

        # Mock call_next
        mock_call_next = AsyncMock(return_value=mock_response)

        # Call dispatch
        result = await middleware.dispatch(mock_request, mock_call_next)

        # Verify token is None when no auth header
        assert mock_request.state.auth_token is None
        mock_call_next.assert_called_once_with(mock_request)
        assert result is mock_response

    @pytest.mark.asyncio
    async def test_dispatch_with_non_bearer_auth(self):
        """Test dispatch with non-Bearer Authorization header."""
        mock_app = MagicMock(spec=FastAPI)
        middleware = AuthMiddlewareClass(mock_app)

        # Create mock request with Basic auth
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": "Basic dXNlcjpwYXNz"}
        mock_request.state = MagicMock()

        # Create mock response
        mock_response = MagicMock(spec=Response)

        # Mock call_next
        mock_call_next = AsyncMock(return_value=mock_response)

        # Call dispatch
        result = await middleware.dispatch(mock_request, mock_call_next)

        # Verify token is None for non-Bearer auth
        assert mock_request.state.auth_token is None
        mock_call_next.assert_called_once_with(mock_request)
        assert result is mock_response

    @pytest.mark.asyncio
    async def test_dispatch_with_empty_bearer_token(self):
        """Test dispatch with empty Bearer token."""
        mock_app = MagicMock(spec=FastAPI)
        middleware = AuthMiddlewareClass(mock_app)

        # Create mock request with empty Bearer token
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer "}
        mock_request.state = MagicMock()

        # Create mock response
        mock_response = MagicMock(spec=Response)

        # Mock call_next
        mock_call_next = AsyncMock(return_value=mock_response)

        # Call dispatch
        result = await middleware.dispatch(mock_request, mock_call_next)

        # Verify empty token is stored
        assert mock_request.state.auth_token == ""
        mock_call_next.assert_called_once_with(mock_request)
        assert result is mock_response
