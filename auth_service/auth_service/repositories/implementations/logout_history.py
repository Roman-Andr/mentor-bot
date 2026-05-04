"""SQLAlchemy implementation of Logout history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import LogoutHistory
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.logout_history import ILogoutHistoryRepository


class LogoutHistoryRepository(SqlAlchemyBaseRepository[LogoutHistory, int], ILogoutHistoryRepository):
    """SQLAlchemy implementation of Logout history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize LogoutHistoryRepository with database session."""
        super().__init__(session, LogoutHistory)

    async def create(self, entity: LogoutHistory) -> LogoutHistory:
        """Create logout history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
    ) -> Sequence[LogoutHistory]:
        """Get logout history for a user with optional date filtering."""
        stmt = select(LogoutHistory).where(LogoutHistory.user_id == user_id)

        if from_date:
            stmt = stmt.where(LogoutHistory.logout_at >= from_date)
        if to_date:
            stmt = stmt.where(LogoutHistory.logout_at <= to_date)

        stmt = stmt.order_by(LogoutHistory.logout_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[LogoutHistory], int]:
        """Get all logout history with filtering and pagination."""
        count_stmt = select(func.count(LogoutHistory.id))
        stmt = select(LogoutHistory)

        if from_date:
            stmt = stmt.where(LogoutHistory.logout_at >= from_date)
            count_stmt = count_stmt.where(LogoutHistory.logout_at >= from_date)
        if to_date:
            stmt = stmt.where(LogoutHistory.logout_at <= to_date)
            count_stmt = count_stmt.where(LogoutHistory.logout_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(LogoutHistory.logout_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
