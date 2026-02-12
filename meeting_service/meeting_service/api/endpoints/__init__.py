"""API endpoint routers."""

from meeting_service.api.endpoints.meetings import router as meetings_router
from meeting_service.api.endpoints.user_meetings import router as user_meetings_router

__all__ = [
    "meetings_router",
    "user_meetings_router",
]
