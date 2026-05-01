"""API endpoint routers."""

from meeting_service.api.endpoints.audit import router as audit_router
from meeting_service.api.endpoints.calendar import router as calendar_router
from meeting_service.api.endpoints.meetings import router as meetings_router
from meeting_service.api.endpoints.user_meetings import router as user_meetings_router

__all__ = [
    "audit_router",
    "calendar_router",
    "meetings_router",
    "user_meetings_router",
]
