"""Middleware components."""

from notification_service.middleware.auth import AuthTokenMiddleware

__all__ = [
    "AuthTokenMiddleware",
]
