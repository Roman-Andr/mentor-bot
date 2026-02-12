"""API endpoint routers."""

from notification_service.api.endpoints.notifications import router as notifications_router

__all__ = [
    "notifications_router",
]
