"""API endpoint routers."""

from notification_service.api.endpoints.audit import router as audit_router
from notification_service.api.endpoints.notifications import router as notifications_router

__all__ = [
    "audit_router",
    "notifications_router",
]
