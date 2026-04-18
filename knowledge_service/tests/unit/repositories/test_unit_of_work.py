"""Tests for Unit of Work implementation."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from knowledge_service.repositories.implementations.article import ArticleRepository
from knowledge_service.repositories.implementations.article_view import ArticleViewRepository
from knowledge_service.repositories.implementations.attachment import AttachmentRepository
from knowledge_service.repositories.implementations.category import CategoryRepository
from knowledge_service.repositories.implementations.dialogue import DialogueScenarioRepository, DialogueStepRepository
from knowledge_service.repositories.implementations.search_history import SearchHistoryRepository
from knowledge_service.repositories.implementations.tag import TagRepository
from knowledge_service.repositories.unit_of_work import (
    SqlAlchemyUnitOfWork,
    sqlalchemy_uow,
)


class TestSqlAlchemyUnitOfWork:
    """Test Unit of Work implementation."""

    @pytest.fixture
    def mock_session_factory(self):
        """Create a mock session factory."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.close = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        factory = MagicMock(spec=async_sessionmaker)
        factory.return_value = mock_session
        return factory, mock_session

    async def test_init(self, mock_session_factory):
        """Test UOW initialization."""
        factory, _ = mock_session_factory
        uow = SqlAlchemyUnitOfWork(factory)

        assert uow._session_factory == factory
        assert uow._session is None

    async def test_aenter_initializes_repositories(self, mock_session_factory):
        """Test entering context initializes all repositories."""
        factory, mock_session = mock_session_factory
        uow = SqlAlchemyUnitOfWork(factory)

        async with uow:
            assert uow._session == mock_session
            assert isinstance(uow.articles, ArticleRepository)
            assert isinstance(uow.article_views, ArticleViewRepository)
            assert isinstance(uow.attachments, AttachmentRepository)
            assert isinstance(uow.categories, CategoryRepository)
            assert isinstance(uow.dialogue_scenarios, DialogueScenarioRepository)
            assert isinstance(uow.dialogue_steps, DialogueStepRepository)
            assert isinstance(uow.search_history, SearchHistoryRepository)
            assert isinstance(uow.tags, TagRepository)

    async def test_aexit_closes_session(self, mock_session_factory):
        """Test exiting context closes session."""
        factory, mock_session = mock_session_factory
        uow = SqlAlchemyUnitOfWork(factory)

        async with uow:
            pass

        mock_session.close.assert_called_once()
        assert uow._session is None

    async def test_session_property_raises_when_not_initialized(self, mock_session_factory):
        """Test accessing session before initialization raises error."""
        factory, _ = mock_session_factory
        uow = SqlAlchemyUnitOfWork(factory)

        with pytest.raises(RuntimeError, match="Session not initialized"):
            _ = uow.session

    async def test_session_property_returns_session_when_initialized(self, mock_session_factory):
        """Test accessing session after initialization returns session."""
        factory, mock_session = mock_session_factory
        uow = SqlAlchemyUnitOfWork(factory)

        async with uow:
            assert uow.session == mock_session

    async def test_commit_success(self, mock_session_factory):
        """Test successful commit."""
        factory, mock_session = mock_session_factory
        uow = SqlAlchemyUnitOfWork(factory)

        async with uow:
            await uow.commit()
            mock_session.commit.assert_called_once()

    async def test_commit_raises_when_not_initialized(self, mock_session_factory):
        """Test commit before initialization raises error."""
        factory, _ = mock_session_factory
        uow = SqlAlchemyUnitOfWork(factory)

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await uow.commit()

    async def test_rollback_success(self, mock_session_factory):
        """Test successful rollback."""
        factory, mock_session = mock_session_factory
        uow = SqlAlchemyUnitOfWork(factory)

        async with uow:
            await uow.rollback()
            mock_session.rollback.assert_called_once()

    async def test_rollback_raises_when_not_initialized(self, mock_session_factory):
        """Test rollback before initialization raises error."""
        factory, _ = mock_session_factory
        uow = SqlAlchemyUnitOfWork(factory)

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await uow.rollback()

    async def test_context_manager_exception_handling(self, mock_session_factory):
        """Test that session is closed even when exception occurs."""
        factory, mock_session = mock_session_factory
        uow = SqlAlchemyUnitOfWork(factory)

        with pytest.raises(ValueError, match="Test error"):
            async with uow:
                msg = "Test error"
                raise ValueError(msg)

        mock_session.close.assert_called_once()
        assert uow._session is None


class TestSqlalchemyUowContextManager:
    """Test the sqlalchemy_uow async context manager."""

    @pytest.fixture
    def mock_factory(self):
        """Create a mock session factory."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.close = AsyncMock()

        factory = MagicMock(spec=async_sessionmaker)
        factory.return_value = mock_session
        return factory

    async def test_context_manager_yields_uow(self, mock_factory):
        """Test that context manager yields a UOW instance."""
        async with sqlalchemy_uow(mock_factory) as uow:
            assert isinstance(uow, SqlAlchemyUnitOfWork)
            assert uow._session is not None

    async def test_context_manager_closes_on_exit(self, mock_factory):
        """Test that session is closed on context exit."""
        mock_session = mock_factory.return_value

        async with sqlalchemy_uow(mock_factory) as uow:
            pass

        mock_session.close.assert_called_once()
        assert uow._session is None
