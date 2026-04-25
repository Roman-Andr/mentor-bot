"""Authentication middleware for HTTP requests."""

from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


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
        logger.debug(
            "Auth token extracted from request (has_token={}, path={})",
            token is not None,
            request.url.path,
        )

        return await call_next(request)
