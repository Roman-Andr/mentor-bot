"""Unit of Work pattern for transaction management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Protocol, Self, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from checklists_service.repositories.implementations.checklist import ChecklistRepository
from checklists_service.repositories.implementations.task import TaskRepository
from checklists_service.repositories.implementations.template import TaskTemplateRepository, TemplateRepository
from checklists_service.repositories.interfaces.checklist import IChecklistRepository
from checklists_service.repositories.interfaces.task import ITaskRepository
from checklists_service.repositories.interfaces.template import ITaskTemplateRepository, ITemplateRepository


@runtime_checkable
class IUnitOfWork(Protocol):
    """Unit of Work interface for managing repositories and transactions."""

    checklists: IChecklistRepository
    tasks: ITaskRepository
    templates: ITemplateRepository
    task_templates: ITaskTemplateRepository

    async def commit(self) -> None:
        """Commit all changes made in this unit of work."""
        ...

    async def rollback(self) -> None:
        """Rollback all changes made in this unit of work."""
        ...

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        ...

    async def __aexit__(self, *args: object) -> None:
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
        self.checklists = ChecklistRepository(self._session)
        self.tasks = TaskRepository(self._session)
        self.templates = TemplateRepository(self._session)
        self.task_templates = TaskTemplateRepository(self._session)
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager and clean up session."""
        if self._session:
            if args and args[0]:
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
