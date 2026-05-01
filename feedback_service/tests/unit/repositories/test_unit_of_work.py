"""Unit tests for SqlAlchemyUnitOfWork."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from feedback_service.repositories.unit_of_work import (
    IUnitOfWork,
    SqlAlchemyUnitOfWork,
    sqlalchemy_uow,
)


class TestSqlAlchemyUnitOfWork:
    """Tests for SqlAlchemyUnitOfWork class."""

    async def test_init_stores_session_factory(self) -> None:
        """Test __init__ stores the session factory."""
        # Arrange
        mock_factory = MagicMock(spec=async_sessionmaker)

        # Act
        uow = SqlAlchemyUnitOfWork(mock_factory)

        # Assert
        assert uow._session_factory == mock_factory
        assert uow._session is None

    async def test_aenter_initializes_repositories(self) -> None:
        """Test __aenter__ creates session and initializes repositories."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_factory = MagicMock(return_value=mock_session)
        mock_factory.__class__ = async_sessionmaker

        uow = SqlAlchemyUnitOfWork(mock_factory)

        # Act
        result = await uow.__aenter__()

        # Assert
        assert result is uow
        assert uow._session is mock_session
        assert uow.pulse_surveys is not None
        assert uow.experience_ratings is not None
        assert uow.comments is not None
        mock_factory.assert_called_once()

    async def test_aexit_with_exception_rolls_back(self) -> None:
        """Test __aexit__ rolls back and closes session on exception."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        mock_factory = MagicMock(return_value=mock_session)
        mock_factory.__class__ = async_sessionmaker

        uow = SqlAlchemyUnitOfWork(mock_factory)
        await uow.__aenter__()

        # Act
        await uow.__aexit__(ValueError, ValueError("Test error"), None)

        # Assert
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        assert uow._session is None

    async def test_aexit_without_exception_closes(self) -> None:
        """Test __aexit__ closes session without exception."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.close = AsyncMock()
        mock_factory = MagicMock(return_value=mock_session)
        mock_factory.__class__ = async_sessionmaker

        uow = SqlAlchemyUnitOfWork(mock_factory)
        await uow.__aenter__()

        # Act
        await uow.__aexit__(None, None, None)

        # Assert
        mock_session.close.assert_called_once()
        assert uow._session is None

    async def test_commit_success(self) -> None:
        """Test commit calls session.commit."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_factory = MagicMock(return_value=mock_session)
        mock_factory.__class__ = async_sessionmaker

        uow = SqlAlchemyUnitOfWork(mock_factory)
        await uow.__aenter__()

        # Act
        await uow.commit()

        # Assert
        mock_session.commit.assert_called_once()

    async def test_commit_raises_when_no_session(self) -> None:
        """Test commit raises RuntimeError when session is None."""
        # Arrange
        mock_factory = MagicMock(spec=async_sessionmaker)
        uow = SqlAlchemyUnitOfWork(mock_factory)
        # Don't enter context, so session stays None

        # Act & Assert
        with pytest.raises(RuntimeError, match="Session not initialized"):
            await uow.commit()

    async def test_rollback_success(self) -> None:
        """Test rollback calls session.rollback."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.rollback = AsyncMock()
        mock_factory = MagicMock(return_value=mock_session)
        mock_factory.__class__ = async_sessionmaker

        uow = SqlAlchemyUnitOfWork(mock_factory)
        await uow.__aenter__()

        # Act
        await uow.rollback()

        # Assert
        mock_session.rollback.assert_called_once()

    async def test_rollback_raises_when_no_session(self) -> None:
        """Test rollback raises RuntimeError when session is None."""
        # Arrange
        mock_factory = MagicMock(spec=async_sessionmaker)
        uow = SqlAlchemyUnitOfWork(mock_factory)
        # Don't enter context, so session stays None

        # Act & Assert
        with pytest.raises(RuntimeError, match="Session not initialized"):
            await uow.rollback()


class TestSqlalchemyUow:
    """Tests for sqlalchemy_uow context manager."""

    async def test_sqlalchemy_uow_yields_uow(self) -> None:
        """Test sqlalchemy_uow yields a SqlAlchemyUnitOfWork instance."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.close = AsyncMock()
        mock_factory = MagicMock(return_value=mock_session)
        mock_factory.__class__ = async_sessionmaker

        # Act & Assert
        async with sqlalchemy_uow(mock_factory) as uow:
            assert isinstance(uow, SqlAlchemyUnitOfWork)
            assert uow._session is mock_session

    async def test_sqlalchemy_uow_closes_on_exit(self) -> None:
        """Test sqlalchemy_uow closes session on exit."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.close = AsyncMock()
        mock_factory = MagicMock(return_value=mock_session)
        mock_factory.__class__ = async_sessionmaker

        # Act
        async with sqlalchemy_uow(mock_factory) as uow:
            pass

        # Assert
        mock_session.close.assert_called_once()

    async def test_sqlalchemy_uow_rolls_back_on_exception(self) -> None:
        """Test sqlalchemy_uow rolls back on exception."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        mock_factory = MagicMock(return_value=mock_session)
        mock_factory.__class__ = async_sessionmaker

        # Act & Assert
        with pytest.raises(ValueError, match="Test error"):
            async with sqlalchemy_uow(mock_factory) as uow:
                raise ValueError("Test error")

        # Assert
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


class TestIUnitOfWorkInterface:
    """Tests for IUnitOfWork protocol interface."""

    async def test_iunit_of_work_is_protocol(self) -> None:
        """Test IUnitOfWork is a runtime_checkable protocol."""
        # Arrange - Create a class that implements the protocol
        class MockUow:
            def __init__(self) -> None:
                self.pulse_surveys = MagicMock()
                self.experience_ratings = MagicMock()
                self.comments = MagicMock()
                self.feedback_status_change_history = MagicMock()

            async def commit(self) -> None:
                pass

            async def rollback(self) -> None:
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args) -> None:
                pass

        mock_uow = MockUow()

        # Assert
        assert isinstance(mock_uow, IUnitOfWork)
