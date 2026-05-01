"""SQLAlchemy implementation of Password change history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import PasswordChangeHistory
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.password_change_history import IPasswordChangeHistoryRepository


class PasswordChangeHistoryRepository(
    SqlAlchemyBaseRepository[PasswordChangeHistory, int], IPasswordChangeHistoryRepository
):
    """SQLAlchemy implementation of Password change history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize PasswordChangeHistoryRepository with database session."""
        super().__init__(session, PasswordChangeHistory)

    async def create(self, entity: PasswordChangeHistory) -> PasswordChangeHistory:
        """Create password change history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[PasswordChangeHistory]:
        """Get password change history for a user with optional date filtering."""
        stmt = select(PasswordChangeHistory).where(PasswordChangeHistory.user_id == user_id)

        if from_date:
            stmt = stmt.where(PasswordChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(PasswordChangeHistory.changed_at <= to_date)

        stmt = stmt.order_by(PasswordChangeHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[PasswordChangeHistory], int]:
        """Get all password change history with filtering and pagination."""
        count_stmt = select(func.count(PasswordChangeHistory.id))
        stmt = select(PasswordChangeHistory)

        if from_date:
            stmt = stmt.where(PasswordChangeHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(PasswordChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(PasswordChangeHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(PasswordChangeHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(PasswordChangeHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
