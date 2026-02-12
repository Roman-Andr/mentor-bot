"""MeetingMaterial repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

from meeting_service.repositories.interfaces.base import BaseRepository

if TYPE_CHECKING:
    from meeting_service.models import MeetingMaterial


class IMaterialRepository(BaseRepository["MeetingMaterial", int]):
    """MeetingMaterial repository interface."""

    @abstractmethod
    async def get_by_meeting(self, meeting_id: int) -> Sequence["MeetingMaterial"]:
        """Get all materials for a specific meeting."""
