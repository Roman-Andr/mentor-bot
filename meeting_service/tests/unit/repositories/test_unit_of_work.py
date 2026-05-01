"""Unit tests for Unit of Work pattern."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from meeting_service.repositories.unit_of_work import (
    SqlAlchemyUnitOfWork,
    sqlalchemy_uow,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class TestSqlAlchemyUnitOfWork:
    """Tests for SqlAlchemyUnitOfWork class."""

    async def test_commit_without_session_raises_runtime_error(self):
        """Test that commit() raises RuntimeError when session is None."""
        # Arrange
        mock_session_factory = MagicMock(spec=async_sessionmaker)
        uow = SqlAlchemyUnitOfWork(mock_session_factory)
        # Don't enter context manager, so _session remains None

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await uow.commit()
        assert "Session not initialized" in str(exc_info.value)

    async def test_rollback_without_session_raises_runtime_error(self):
        """Test that rollback() raises RuntimeError when session is None."""
        # Arrange
        mock_session_factory = MagicMock(spec=async_sessionmaker)
        uow = SqlAlchemyUnitOfWork(mock_session_factory)
        # Don't enter context manager, so _session remains None

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await uow.rollback()
        assert "Session not initialized" in str(exc_info.value)

    async def test_context_manager_initializes_repositories(self):
        """Test that entering context manager initializes all repositories."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session_factory = MagicMock(spec=async_sessionmaker, return_value=mock_session)

        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        # Act
        async with uow as ctx:
            # Assert - verify all repositories are initialized
            assert ctx.meetings is not None
            assert ctx.materials is not None
            assert ctx.user_meetings is not None
            assert ctx.google_calendar_accounts is not None

    async def test_context_manager_closes_session_on_exit(self):
        """Test that session is closed when exiting context manager."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.close = AsyncMock()
        mock_session_factory = MagicMock(spec=async_sessionmaker, return_value=mock_session)

        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        # Act
        async with uow:
            pass  # Just enter and exit

        # Assert - session should be closed
        mock_session.close.assert_called_once()
        assert uow._session is None

    async def test_commit_with_active_session(self):
        """Test that commit() works when session is active."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.close = AsyncMock()
        mock_session_factory = MagicMock(spec=async_sessionmaker, return_value=mock_session)

        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        # Act
        async with uow:
            await uow.commit()

        # Assert
        mock_session.commit.assert_called_once()

    async def test_rollback_with_active_session(self):
        """Test that rollback() works when session is active."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        mock_session_factory = MagicMock(spec=async_sessionmaker, return_value=mock_session)

        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        # Act
        async with uow:
            await uow.rollback()

        # Assert
        mock_session.rollback.assert_called_once()

    async def test_aexit_rollbacks_session_on_exception(self):
        """Exiting the context manager with an exception triggers session.rollback()."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        mock_session_factory = MagicMock(spec=async_sessionmaker, return_value=mock_session)

        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        # Act & Assert
        with pytest.raises(ValueError, match="boom"):
            async with uow:
                msg = "boom"
                raise ValueError(msg)

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        assert uow._session is None


class TestSqlalchemyUowContextManager:
    """Tests for the sqlalchemy_uow async context manager function."""

    async def test_sqlalchemy_uow_yields_unit_of_work(self):
        """Test that sqlalchemy_uow yields a SqlAlchemyUnitOfWork instance."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.close = AsyncMock()
        mock_session_factory = MagicMock(spec=async_sessionmaker, return_value=mock_session)

        # Act & Assert
        async with sqlalchemy_uow(mock_session_factory) as uow:
            assert isinstance(uow, SqlAlchemyUnitOfWork)
            assert uow._session is not None

    async def test_sqlalchemy_uow_closes_session_after_yield(self):
        """Test that sqlalchemy_uow properly closes session after use."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.close = AsyncMock()
        mock_session_factory = MagicMock(spec=async_sessionmaker, return_value=mock_session)

        # Act
        async with sqlalchemy_uow(mock_session_factory) as uow:
            pass  # Just use and exit

        # Assert
        mock_session.close.assert_called_once()
        assert uow._session is None
