"""API routers and dependencies for the Meeting Service."""

from meeting_service.api.deps import (
    AdminUser,
    CurrentUser,
    DatabaseSession,
    HRUser,
    UserInfo,
    get_current_active_user,
    get_current_user,
)
from meeting_service.api.endpoints import meetings, user_meetings

__all__ = [
    "AdminUser",
    "CurrentUser",
    "DatabaseSession",
    "HRUser",
    "UserInfo",
    "get_current_active_user",
    "get_current_user",
    "meetings",
    "user_meetings",
]
