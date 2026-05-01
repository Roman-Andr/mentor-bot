"""Feedback status change history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from feedback_service.models import FeedbackStatusChangeHistory
from feedback_service.repositories.interfaces.base import BaseRepository


class IFeedbackStatusChangeHistoryRepository(BaseRepository["FeedbackStatusChangeHistory", int]):
    """Feedback status change history repository interface."""

    @abstractmethod
    async def create(self, entity: FeedbackStatusChangeHistory) -> FeedbackStatusChangeHistory:
        """Create feedback status change history entry."""

    @abstractmethod
    async def get_by_feedback_id(
        self,
        feedback_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[FeedbackStatusChangeHistory]:
        """Get feedback status change history for a feedback with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[FeedbackStatusChangeHistory], int]:
        """Get all feedback status change history with filtering and pagination."""
