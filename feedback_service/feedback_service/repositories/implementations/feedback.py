"""SQLAlchemy implementations of feedback repositories."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from feedback_service.models import Comment, ExperienceRating, PulseSurvey
from feedback_service.repositories.implementations.base import SqlAlchemyBaseRepository
from feedback_service.repositories.interfaces import (
    ICommentRepository,
    IExperienceRatingRepository,
    IPulseSurveyRepository,
)


class PulseSurveyRepository(SqlAlchemyBaseRepository[PulseSurvey, int], IPulseSurveyRepository):
    """SQLAlchemy implementation of PulseSurvey repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize PulseSurveyRepository with database session."""
        super().__init__(session, PulseSurvey)

    async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[PulseSurvey]:
        """Find pulse surveys by user ID."""
        stmt = (
            select(PulseSurvey)
            .where(PulseSurvey.user_id == user_id)
            .order_by(PulseSurvey.submitted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()


class ExperienceRatingRepository(SqlAlchemyBaseRepository[ExperienceRating, int], IExperienceRatingRepository):
    """SQLAlchemy implementation of ExperienceRating repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ExperienceRatingRepository with database session."""
        super().__init__(session, ExperienceRating)

    async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[ExperienceRating]:
        """Find experience ratings by user ID."""
        stmt = (
            select(ExperienceRating)
            .where(ExperienceRating.user_id == user_id)
            .order_by(ExperienceRating.submitted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()


class CommentRepository(SqlAlchemyBaseRepository[Comment, int], ICommentRepository):
    """SQLAlchemy implementation of Comment repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize CommentRepository with database session."""
        super().__init__(session, Comment)

    async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Comment]:
        """Find comments by user ID."""
        stmt = (
            select(Comment)
            .where(Comment.user_id == user_id)
            .order_by(Comment.submitted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
