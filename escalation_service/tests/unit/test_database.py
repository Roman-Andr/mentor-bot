"""Unit tests for escalation_service/database.py."""

import contextlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from escalation_service.database import get_db, init_db


class TestDatabaseModule:
    """Tests for database module functions."""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """Test that get_db yields an async session."""
        mock_session = AsyncMock()
        # Mock AsyncSessionLocal as an async context manager
        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("escalation_service.database.AsyncSessionLocal", mock_factory):
            # Get the async generator
            gen = get_db()

            # Get the yielded session
            session = await gen.asend(None)
            assert session is not None

            # Close the generator successfully (triggers commit)
            with contextlib.suppress(StopAsyncIteration):
                await gen.asend(None)

    @pytest.mark.asyncio
    async def test_get_db_commits_on_success(self):
        """Test that get_db commits on successful exit."""
        mock_session = AsyncMock()
        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("escalation_service.database.AsyncSessionLocal", mock_factory):
            gen = get_db()
            await gen.asend(None)

            # Simulate successful completion
            with contextlib.suppress(StopAsyncIteration):
                await gen.asend(None)

            # Verify commit was called
            mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_db_rollback_on_exception(self):
        """Test that get_db rolls back on exception."""
        mock_session = AsyncMock()
        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("escalation_service.database.AsyncSessionLocal", mock_factory):
            gen = get_db()
            await gen.asend(None)

            # Simulate exception
            with contextlib.suppress(ValueError):
                await gen.athrow(ValueError("Test error"))

            # Verify rollback was called
            mock_session.rollback.assert_awaited_once()


class TestInitDB:
    """Tests for init_db function."""

    @pytest.mark.asyncio
    async def test_init_db_runs_without_error(self):
        """Test that init_db runs without error (uses public schema, no schema creation needed)."""
        mock_engine = MagicMock()

        with patch("escalation_service.database.engine", mock_engine):
            await init_db()
