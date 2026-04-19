"""Unit tests for database module."""

from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


class TestGetEngine:
    """Tests for engine creation and configuration."""

    def test_engine_created_with_settings(self):
        """Test engine is created with correct configuration from settings."""
        from meeting_service.database import engine

        assert isinstance(engine, AsyncEngine)

    def test_engine_configuration(self):
        """Test engine has correct pool settings from config."""
        from meeting_service.config import settings
        from meeting_service.database import engine

        # Check that engine uses settings values
        assert engine.pool.size() == settings.DATABASE_POOL_SIZE
        assert engine.pool._max_overflow == settings.DATABASE_MAX_OVERFLOW


class TestGetDB:
    """Tests for get_db async generator."""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """Test get_db yields an async session."""
        from meeting_service.database import get_db

        # Mock AsyncSessionLocal
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=None)

        with patch("meeting_service.database.AsyncSessionLocal", return_value=mock_context):
            # Use the async generator
            async_gen = get_db()
            session = await async_gen.__anext__()

            assert session == mock_session

            # Clean up the generator
            with suppress(StopAsyncIteration):
                await async_gen.__anext__()

    @pytest.mark.asyncio
    async def test_get_db_commits_on_success(self):
        """Test get_db commits when no exception occurs."""
        from meeting_service.database import get_db

        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=None)

        with patch("meeting_service.database.AsyncSessionLocal", return_value=mock_context):
            async_gen = get_db()
            await async_gen.__anext__()

            # Simulate successful completion
            with suppress(StopAsyncIteration):
                await async_gen.__anext__()

            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_rollback_on_exception(self):
        """Test get_db rolls back on exception."""
        from meeting_service.database import get_db

        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=None)

        with patch("meeting_service.database.AsyncSessionLocal", return_value=mock_context):
            async_gen = get_db()
            await async_gen.__anext__()

            # Simulate exception by calling athrow
            with pytest.raises(ValueError, match="Test error"):
                await async_gen.athrow(ValueError("Test error"))

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()


class TestInitDB:
    """Tests for database initialization."""

    @pytest.mark.asyncio
    async def test_init_db_creates_schema(self):
        """Test init_db creates schema if not exists."""
        from meeting_service.database import init_db

        mock_conn = MagicMock()
        mock_conn.run_sync = AsyncMock()

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock()
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        mock_engine.begin.return_value = mock_context

        with patch("meeting_service.database.engine", mock_engine):
            await init_db()

        # Should call run_sync twice: once for schema creation, once for table creation
        assert mock_conn.run_sync.call_count == 2

    @pytest.mark.asyncio
    async def test_init_db_exception_handling(self):
        """Test init_db handles exceptions during initialization."""
        from meeting_service.database import init_db

        mock_conn = MagicMock()
        mock_conn.run_sync = AsyncMock(side_effect=Exception("Database error"))

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock()
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        mock_engine.begin.return_value = mock_context

        with patch("meeting_service.database.engine", mock_engine):
            with pytest.raises(Exception, match="Database error"):
                await init_db()

    @pytest.mark.asyncio
    async def test_init_db_schema_creation_call(self):
        """Test that init_db properly creates schema."""
        from meeting_service.database import init_db, settings

        mock_conn = MagicMock()
        mock_conn.run_sync = AsyncMock()

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock()
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        mock_engine.begin.return_value = mock_context

        with patch("meeting_service.database.engine", mock_engine):
            await init_db()

        # Get the first run_sync call (schema creation)
        first_call = mock_conn.run_sync.call_args_list[0]
        callable_arg = first_call[0][0]

        # Verify the callable when executed creates a CreateSchema statement
        mock_sync_conn = MagicMock()
        callable_arg(mock_sync_conn)

        # Check that execute was called on the sync connection
        mock_sync_conn.execute.assert_called_once()
        call_args = mock_sync_conn.execute.call_args[0][0]

        # Verify it's a CreateSchema statement for the correct schema
        assert str(settings.DATABASE_SCHEMA) in str(call_args)


class TestBase:
    """Tests for declarative Base class."""

    def test_base_has_metadata(self):
        """Test Base class has correct metadata."""
        from meeting_service.database import Base, metadata_obj

        assert Base.metadata == metadata_obj

    def test_metadata_has_schema(self):
        """Test metadata is configured with correct schema."""
        from meeting_service.database import metadata_obj, settings

        assert metadata_obj.schema == settings.DATABASE_SCHEMA
