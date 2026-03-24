"""User repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from auth_service.core import UserRole
from auth_service.models import User
from auth_service.repositories.interfaces.base import BaseRepository


class IUserRepository(BaseRepository["User", int]):
    """User repository interface with user-specific queries."""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""

    @abstractmethod
    async def get_by_employee_id(self, employee_id: str) -> User | None:
        """Get user by employee ID."""

    @abstractmethod
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

    @abstractmethod
    async def update_last_login(self, user_id: int, login_time: datetime) -> None:
        """Update user's last login timestamp."""

    @abstractmethod
    async def update_role(self, user_id: int, role: UserRole) -> User:
        """Update user's role."""

    @abstractmethod
    async def deactivate_user(self, user_id: int) -> User:
        """Deactivate user account."""
