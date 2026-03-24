"""Middleware components."""

from checklists_service.middleware.auth import AuthTokenMiddleware

__all__ = [
    "AuthTokenMiddleware",
]
