"""SQLAlchemy implementation of Escalation status history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from escalation_service.models import EscalationStatusHistory
from escalation_service.repositories.implementations.base import SqlAlchemyBaseRepository
from escalation_service.repositories.interfaces.escalation_status_history import IEscalationStatusHistoryRepository


class EscalationStatusHistoryRepository(
    SqlAlchemyBaseRepository[EscalationStatusHistory, int], IEscalationStatusHistoryRepository
):
    """SQLAlchemy implementation of Escalation status history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize EscalationStatusHistoryRepository with database session."""
        super().__init__(session, EscalationStatusHistory)

    async def create(self, entity: EscalationStatusHistory) -> EscalationStatusHistory:
        """Create escalation status history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_escalation_id(
        self,
        escalation_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[EscalationStatusHistory]:
        """Get escalation status history for an escalation with optional date filtering."""
        stmt = select(EscalationStatusHistory).where(EscalationStatusHistory.escalation_id == escalation_id)

        if from_date:
            stmt = stmt.where(EscalationStatusHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(EscalationStatusHistory.changed_at <= to_date)

        stmt = stmt.order_by(EscalationStatusHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[EscalationStatusHistory]:
        """Get escalation status history for a user with optional date filtering."""
        stmt = select(EscalationStatusHistory).where(EscalationStatusHistory.user_id == user_id)

        if from_date:
            stmt = stmt.where(EscalationStatusHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(EscalationStatusHistory.changed_at <= to_date)

        stmt = stmt.order_by(EscalationStatusHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[EscalationStatusHistory], int]:
        """Get all escalation status history with filtering and pagination."""
        count_stmt = select(func.count(EscalationStatusHistory.id))
        stmt = select(EscalationStatusHistory)

        if from_date:
            stmt = stmt.where(EscalationStatusHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(EscalationStatusHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(EscalationStatusHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(EscalationStatusHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(EscalationStatusHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
