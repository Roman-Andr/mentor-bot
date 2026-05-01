"""SQLAlchemy implementation of Login history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import LoginHistory
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.login_history import ILoginHistoryRepository


class LoginHistoryRepository(SqlAlchemyBaseRepository[LoginHistory, int], ILoginHistoryRepository):
    """SQLAlchemy implementation of Login history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize LoginHistoryRepository with database session."""
        super().__init__(session, LoginHistory)

    async def create(self, entity: LoginHistory) -> LoginHistory:
        """Create login history entry."""
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
    ) -> Sequence[LoginHistory]:
        """Get login history for a user with optional date filtering."""
        stmt = select(LoginHistory).where(LoginHistory.user_id == user_id)

        if from_date:
            stmt = stmt.where(LoginHistory.login_at >= from_date)
        if to_date:
            stmt = stmt.where(LoginHistory.login_at <= to_date)

        stmt = stmt.order_by(LoginHistory.login_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[LoginHistory], int]:
        """Get all login history with filtering and pagination."""
        count_stmt = select(func.count(LoginHistory.id))
        stmt = select(LoginHistory)

        if from_date:
            stmt = stmt.where(LoginHistory.login_at >= from_date)
            count_stmt = count_stmt.where(LoginHistory.login_at >= from_date)
        if to_date:
            stmt = stmt.where(LoginHistory.login_at <= to_date)
            count_stmt = count_stmt.where(LoginHistory.login_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(LoginHistory.login_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
