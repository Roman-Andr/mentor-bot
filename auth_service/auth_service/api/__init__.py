"""API routers and dependencies for the Auth Service with repository pattern."""

from auth_service.api.deps import (
    AdminUser,
    AuthServiceDep,
    CurrentUser,
    HRUser,
    InvitationServiceDep,
    MentorUser,
    UOWDep,
    UserServiceDep,
    get_current_user,
)
from auth_service.api.endpoints import auth, invitations, users

__all__ = [
    "AdminUser",
    "AuthServiceDep",
    "CurrentUser",
    "HRUser",
    "InvitationServiceDep",
    "MentorUser",
    "UOWDep",
    "UserServiceDep",
    "auth",
    "get_current_user",
    "invitations",
    "users",
]
