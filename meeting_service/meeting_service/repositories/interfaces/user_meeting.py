"""UserMeeting repository interface."""

from abc import abstractmethod
from collections.abc import Sequence

from meeting_service.core.enums import MeetingStatus
from meeting_service.models import UserMeeting
from meeting_service.repositories.interfaces.base import BaseRepository


class IUserMeetingRepository(BaseRepository["UserMeeting", int]):
    """UserMeeting repository interface."""

    @abstractmethod
    async def find_by_user(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        status: MeetingStatus | None = None,
    ) -> tuple[Sequence[UserMeeting], int]:
        """Find meetings assigned to a user with optional status filter."""

    @abstractmethod
    async def find_by_meeting(
        self,
        meeting_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        status: MeetingStatus | None = None,
    ) -> tuple[Sequence[UserMeeting], int]:
        """Find all assignments for a specific meeting template with pagination."""

    @abstractmethod
    async def get_user_meeting(self, user_id: int, meeting_id: int) -> UserMeeting | None:
        """Get specific assignment of a meeting to a user."""
