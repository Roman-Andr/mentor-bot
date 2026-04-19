"""SQLAlchemy implementation of Meeting repository."""

from collections.abc import Sequence
from typing import cast

from sqlalchemy import Column, func, or_, select
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

    def _get_sort_column(self, sort_by: str | None) -> Column:
        """Get SQLAlchemy column for sorting."""
        column_map = {
            "title": Meeting.title,
            "type": Meeting.type,
            "department": Meeting.department_id,
            "position": Meeting.position,
            "level": Meeting.level,
            "isMandatory": Meeting.is_mandatory,
            "order": Meeting.order,
            "createdAt": Meeting.created_at,
            "updatedAt": Meeting.updated_at,
        }
        return column_map.get(sort_by, Meeting.order)

    async def find_meetings(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        meeting_type: MeetingType | None = None,
        department_id: int | None = None,
        position: str | None = None,
        level: EmployeeLevel | None = None,
        is_mandatory: bool | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[Sequence[Meeting], int]:
        """Find meetings with filtering and return results with total count."""
        count_stmt = select(func.count(Meeting.id))
        stmt = select(Meeting)

        if meeting_type:
            stmt = stmt.where(Meeting.type == meeting_type)
            count_stmt = count_stmt.where(Meeting.type == meeting_type)
        if department_id is not None:
            stmt = stmt.where(Meeting.department_id == department_id)
            count_stmt = count_stmt.where(Meeting.department_id == department_id)
        if position:
            stmt = stmt.where(Meeting.position == position)
            count_stmt = count_stmt.where(Meeting.position == position)
        if level:
            stmt = stmt.where(Meeting.level == level)
            count_stmt = count_stmt.where(Meeting.level == level)
        if is_mandatory is not None:
            stmt = stmt.where(Meeting.is_mandatory == is_mandatory)
            count_stmt = count_stmt.where(Meeting.is_mandatory == is_mandatory)

        if search:
            search_filter = or_(
                Meeting.title.ilike(f"%{search}%"),
                Meeting.description.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        # Apply sorting
        sort_column = self._get_sort_column(sort_by)
        stmt = stmt.order_by(sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        meetings = result.scalars().all()

        return meetings, total
