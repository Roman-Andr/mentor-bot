"""Unit of Work pattern for transaction management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Protocol, Self, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from meeting_service.repositories.implementations.department import DepartmentRepository
from meeting_service.repositories.implementations.google_calendar_account import (
    SQLAlchemyGoogleCalendarAccountRepository,
)
from meeting_service.repositories.implementations.material import MaterialRepository
from meeting_service.repositories.implementations.meeting import MeetingRepository
from meeting_service.repositories.implementations.user_meeting import UserMeetingRepository
from meeting_service.repositories.interfaces.department import IDepartmentRepository
from meeting_service.repositories.interfaces.google_calendar_account import IGoogleCalendarAccountRepository
from meeting_service.repositories.interfaces.material import IMaterialRepository
from meeting_service.repositories.interfaces.meeting import IMeetingRepository
from meeting_service.repositories.interfaces.user_meeting import IUserMeetingRepository


@runtime_checkable
class IUnitOfWork(Protocol):
    """Unit of Work interface for managing repositories and transactions."""

    meetings: IMeetingRepository
    materials: IMaterialRepository
    user_meetings: IUserMeetingRepository
    google_calendar_accounts: IGoogleCalendarAccountRepository
    departments: IDepartmentRepository

    async def commit(self) -> None:
        """Commit all changes made in this unit of work."""

    async def rollback(self) -> None:
        """Rollback all changes made in this unit of work."""

    async def __aenter__(self) -> Self:
        """Enter async context manager."""

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of Unit of Work."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Initialize Unit of Work with session factory."""
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        """Enter async context manager and initialize repositories."""
        self._session = self._session_factory()
        self.meetings = MeetingRepository(self._session)
        self.materials = MaterialRepository(self._session)
        self.user_meetings = UserMeetingRepository(self._session)
        self.google_calendar_accounts = SQLAlchemyGoogleCalendarAccountRepository(self._session)
        self.departments = DepartmentRepository(self._session)
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object
    ) -> None:
        """Exit async context manager and clean up session."""
        if self._session:
            if exc_type:
                await self._session.rollback()
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        """Commit all changes made in this unit of work."""
        if not self._session:
            msg = "Session not initialized"
            raise RuntimeError(msg)
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback all changes made in this unit of work."""
        if not self._session:
            msg = "Session not initialized"
            raise RuntimeError(msg)
        await self._session.rollback()


@asynccontextmanager
async def sqlalchemy_uow(session_factory: async_sessionmaker) -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    """Async context manager for SqlAlchemyUnitOfWork."""
    async with SqlAlchemyUnitOfWork(session_factory) as uow:
        yield uow
