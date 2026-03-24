"""User-Mentor repository interface."""

from abc import abstractmethod
from collections.abc import Sequence

from auth_service.models import UserMentor
from auth_service.repositories.interfaces.base import BaseRepository


class IUserMentorRepository(BaseRepository["UserMentor", int]):
    """User-Mentor repository interface."""

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Sequence[UserMentor]:
        """Get all mentor relations for a user."""

    @abstractmethod
    async def get_by_mentor_id(self, mentor_id: int) -> Sequence[UserMentor]:
        """Get all mentee relations for a mentor."""

    @abstractmethod
    async def get_active_by_user_id(self, user_id: int) -> UserMentor | None:
        """Get active mentor relation for a user."""

    @abstractmethod
    async def get_by_user_and_mentor(self, user_id: int, mentor_id: int) -> UserMentor | None:
        """Get relation by user and mentor IDs."""
