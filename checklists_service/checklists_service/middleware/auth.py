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
            logger.debug("Auth token extracted from header (path={})", request.url.path)
        else:
            logger.debug("No bearer auth token in request (path={})", request.url.path)

        request.state.auth_token = token

        return await call_next(request)
