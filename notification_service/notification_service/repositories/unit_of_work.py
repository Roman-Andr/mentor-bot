"""Unit of Work pattern for transaction management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Protocol, Self, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from notification_service.repositories.implementations.notification import (
    NotificationRepository,
    ScheduledNotificationRepository,
)
from notification_service.repositories.implementations.template import NotificationTemplateRepository
from notification_service.repositories.interfaces.notification import (
    INotificationRepository,
    IScheduledNotificationRepository,
)
from notification_service.repositories.interfaces.template import INotificationTemplateRepository


@runtime_checkable
class IUnitOfWork(Protocol):
    """Unit of Work interface for managing repositories and transactions."""

    notifications: INotificationRepository
    scheduled_notifications: IScheduledNotificationRepository
    templates: INotificationTemplateRepository

    async def commit(self) -> None:
        """Commit all changes made in this unit of work."""
        ...  # pragma: no cover

    async def rollback(self) -> None:
        """Rollback all changes made in this unit of work."""
        ...  # pragma: no cover

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        ...  # pragma: no cover

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        ...  # pragma: no cover


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of Unit of Work."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Initialize Unit of Work with session factory."""
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        """Enter async context manager and initialize repositories."""
        self._session = self._session_factory()
        self.notifications = NotificationRepository(self._session)
        self.scheduled_notifications = ScheduledNotificationRepository(self._session)
        self.templates = NotificationTemplateRepository(self._session)
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager and clean up session."""
        if self._session:
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
