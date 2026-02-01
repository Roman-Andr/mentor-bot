"""API routers and dependencies for the Checklists Service."""

from checklists_service.api.deps import (
    AdminUser,
    AuthToken,
    CurrentUser,
    DatabaseSession,
    HRUser,
    MentorUser,
    UserInfo,
    get_auth_token,
    get_current_active_user,
    get_current_user,
    require_admin,
    require_hr,
    require_mentor_or_above,
)
from checklists_service.api.endpoints import checklists, tasks, templates

__all__ = [
    "AdminUser",
    "AuthToken",
    "CurrentUser",
    "DatabaseSession",
    "HRUser",
    "MentorUser",
    "UserInfo",
    "auth",
    "checklists",
    "get_auth_token",
    "get_current_active_user",
    "get_current_user",
    "require_admin",
    "require_hr",
    "require_mentor_or_above",
    "tasks",
    "templates",
]
