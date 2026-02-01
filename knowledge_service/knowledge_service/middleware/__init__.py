"""Middleware components."""

from knowledge_service.middleware.auth import AuthTokenMiddleware

__all__ = [
    "AuthTokenMiddleware",
]
