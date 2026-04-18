"""SQLAlchemy implementations of feedback repositories."""

from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from feedback_service.models import Comment, ExperienceRating, PulseSurvey
from feedback_service.repositories.implementations.base import DateFilterMixin, SqlAlchemyBaseRepository
from feedback_service.repositories.interfaces import (
    ICommentRepository,
    IExperienceRatingRepository,
    IPulseSurveyRepository,
)


class PulseSurveyRepository(DateFilterMixin, SqlAlchemyBaseRepository[PulseSurvey, int], IPulseSurveyRepository):
    """SQLAlchemy implementation of PulseSurvey repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize PulseSurveyRepository with database session."""
        super().__init__(session, PulseSurvey)

    async def find_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[PulseSurvey]:
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

    async def get_by_user(
        self,
        user_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[PulseSurvey], int]:
        """Get pulse surveys with optional user filter and date range."""
        query = select(PulseSurvey)

        if user_id is not None:
            query = query.where(PulseSurvey.user_id == user_id)

        query = self._apply_date_filters(query, PulseSurvey, from_date, to_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(PulseSurvey.submitted_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self._session.execute(query)

        return result.scalars().all(), total

    async def get_stats(
        self,
        user_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict:
        """Get aggregate statistics for pulse surveys."""
        query = select(
            func.avg(PulseSurvey.rating).label("avg_rating"),
            func.count().label("total"),
            func.min(PulseSurvey.rating).label("min_rating"),
            func.max(PulseSurvey.rating).label("max_rating"),
        )

        if user_id is not None:
            query = query.where(PulseSurvey.user_id == user_id)

        query = self._apply_date_filters(query, PulseSurvey, from_date, to_date)

        result = await self._session.execute(query)
        row = result.one()

        return {
            "average_rating": round(row.avg_rating, 2) if row.avg_rating else None,
            "total_responses": row.total,
            "min_rating": row.min_rating,
            "max_rating": row.max_rating,
        }

    async def get_rating_distribution(
        self,
        user_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict[int, int]:
        """Get count of each rating (1-10)."""
        query = select(
            PulseSurvey.rating,
            func.count().label("cnt"),
        ).group_by(PulseSurvey.rating)

        if user_id is not None:
            query = query.where(PulseSurvey.user_id == user_id)

        query = self._apply_date_filters(query, PulseSurvey, from_date, to_date)

        result = await self._session.execute(query)
        return {row.rating: row.cnt for row in result.all()}

    async def get_anonymity_stats(
        self,
        department_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict:
        """Get stats for anonymous vs attributed feedback."""
        query = select(
            PulseSurvey.is_anonymous,
            func.avg(PulseSurvey.rating).label("avg_rating"),
            func.count().label("cnt"),
        ).group_by(PulseSurvey.is_anonymous)

        if department_id:
            query = query.where(PulseSurvey.department_id == department_id)

        query = self._apply_date_filters(query, PulseSurvey, from_date, to_date)

        result = await self._session.execute(query)

        stats: dict = {"anonymous": {"average_rating": None, "count": 0}, "attributed": {"average_rating": None, "count": 0}}
        for row in result.all():
            key = "anonymous" if row.is_anonymous else "attributed"
            stats[key] = {
                "average_rating": round(row.avg_rating, 2) if row.avg_rating else None,
                "count": row.cnt,
            }

        return stats


class ExperienceRatingRepository(DateFilterMixin, SqlAlchemyBaseRepository[ExperienceRating, int], IExperienceRatingRepository):
    """SQLAlchemy implementation of ExperienceRating repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ExperienceRatingRepository with database session."""
        super().__init__(session, ExperienceRating)

    async def find_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ExperienceRating]:
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

    async def get_by_user(
        self,
        user_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        min_rating: int | None = None,
        max_rating: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[ExperienceRating], int]:
        """Get experience ratings with optional filters."""
        query = select(ExperienceRating)

        if user_id is not None:
            query = query.where(ExperienceRating.user_id == user_id)
        if min_rating is not None:
            query = query.where(ExperienceRating.rating >= min_rating)
        if max_rating is not None:
            query = query.where(ExperienceRating.rating <= max_rating)

        query = self._apply_date_filters(query, ExperienceRating, from_date, to_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(ExperienceRating.submitted_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self._session.execute(query)

        return result.scalars().all(), total

    async def get_stats(
        self,
        user_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict:
        """Get aggregate statistics for experience ratings."""
        query = select(
            func.avg(ExperienceRating.rating).label("avg_rating"),
            func.count().label("total"),
            func.min(ExperienceRating.rating).label("min_rating"),
            func.max(ExperienceRating.rating).label("max_rating"),
        )

        if user_id is not None:
            query = query.where(ExperienceRating.user_id == user_id)

        query = self._apply_date_filters(query, ExperienceRating, from_date, to_date)

        result = await self._session.execute(query)
        row = result.one()

        return {
            "average_rating": round(row.avg_rating, 2) if row.avg_rating else None,
            "total_ratings": row.total,
            "min_rating": row.min_rating,
            "max_rating": row.max_rating,
        }

    async def get_rating_distribution(
        self,
        user_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict[int, int]:
        """Get count of each rating (1-5)."""
        query = select(
            ExperienceRating.rating,
            func.count().label("cnt"),
        ).group_by(ExperienceRating.rating)

        if user_id is not None:
            query = query.where(ExperienceRating.user_id == user_id)

        query = self._apply_date_filters(query, ExperienceRating, from_date, to_date)

        result = await self._session.execute(query)
        return {row.rating: row.cnt for row in result.all()}

    async def get_anonymity_stats(
        self,
        department_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict:
        """Get stats for anonymous vs attributed feedback."""
        query = select(
            ExperienceRating.is_anonymous,
            func.avg(ExperienceRating.rating).label("avg_rating"),
            func.count().label("cnt"),
        ).group_by(ExperienceRating.is_anonymous)

        if department_id:
            query = query.where(ExperienceRating.department_id == department_id)

        query = self._apply_date_filters(query, ExperienceRating, from_date, to_date)

        result = await self._session.execute(query)

        stats = {"anonymous": {"average_rating": None, "count": 0}, "attributed": {"average_rating": None, "count": 0}}
        for row in result.all():
            key = "anonymous" if row.is_anonymous else "attributed"
            stats[key] = {
                "average_rating": round(row.avg_rating, 2) if row.avg_rating else None,
                "count": row.cnt,
            }

        return stats


class CommentRepository(DateFilterMixin, SqlAlchemyBaseRepository[Comment, int], ICommentRepository):
    """SQLAlchemy implementation of Comment repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize CommentRepository with database session."""
        super().__init__(session, Comment)

    async def find_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Comment]:
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

    @staticmethod
    def _escape_ilike_pattern(pattern: str) -> str:
        """Escape special characters for PostgreSQL ILIKE to prevent SQL injection."""
        return pattern.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    async def get_by_user(
        self,
        user_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        search: str | None = None,
        has_reply: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Comment], int]:
        """Get comments with optional filters."""
        query = select(Comment)

        if user_id is not None:
            query = query.where(Comment.user_id == user_id)
        if search:
            escaped_search = self._escape_ilike_pattern(search)
            query = query.where(Comment.comment.ilike(f"%{escaped_search}%", escape="\\"))
        if has_reply is not None:
            query = query.where(Comment.reply.isnot(None) if has_reply else Comment.reply.is_(None))

        query = self._apply_date_filters(query, Comment, from_date, to_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(Comment.submitted_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self._session.execute(query)

        return result.scalars().all(), total

    async def add_reply(
        self,
        comment_id: int,
        reply: str,
        replied_by: int,
    ) -> Comment | None:
        """Add a reply to a comment."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        comment.reply = reply
        comment.replied_at = datetime.now(UTC)
        comment.replied_by = replied_by

        await self._session.flush()
        await self._session.refresh(comment)
        return comment

    async def get_anonymity_stats(
        self,
        department_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict:
        """Get stats for anonymous vs attributed comments."""
        query = select(
            Comment.is_anonymous,
            func.count().label("cnt"),
        ).group_by(Comment.is_anonymous)

        if department_id:
            query = query.where(Comment.department_id == department_id)

        query = self._apply_date_filters(query, Comment, from_date, to_date)

        result = await self._session.execute(query)

        stats: dict = {"anonymous": {"count": 0, "with_contact": 0}, "attributed": {"count": 0}}
        for row in result.all():
            key = "anonymous" if row.is_anonymous else "attributed"
            stats[key]["count"] = row.cnt

        # Count anonymous comments with contact info
        contact_query = select(func.count()).where(
            Comment.is_anonymous.is_(True),
            Comment.allow_contact.is_(True),
        )
        if department_id:
            contact_query = contact_query.where(Comment.department_id == department_id)

        contact_query = self._apply_date_filters(contact_query, Comment, from_date, to_date)

        contact_result = await self._session.execute(contact_query)
        stats["anonymous"]["with_contact"] = contact_result.scalar() or 0

        return stats

    async def get_reply_eligible_comments(
        self,
        department_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Comment], int]:
        """Get comments that can be replied to (non-anonymous or anonymous with contact)."""
        query = select(Comment).where(
            (Comment.is_anonymous.is_(False)) |
            (Comment.allow_contact.is_(True))
        )

        if department_id:
            query = query.where(Comment.department_id == department_id)

        query = self._apply_date_filters(query, Comment, from_date, to_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(Comment.submitted_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self._session.execute(query)

        return result.scalars().all(), total
