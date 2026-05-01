"""SQLAlchemy implementation of Invitation status history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import InvitationStatusHistory
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.invitation_status_history import IInvitationStatusHistoryRepository


class InvitationStatusHistoryRepository(
    SqlAlchemyBaseRepository[InvitationStatusHistory, int], IInvitationStatusHistoryRepository
):
    """SQLAlchemy implementation of Invitation status history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize InvitationStatusHistoryRepository with database session."""
        super().__init__(session, InvitationStatusHistory)

    async def create(self, entity: InvitationStatusHistory) -> InvitationStatusHistory:
        """Create invitation status history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_invitation_id(
        self,
        invitation_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[InvitationStatusHistory]:
        """Get invitation status history for an invitation with optional date filtering."""
        stmt = select(InvitationStatusHistory).where(InvitationStatusHistory.invitation_id == invitation_id)

        if from_date:
            stmt = stmt.where(InvitationStatusHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(InvitationStatusHistory.changed_at <= to_date)

        stmt = stmt.order_by(InvitationStatusHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[InvitationStatusHistory], int]:
        """Get all invitation status history with filtering and pagination."""
        count_stmt = select(func.count(InvitationStatusHistory.id))
        stmt = select(InvitationStatusHistory)

        if from_date:
            stmt = stmt.where(InvitationStatusHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(InvitationStatusHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(InvitationStatusHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(InvitationStatusHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(InvitationStatusHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
