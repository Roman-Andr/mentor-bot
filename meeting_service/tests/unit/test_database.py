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
    async def test_init_db_completes_successfully(self):
        """Test init_db completes without errors (no schema creation needed)."""
        from meeting_service.database import init_db

        await init_db()

    @pytest.mark.asyncio
    async def test_init_db_does_not_create_schema(self):
        """Test init_db does not attempt schema creation (uses public schema)."""
        from meeting_service.database import init_db

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock()

        with patch("meeting_service.database.engine", mock_engine):
            await init_db()

        mock_engine.begin.assert_not_called()


class TestBase:
    """Tests for declarative Base class."""

    def test_base_has_metadata(self):
        """Test Base class has correct metadata."""
        from meeting_service.database import Base, metadata_obj

        assert Base.metadata == metadata_obj

    def test_metadata_exists(self):
        """Test metadata object exists and is usable."""
        from meeting_service.database import metadata_obj

        assert metadata_obj is not None
        assert hasattr(metadata_obj, "tables")
