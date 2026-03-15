"""SQLAlchemy implementation of Meeting repository."""

from collections.abc import Sequence
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.core.enums import EmployeeLevel, MeetingType
from meeting_service.models import Meeting
from meeting_service.repositories.implementations.base import SqlAlchemyBaseRepository
from meeting_service.repositories.interfaces.meeting import IMeetingRepository


class MeetingRepository(SqlAlchemyBaseRepository[Meeting, int], IMeetingRepository):
    """SQLAlchemy implementation of Meeting repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize MeetingRepository with database session."""
        super().__init__(session, Meeting)

    async def find_meetings(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        meeting_type: MeetingType | None = None,
        department: str | None = None,
        position: str | None = None,
        level: EmployeeLevel | None = None,
        is_mandatory: bool | None = None,
    ) -> tuple[Sequence[Meeting], int]:
        """Find meetings with filtering and return results with total count."""
        count_stmt = select(func.count(Meeting.id))
        stmt = select(Meeting)

        if meeting_type:
            stmt = stmt.where(Meeting.type == meeting_type)
            count_stmt = count_stmt.where(Meeting.type == meeting_type)
        if department:
            stmt = stmt.where(Meeting.department == department)
            count_stmt = count_stmt.where(Meeting.department == department)
        if position:
            stmt = stmt.where(Meeting.position == position)
            count_stmt = count_stmt.where(Meeting.position == position)
        if level:
            stmt = stmt.where(Meeting.level == level)
            count_stmt = count_stmt.where(Meeting.level == level)
        if is_mandatory is not None:
            stmt = stmt.where(Meeting.is_mandatory == is_mandatory)
            count_stmt = count_stmt.where(Meeting.is_mandatory == is_mandatory)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(Meeting.order, Meeting.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        meetings = result.scalars().all()

        return meetings, total
