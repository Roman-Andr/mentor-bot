"""API routers and dependencies for the Auth Service with repository pattern."""

from auth_service.api.deps import (
    AdminUser,
    AuthServiceDep,
    CurrentUser,
    DepartmentServiceDep,
    HRUser,
    InvitationServiceDep,
    MentorUser,
    UOWDep,
    UserServiceDep,
    get_current_user,
)
from auth_service.api.endpoints import auth, departments, invitations, password_reset, user_mentors, users

__all__ = [
    "AdminUser",
    "AuthServiceDep",
    "CurrentUser",
    "DepartmentServiceDep",
    "HRUser",
    "InvitationServiceDep",
    "MentorUser",
    "UOWDep",
    "UserServiceDep",
    "auth",
    "departments",
    "get_current_user",
    "invitations",
    "password_reset",
    "user_mentors",
    "users",
]
