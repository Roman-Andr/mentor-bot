"""Models package for the Meeting Service."""

from meeting_service.models.material import MeetingMaterial
from meeting_service.models.meeting import Meeting
from meeting_service.models.user_meeting import UserMeeting

__all__ = [
    "Meeting",
    "MeetingMaterial",
    "UserMeeting",
]
