"""SQLAlchemy implementation of Role change history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import RoleChangeHistory
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.role_change_history import IRoleChangeHistoryRepository


class RoleChangeHistoryRepository(SqlAlchemyBaseRepository[RoleChangeHistory, int], IRoleChangeHistoryRepository):
    """SQLAlchemy implementation of Role change history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize RoleChangeHistoryRepository with database session."""
        super().__init__(session, RoleChangeHistory)

    async def create(self, entity: RoleChangeHistory) -> RoleChangeHistory:
        """Create role change history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[RoleChangeHistory]:
        """Get role change history for a user with optional date filtering."""
        stmt = select(RoleChangeHistory).where(RoleChangeHistory.user_id == user_id)

        if from_date:
            stmt = stmt.where(RoleChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(RoleChangeHistory.changed_at <= to_date)

        stmt = stmt.order_by(RoleChangeHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[RoleChangeHistory], int]:
        """Get all role change history with filtering and pagination."""
        count_stmt = select(func.count(RoleChangeHistory.id))
        stmt = select(RoleChangeHistory)

        if from_date:
            stmt = stmt.where(RoleChangeHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(RoleChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(RoleChangeHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(RoleChangeHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(RoleChangeHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
