"""API routers and dependencies for the Escalation Service."""

from escalation_service.api.deps import (
    AdminUser,
    CurrentUser,
    DatabaseSession,
    HRUser,
    UserInfo,
    get_current_active_user,
    get_current_user,
)
from escalation_service.api.endpoints import escalations_router

__all__ = [
    "AdminUser",
    "CurrentUser",
    "DatabaseSession",
    "HRUser",
    "UserInfo",
    "escalations_router",
    "get_current_active_user",
    "get_current_user",
]
