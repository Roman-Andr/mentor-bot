"""API endpoint routers."""

from auth_service.api.endpoints.auth import router as auth_router
from auth_service.api.endpoints.departments import router as departments_router
from auth_service.api.endpoints.invitations import router as invitations_router
from auth_service.api.endpoints.user_mentors import router as user_mentors_router
from auth_service.api.endpoints.users import router as users_router

__all__ = [
    "auth_router",
    "departments_router",
    "invitations_router",
    "user_mentors_router",
    "users_router",
]
