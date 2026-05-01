"""Unit of Work pattern for transaction management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Protocol, Self, runtime_checkable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from auth_service.repositories.implementations.department import DepartmentRepository
from auth_service.repositories.implementations.invitation import InvitationRepository
from auth_service.repositories.implementations.invitation_status_history import InvitationStatusHistoryRepository
from auth_service.repositories.implementations.login_history import LoginHistoryRepository
from auth_service.repositories.implementations.mentor_assignment_history import MentorAssignmentHistoryRepository
from auth_service.repositories.implementations.password_change_history import PasswordChangeHistoryRepository
from auth_service.repositories.implementations.role_change_history import RoleChangeHistoryRepository
from auth_service.repositories.implementations.user import UserRepository
from auth_service.repositories.implementations.user_mentor import UserMentorRepository
from auth_service.repositories.interfaces.department import IDepartmentRepository
from auth_service.repositories.interfaces.invitation import IInvitationRepository
from auth_service.repositories.interfaces.invitation_status_history import IInvitationStatusHistoryRepository
from auth_service.repositories.interfaces.login_history import ILoginHistoryRepository
from auth_service.repositories.interfaces.mentor_assignment_history import IMentorAssignmentHistoryRepository
from auth_service.repositories.interfaces.password_change_history import IPasswordChangeHistoryRepository
from auth_service.repositories.interfaces.role_change_history import IRoleChangeHistoryRepository
from auth_service.repositories.interfaces.user import IUserRepository
from auth_service.repositories.interfaces.user_mentor import IUserMentorRepository


@runtime_checkable
class IUnitOfWork(Protocol):
    """Unit of Work interface for managing repositories and transactions."""

    users: IUserRepository
    invitations: IInvitationRepository
    departments: IDepartmentRepository
    user_mentors: IUserMentorRepository
    login_history: ILoginHistoryRepository
    password_change_history: IPasswordChangeHistoryRepository
    role_change_history: IRoleChangeHistoryRepository
    invitation_status_history: IInvitationStatusHistoryRepository
    mentor_assignment_history: IMentorAssignmentHistoryRepository

    async def commit(self) -> None:
        """Commit all changes made in this unit of work."""
        ...

    async def rollback(self) -> None:
        """Rollback all changes made in this unit of work."""
        ...

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        ...

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object
    ) -> None:
        """Exit async context manager."""
        ...


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of Unit of Work."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Initialize Unit of Work with session factory."""
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        """Enter async context manager and initialize repositories."""
        self._session = self._session_factory()
        self.users = UserRepository(self._session)
        self.invitations = InvitationRepository(self._session)
        self.departments = DepartmentRepository(self._session)
        self.user_mentors = UserMentorRepository(self._session)
        self.login_history = LoginHistoryRepository(self._session)
        self.password_change_history = PasswordChangeHistoryRepository(self._session)
        self.role_change_history = RoleChangeHistoryRepository(self._session)
        self.invitation_status_history = InvitationStatusHistoryRepository(self._session)
        self.mentor_assignment_history = MentorAssignmentHistoryRepository(self._session)
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object
    ) -> None:
        """Exit async context manager and clean up session."""
        if self._session:
            if exc_type:
                logger.warning("UoW rollback on exit due to exception: {}", exc_type.__name__)
                await self._session.rollback()
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        """Commit all changes made in this unit of work."""
        if not self._session:
            logger.error("UoW commit attempted on uninitialized session")
            msg = "Session not initialized"
            raise RuntimeError(msg)
        logger.debug("UoW commit")
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback all changes made in this unit of work."""
        if not self._session:
            logger.error("UoW rollback attempted on uninitialized session")
            msg = "Session not initialized"
            raise RuntimeError(msg)
        logger.debug("UoW rollback")
        await self._session.rollback()


@asynccontextmanager
async def sqlalchemy_uow(session_factory: async_sessionmaker) -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    """Async context manager for SqlAlchemyUnitOfWork."""
    async with SqlAlchemyUnitOfWork(session_factory) as uow:
        yield uow
