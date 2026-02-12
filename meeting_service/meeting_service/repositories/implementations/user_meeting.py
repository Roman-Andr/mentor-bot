"""SQLAlchemy implementation of UserMeeting repository."""

from collections.abc import Sequence
from typing import cast

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.core.enums import MeetingStatus
from meeting_service.models import UserMeeting
from meeting_service.repositories.implementations.base import SqlAlchemyBaseRepository
from meeting_service.repositories.interfaces.user_meeting import IUserMeetingRepository


class UserMeetingRepository(SqlAlchemyBaseRepository[UserMeeting, int], IUserMeetingRepository):
    """SQLAlchemy implementation of UserMeeting repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize UserMeetingRepository with database session."""
        super().__init__(session, UserMeeting)

    async def find_by_user(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        status: MeetingStatus | None = None,
    ) -> tuple[Sequence[UserMeeting], int]:
        """Find meetings assigned to a user with optional status filter."""
        count_stmt = select(func.count(UserMeeting.id)).where(UserMeeting.user_id == user_id)
        stmt = select(UserMeeting).where(UserMeeting.user_id == user_id)

        if status:
            stmt = stmt.where(UserMeeting.status == status)
            count_stmt = count_stmt.where(UserMeeting.status == status)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(UserMeeting.scheduled_at, UserMeeting.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        items = result.scalars().all()

        return items, total

    async def find_by_meeting(self, meeting_id: int) -> Sequence[UserMeeting]:
        """Find all assignments for a specific meeting template."""
        stmt = select(UserMeeting).where(UserMeeting.meeting_id == meeting_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_user_meeting(self, user_id: int, meeting_id: int) -> UserMeeting | None:
        """Get specific assignment of a meeting to a user."""
        stmt = select(UserMeeting).where(
            and_(
                UserMeeting.user_id == user_id,
                UserMeeting.meeting_id == meeting_id,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
