"""Authentication middleware for HTTP requests."""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from notification_service.config import settings


class AuthTokenMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and store auth token from requests."""

    def __init__(self, app: ASGIApp) -> None:
        """Initialize middleware with ASGI application."""
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request to extract auth token."""
        auth_header = request.headers.get("Authorization")
        token = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

        request.state.auth_token = token

        return await call_next(request)


def verify_service_api_key(api_key: str) -> bool:
    """Verify that the provided API key is valid for service-to-service communication.

    Args:
        api_key: The API key to verify

    Returns:
        True if the API key is valid, False otherwise
    """
    # In development mode with no key configured, accept any non-empty key
    if settings.DEBUG and not settings.SERVICE_API_KEY:
        return bool(api_key)

    return api_key == settings.SERVICE_API_KEY
