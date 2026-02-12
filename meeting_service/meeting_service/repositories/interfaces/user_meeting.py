"""UserMeeting repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

from meeting_service.core.enums import MeetingStatus
from meeting_service.repositories.interfaces.base import BaseRepository

if TYPE_CHECKING:
    from meeting_service.models import UserMeeting


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
    ) -> tuple[Sequence["UserMeeting"], int]:
        """Find meetings assigned to a user with optional status filter."""

    @abstractmethod
    async def find_by_meeting(self, meeting_id: int) -> Sequence["UserMeeting"]:
        """Find all assignments for a specific meeting template."""

    @abstractmethod
    async def get_user_meeting(self, user_id: int, meeting_id: int) -> "UserMeeting | None":
        """Get specific assignment of a meeting to a user."""
