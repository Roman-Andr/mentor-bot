"""SQLAlchemy implementation of MeetingMaterial repository."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.models import MeetingMaterial
from meeting_service.repositories.implementations.base import SqlAlchemyBaseRepository
from meeting_service.repositories.interfaces.material import IMaterialRepository


class MaterialRepository(SqlAlchemyBaseRepository[MeetingMaterial, int], IMaterialRepository):
    """SQLAlchemy implementation of MeetingMaterial repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize MaterialRepository with database session."""
        super().__init__(session, MeetingMaterial)

    async def get_by_meeting(self, meeting_id: int) -> Sequence[MeetingMaterial]:
        """Get all materials for a specific meeting."""
        stmt = select(MeetingMaterial).where(MeetingMaterial.meeting_id == meeting_id).order_by(MeetingMaterial.order)
        result = await self._session.execute(stmt)
        return result.scalars().all()
