"""Feedback repository interfaces."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from feedback_service.models import Comment, ExperienceRating, PulseSurvey

from .base import BaseRepository


class IPulseSurveyRepository(BaseRepository[PulseSurvey, int]):
    """Interface for PulseSurvey repository."""

    @abstractmethod
    async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[PulseSurvey]:
        """Find pulse surveys by user ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_user(
        self,
        user_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
        skip: int,
        limit: int,
    ) -> tuple[Sequence[PulseSurvey], int]:
        """Get pulse surveys with optional user filter and date range."""
        raise NotImplementedError

    @abstractmethod
    async def get_stats(
        self,
        user_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> dict:
        """Get aggregate statistics for pulse surveys."""
        raise NotImplementedError

    @abstractmethod
    async def get_rating_distribution(
        self,
        user_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> dict[int, int]:
        """Get count of each rating (1-10)."""
        raise NotImplementedError

    @abstractmethod
    async def get_anonymity_stats(
        self,
        department_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> dict:
        """Get stats for anonymous vs attributed feedback."""
        raise NotImplementedError


class IExperienceRatingRepository(BaseRepository[ExperienceRating, int]):
    """Interface for ExperienceRating repository."""

    @abstractmethod
    async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[ExperienceRating]:
        """Find experience ratings by user ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_user(
        self,
        user_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
        min_rating: int | None,
        max_rating: int | None,
        skip: int,
        limit: int,
    ) -> tuple[Sequence[ExperienceRating], int]:
        """Get experience ratings with optional filters."""
        raise NotImplementedError

    @abstractmethod
    async def get_stats(
        self,
        user_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> dict:
        """Get aggregate statistics for experience ratings."""
        raise NotImplementedError

    @abstractmethod
    async def get_rating_distribution(
        self,
        user_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> dict[int, int]:
        """Get count of each rating (1-5)."""
        raise NotImplementedError

    @abstractmethod
    async def get_anonymity_stats(
        self,
        department_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> dict:
        """Get stats for anonymous vs attributed feedback."""
        raise NotImplementedError


class ICommentRepository(BaseRepository[Comment, int]):
    """Interface for Comment repository."""

    @abstractmethod
    async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Comment]:
        """Find comments by user ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_user(
        self,
        user_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
        search: str | None,
        has_reply: bool | None,
        skip: int,
        limit: int,
    ) -> tuple[Sequence[Comment], int]:
        """Get comments with optional filters."""
        raise NotImplementedError

    @abstractmethod
    async def add_reply(
        self,
        comment_id: int,
        reply: str,
        replied_by: int,
    ) -> Comment | None:
        """Add a reply to a comment."""
        raise NotImplementedError

    @abstractmethod
    async def get_anonymity_stats(
        self,
        department_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> dict:
        """Get stats for anonymous vs attributed comments."""
        raise NotImplementedError

    @abstractmethod
    async def get_reply_eligible_comments(
        self,
        department_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
        skip: int,
        limit: int,
    ) -> tuple[Sequence[Comment], int]:
        """Get comments that can be replied to (non-anonymous or anonymous with contact)."""
        raise NotImplementedError
