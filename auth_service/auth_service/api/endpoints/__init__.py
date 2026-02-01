"""API endpoint routers."""

from auth_service.api.endpoints.auth import router as auth_router
from auth_service.api.endpoints.invitations import router as invitations_router
from auth_service.api.endpoints.users import router as users_router

__all__ = [
    "auth_router",
    "invitations_router",
    "users_router",
]
