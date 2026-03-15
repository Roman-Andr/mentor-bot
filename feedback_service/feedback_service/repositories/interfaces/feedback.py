"""Feedback repository interfaces."""

from abc import abstractmethod
from collections.abc import Sequence

from feedback_service.models import Comment, ExperienceRating, PulseSurvey

from .base import BaseRepository


class IPulseSurveyRepository(BaseRepository[PulseSurvey, int]):
    """Interface for PulseSurvey repository."""

    @abstractmethod
    async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[PulseSurvey]:
        """Find pulse surveys by user ID."""
        raise NotImplementedError


class IExperienceRatingRepository(BaseRepository[ExperienceRating, int]):
    """Interface for ExperienceRating repository."""

    @abstractmethod
    async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[ExperienceRating]:
        """Find experience ratings by user ID."""
        raise NotImplementedError


class ICommentRepository(BaseRepository[Comment, int]):
    """Interface for Comment repository."""

    @abstractmethod
    async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Comment]:
        """Find comments by user ID."""
        raise NotImplementedError
