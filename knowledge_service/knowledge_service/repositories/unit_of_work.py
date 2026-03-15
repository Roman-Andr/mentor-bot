"""Unit of Work pattern for transaction management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Protocol, Self, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from knowledge_service.repositories.implementations.article import ArticleRepository
from knowledge_service.repositories.implementations.article_view import ArticleViewRepository
from knowledge_service.repositories.implementations.attachment import AttachmentRepository
from knowledge_service.repositories.implementations.category import CategoryRepository
from knowledge_service.repositories.implementations.search_history import SearchHistoryRepository
from knowledge_service.repositories.implementations.tag import TagRepository
from knowledge_service.repositories.interfaces.article import IArticleRepository
from knowledge_service.repositories.interfaces.article_view import IArticleViewRepository
from knowledge_service.repositories.interfaces.attachment import IAttachmentRepository
from knowledge_service.repositories.interfaces.category import ICategoryRepository
from knowledge_service.repositories.interfaces.search_history import ISearchHistoryRepository
from knowledge_service.repositories.interfaces.tag import ITagRepository


@runtime_checkable
class IUnitOfWork(Protocol):
    """Unit of Work interface for managing repositories and transactions."""

    articles: IArticleRepository
    article_views: IArticleViewRepository
    attachments: IAttachmentRepository
    categories: ICategoryRepository
    search_history: ISearchHistoryRepository
    tags: ITagRepository

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, *args: object) -> None: ...


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of Unit of Work."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self.articles = ArticleRepository(self._session)
        self.article_views = ArticleViewRepository(self._session)
        self.attachments = AttachmentRepository(self._session)
        self.categories = CategoryRepository(self._session)
        self.search_history = SearchHistoryRepository(self._session)
        self.tags = TagRepository(self._session)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        if not self._session:
            msg = "Session not initialized"
            raise RuntimeError(msg)
        await self._session.commit()

    async def rollback(self) -> None:
        if not self._session:
            msg = "Session not initialized"
            raise RuntimeError(msg)
        await self._session.rollback()


@asynccontextmanager
async def sqlalchemy_uow(session_factory: async_sessionmaker) -> AsyncGenerator[SqlAlchemyUnitOfWork, None]:
    """Async context manager for SqlAlchemyUnitOfWork."""
    async with SqlAlchemyUnitOfWork(session_factory) as uow:
        yield uow
