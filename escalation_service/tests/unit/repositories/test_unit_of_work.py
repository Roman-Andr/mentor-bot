"""Unit tests for escalation_service/repositories/unit_of_work.py."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from escalation_service.repositories.unit_of_work import SqlAlchemyUnitOfWork, sqlalchemy_uow


class TestSqlAlchemyUOWContextManager:
    """Tests for sqlalchemy_uow async context manager (lines 74-75)."""

    @pytest.mark.asyncio
    async def test_sqlalchemy_uow_context_manager(self):
        """Test that sqlalchemy_uow yields a SqlAlchemyUnitOfWork instance."""
        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        async with sqlalchemy_uow(mock_session_factory) as uow:
            assert isinstance(uow, SqlAlchemyUnitOfWork)
            assert uow._session is not None

    @pytest.mark.asyncio
    async def test_sqlalchemy_uow_cleanup_on_exit(self):
        """Test that sqlalchemy_uow cleans up session on exit."""
        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        async with sqlalchemy_uow(mock_session_factory) as uow:
            pass

        # After exit, session should be closed
        mock_session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_sqlalchemy_uow_rollback_on_exception(self):
        """Test that sqlalchemy_uow handles exceptions properly."""
        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        with pytest.raises(ValueError, match="Test error"):
            async with sqlalchemy_uow(mock_session_factory) as uow:
                raise ValueError("Test error")

        # Session close should still be called on exception
        mock_session.close.assert_awaited_once()


class TestSqlAlchemyUnitOfWork:
    """Tests for SqlAlchemyUnitOfWork class."""

    @pytest.mark.asyncio
    async def test_uow_aenter_initializes_session(self):
        """Test that __aenter__ initializes session and repositories."""
        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        result = await uow.__aenter__()

        assert result is uow
        assert uow._session is mock_session
        assert uow.escalations is not None

    @pytest.mark.asyncio
    async def test_uow_aexit_closes_session(self):
        """Test that __aexit__ closes session."""
        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        uow = SqlAlchemyUnitOfWork(mock_session_factory)
        await uow.__aenter__()

        await uow.__aexit__(None, None, None)

        mock_session.close.assert_awaited_once()
        assert uow._session is None

    @pytest.mark.asyncio
    async def test_uow_commit_with_session(self):
        """Test that commit works with initialized session."""
        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        uow = SqlAlchemyUnitOfWork(mock_session_factory)
        await uow.__aenter__()

        await uow.commit()

        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_uow_rollback_with_session(self):
        """Test that rollback works with initialized session."""
        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        uow = SqlAlchemyUnitOfWork(mock_session_factory)
        await uow.__aenter__()

        await uow.rollback()

        mock_session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_uow_commit_raises_without_session(self):
        """Test that commit raises RuntimeError without session."""
        mock_session_factory = MagicMock()
        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await uow.commit()

    @pytest.mark.asyncio
    async def test_uow_rollback_raises_without_session(self):
        """Test that rollback raises RuntimeError without session."""
        mock_session_factory = MagicMock()
        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await uow.rollback()

    @pytest.mark.asyncio
    async def test_uow_aexit_with_none_session(self):
        """Test that __aexit__ handles None session gracefully (covers line 54->exit branch)."""
        mock_session_factory = MagicMock()
        uow = SqlAlchemyUnitOfWork(mock_session_factory)
        # Ensure _session is None (not initialized or explicitly set to None)
        uow._session = None

        # Should not raise any error and should not try to close a None session
        await uow.__aexit__(None, None, None)

        # Verify session is still None (no session was created or closed)
        assert uow._session is None
