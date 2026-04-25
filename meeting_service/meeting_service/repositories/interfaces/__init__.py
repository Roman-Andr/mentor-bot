"""Repository interfaces following Interface Segregation Principle."""

from meeting_service.repositories.interfaces.base import BaseRepository
from meeting_service.repositories.interfaces.material import IMaterialRepository
from meeting_service.repositories.interfaces.meeting import IMeetingRepository
from meeting_service.repositories.interfaces.user_meeting import IUserMeetingRepository

__all__ = [
    "BaseRepository",
    "IMaterialRepository",
    "IMeetingRepository",
    "IUserMeetingRepository",
]
