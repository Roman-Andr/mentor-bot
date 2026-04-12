"""API endpoint routers."""

from meeting_service.api.endpoints.calendar import router as calendar_router
from meeting_service.api.endpoints.departments import router as departments_router
from meeting_service.api.endpoints.meetings import router as meetings_router
from meeting_service.api.endpoints.user_meetings import router as user_meetings_router

__all__ = [
    "calendar_router",
    "departments_router",
    "meetings_router",
    "user_meetings_router",
]
