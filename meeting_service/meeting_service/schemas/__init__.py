"""Pydantic schemas for request/response validation."""

from meeting_service.schemas.material import (
    MaterialBase,
    MaterialCreate,
    MaterialResponse,
)
from meeting_service.schemas.meeting import (
    MeetingBase,
    MeetingCreate,
    MeetingListResponse,
    MeetingResponse,
    MeetingUpdate,
)
from meeting_service.schemas.responses import (
    HealthCheck,
    MessageResponse,
    ServiceStatus,
)
from meeting_service.schemas.user_meeting import (
    UserMeetingBase,
    UserMeetingComplete,
    UserMeetingCreate,
    UserMeetingListResponse,
    UserMeetingResponse,
    UserMeetingUpdate,
)

__all__ = [
    "HealthCheck",
    "MaterialBase",
    "MaterialCreate",
    "MaterialResponse",
    "MeetingBase",
    "MeetingCreate",
    "MeetingListResponse",
    "MeetingResponse",
    "MeetingUpdate",
    "MessageResponse",
    "ServiceStatus",
    "UserMeetingBase",
    "UserMeetingComplete",
    "UserMeetingCreate",
    "UserMeetingListResponse",
    "UserMeetingResponse",
    "UserMeetingUpdate",
]
