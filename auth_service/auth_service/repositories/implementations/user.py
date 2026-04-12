"""SQLAlchemy implementation of User repository."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import cast

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth_service.core import UserRole
from auth_service.models import User
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.user import IUserRepository


class UserRepository(SqlAlchemyBaseRepository[User, int], IUserRepository):
    """SQLAlchemy implementation of User repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize UserRepository with database session."""
        super().__init__(session, User)

    async def create(self, entity: User) -> User:
        """Create user and reload with department relationship."""
        self._session.add(entity)
        await self._session.flush()
        return await self.get_by_id(entity.id) or entity  # type: ignore[return-value]

    async def get_by_id(self, entity_id: int) -> User | None:
        """Get user by ID with department and mentor relationships."""
        from auth_service.models.user_mentor import UserMentor

        stmt = (
            select(User)
            .where(User.id == entity_id)
            .options(
                selectinload(User.department),
                selectinload(User.mentor_assignments).selectinload(UserMentor.mentor),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        stmt = select(User).where(User.email == email).options(selectinload(User.department))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        stmt = select(User).where(User.telegram_id == telegram_id).options(selectinload(User.department))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_employee_id(self, employee_id: str) -> User | None:
        """Get user by employee ID."""
        stmt = select(User).where(User.employee_id == employee_id).options(selectinload(User.department))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_users(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        department_id: int | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> tuple[Sequence[User], int]:
        """Find users with filtering and return results with total count."""
        # Count query
        count_stmt = select(func.count(User.id))

        # Results query
        stmt = select(User).options(selectinload(User.department))

        # Apply filters to both queries
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.employee_id.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        if department_id is not None:
            stmt = stmt.where(User.department_id == department_id)
            count_stmt = count_stmt.where(User.department_id == department_id)

        if role:
            stmt = stmt.where(User.role == role)
            count_stmt = count_stmt.where(User.role == role)

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
            count_stmt = count_stmt.where(User.is_active == is_active)

        # Get total count
        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        # Get paginated results
        stmt = stmt.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self._session.execute(stmt)
        users = result.scalars().all()

        return users, total

    async def update(self, entity: User) -> User:
        """Update user and reload with department relationship."""
        await self._session.flush()
        return await self.get_by_id(entity.id) or entity  # type: ignore[return-value]

    async def update_last_login(self, user_id: int, login_time: datetime) -> None:
        """Update user's last login timestamp."""
        user = await self.get_by_id(user_id)
        if user:
            user.last_login_at = login_time
            await self._session.flush()

    async def update_role(self, user_id: int, role: UserRole) -> User:
        """Update user's role."""
        user = await self.get_by_id(user_id)
        if not user:
            msg = f"User with ID {user_id} not found"
            raise ValueError(msg)

        user.role = role
        user.updated_at = datetime.now(UTC)
        await self._session.flush()
        return await self.get_by_id(user_id) or user  # type: ignore[return-value]

    async def deactivate_user(self, user_id: int) -> User:
        """Deactivate user account."""
        user = await self.get_by_id(user_id)
        if not user:
            msg = f"User with ID {user_id} not found"
            raise ValueError(msg)

        user.is_active = False
        user.updated_at = datetime.now(UTC)
        await self._session.flush()
        return await self.get_by_id(user_id) or user  # type: ignore[return-value]
