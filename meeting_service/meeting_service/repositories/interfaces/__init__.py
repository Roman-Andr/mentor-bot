"""Repository interfaces following Interface Segregation Principle."""

from meeting_service.repositories.interfaces.base import BaseRepository
from meeting_service.repositories.interfaces.material import IMaterialRepository
from meeting_service.repositories.interfaces.meeting import IMeetingRepository
from meeting_service.repositories.interfaces.meeting_participant_history import IMeetingParticipantHistoryRepository
from meeting_service.repositories.interfaces.meeting_status_change_history import IMeetingStatusChangeHistoryRepository
from meeting_service.repositories.interfaces.user_meeting import IUserMeetingRepository

__all__ = [
    "BaseRepository",
    "IMaterialRepository",
    "IMeetingParticipantHistoryRepository",
    "IMeetingRepository",
    "IMeetingStatusChangeHistoryRepository",
    "IUserMeetingRepository",
]
