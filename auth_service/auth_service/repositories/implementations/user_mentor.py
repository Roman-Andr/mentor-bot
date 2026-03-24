"""SQLAlchemy implementation of UserMentor repository."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import UserMentor
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.user_mentor import IUserMentorRepository


class UserMentorRepository(SqlAlchemyBaseRepository[UserMentor, int], IUserMentorRepository):
    """SQLAlchemy implementation of UserMentor repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize UserMentorRepository with database session."""
        super().__init__(session, UserMentor)

    async def get_by_user_id(self, user_id: int) -> Sequence[UserMentor]:
        """Get all mentor relations for a user."""
        stmt = select(UserMentor).where(UserMentor.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_mentor_id(self, mentor_id: int) -> Sequence[UserMentor]:
        """Get all mentee relations for a mentor."""
        stmt = select(UserMentor).where(UserMentor.mentor_id == mentor_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_active_by_user_id(self, user_id: int) -> UserMentor | None:
        """Get active mentor relation for a user."""
        stmt = select(UserMentor).where(
            UserMentor.user_id == user_id,
            UserMentor.is_active.is_(True),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_mentor(self, user_id: int, mentor_id: int) -> UserMentor | None:
        """Get relation by user and mentor IDs."""
        stmt = select(UserMentor).where(
            UserMentor.user_id == user_id,
            UserMentor.mentor_id == mentor_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
