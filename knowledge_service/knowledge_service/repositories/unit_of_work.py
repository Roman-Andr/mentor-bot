"""Unit of Work pattern for transaction management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Protocol, Self, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from knowledge_service.repositories.implementations.article import ArticleRepository
from knowledge_service.repositories.implementations.article_view import ArticleViewRepository
from knowledge_service.repositories.implementations.attachment import AttachmentRepository
from knowledge_service.repositories.implementations.category import CategoryRepository
from knowledge_service.repositories.implementations.dialogue import DialogueScenarioRepository, DialogueStepRepository
from knowledge_service.repositories.implementations.search_history import SearchHistoryRepository
from knowledge_service.repositories.implementations.tag import TagRepository
from knowledge_service.repositories.interfaces.article import IArticleRepository
from knowledge_service.repositories.interfaces.article_view import IArticleViewRepository
from knowledge_service.repositories.interfaces.attachment import IAttachmentRepository
from knowledge_service.repositories.interfaces.category import ICategoryRepository
from knowledge_service.repositories.interfaces.dialogue import IDialogueScenarioRepository, IDialogueStepRepository
from knowledge_service.repositories.interfaces.search_history import ISearchHistoryRepository
from knowledge_service.repositories.interfaces.tag import ITagRepository


@runtime_checkable
class IUnitOfWork(Protocol):
    """Unit of Work interface for managing repositories and transactions."""

    articles: IArticleRepository
    article_views: IArticleViewRepository
    attachments: IAttachmentRepository
    categories: ICategoryRepository
    dialogue_scenarios: IDialogueScenarioRepository
    dialogue_steps: IDialogueStepRepository
    search_history: ISearchHistoryRepository
    tags: ITagRepository

    @property
    def session(self) -> AsyncSession:
        """Get the current database session."""
        ...

    async def commit(self) -> None:
        """Commit the current transaction."""
        ...

    async def rollback(self) -> None:
        """Rollback the current transaction."""
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
        """Initialize unit of work with session factory."""
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        """Get the current database session."""
        if not self._session:
            msg = "Session not initialized"
            raise RuntimeError(msg)
        return self._session

    async def __aenter__(self) -> Self:
        """Initialize session and repositories."""
        self._session = self._session_factory()
        self.articles = ArticleRepository(self._session)
        self.article_views = ArticleViewRepository(self._session)
        self.attachments = AttachmentRepository(self._session)
        self.categories = CategoryRepository(self._session)
        self.dialogue_scenarios = DialogueScenarioRepository(self._session)
        self.dialogue_steps = DialogueStepRepository(self._session)
        self.search_history = SearchHistoryRepository(self._session)
        self.tags = TagRepository(self._session)
        return self

    async def __aexit__(self, *args: object) -> None:
        """Close session on context exit."""
        if self._session:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        """Commit the current transaction."""
        if not self._session:
            msg = "Session not initialized"
            raise RuntimeError(msg)
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if not self._session:
            msg = "Session not initialized"
            raise RuntimeError(msg)
        await self._session.rollback()


@asynccontextmanager
async def sqlalchemy_uow(session_factory: async_sessionmaker) -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    """Async context manager for SqlAlchemyUnitOfWork."""
    async with SqlAlchemyUnitOfWork(session_factory) as uow:
        yield uow
