"""API routers and dependencies for the Checklists Service."""

from checklists_service.api.deps import (
    AdminUser,
    AuthToken,
    CurrentUser,
    HRUser,
    MentorUser,
    UOWDep,
    UserInfo,
    get_auth_token,
    get_current_active_user,
    get_current_user,
    get_uow,
    require_admin,
    require_hr,
    require_mentor_or_above,
)
from checklists_service.api.endpoints import audit, certificates, checklists, tasks, templates

__all__ = [
    "AdminUser",
    "AuthToken",
    "CurrentUser",
    "HRUser",
    "MentorUser",
    "UOWDep",
    "UserInfo",
    "audit",
    "certificates",
    "checklists",
    "get_auth_token",
    "get_current_active_user",
    "get_current_user",
    "get_uow",
    "require_admin",
    "require_hr",
    "require_mentor_or_above",
    "tasks",
    "templates",
]
