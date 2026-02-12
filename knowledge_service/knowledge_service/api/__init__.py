"""API routers and dependencies for the Knowledge Service."""

from knowledge_service.api.deps import (
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
from knowledge_service.api.endpoints import articles, attachments, categories, search, tags

__all__ = [
    "AdminUser",
    "AuthToken",
    "CurrentUser",
    "DatabaseSession",
    "HRUser",
    "MentorUser",
    "UserInfo",
    "articles",
    "attachments",
    "categories",
    "get_auth_token",
    "get_current_active_user",
    "get_current_user",
    "require_admin",
    "require_hr",
    "require_mentor_or_above",
    "search",
    "tags",
]
