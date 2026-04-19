"""API routers and dependencies for the Notification Service."""

from notification_service.api import templates
from notification_service.api.deps import (
    AdminUser,
    CurrentUser,
    DatabaseSession,
    HRUser,
    UserInfo,
    get_current_active_user,
    get_current_user,
)
from notification_service.api.endpoints import email, notifications

__all__ = [
    "AdminUser",
    "CurrentUser",
    "DatabaseSession",
    "HRUser",
    "UserInfo",
    "email",
    "get_current_active_user",
    "get_current_user",
    "notifications",
    "templates",
]
