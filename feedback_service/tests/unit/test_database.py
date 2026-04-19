"""Tests for database.py - connection handling and session management."""

from collections.abc import AsyncGenerator
from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from feedback_service.database import get_db


class TestGetDb:
    """Tests for get_db context manager."""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self) -> None:
        """Test get_db yields a session and commits successfully."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.close = AsyncMock()

        # Setup the async context manager behavior
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_factory = MagicMock(return_value=mock_session)

        with patch("feedback_service.database.AsyncSessionLocal", mock_factory):
            # Act
            gen: AsyncGenerator = get_db()
            session = await gen.__anext__()

            # Assert - session is yielded
            assert session == mock_session

            # Complete the generator (simulating normal exit)
            with suppress(StopAsyncIteration):
                await gen.__anext__()

    @pytest.mark.asyncio
    async def test_get_db_rolls_back_on_exception(self) -> None:
        """Test get_db rolls back session when exception occurs."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        # Setup the async context manager behavior
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_factory = MagicMock(return_value=mock_session)

        with patch("feedback_service.database.AsyncSessionLocal", mock_factory):
            # Act & Assert
            gen: AsyncGenerator = get_db()
            session = await gen.__anext__()
            assert session == mock_session

            # Simulate exception by throwing into generator
            with pytest.raises(ValueError, match="Test error"):
                await gen.athrow(ValueError("Test error"))

            # Verify rollback and close were called by the generator's exception handling
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_always_closes_session(self) -> None:
        """Test get_db always closes session even on success."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()

        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_factory = MagicMock(return_value=mock_session)

        with patch("feedback_service.database.AsyncSessionLocal", mock_factory):
            # Act
            gen: AsyncGenerator = get_db()
            await gen.__anext__()

            # Complete the generator (normal exit)
            with suppress(StopAsyncIteration):
                await gen.__anext__()

            # Assert - close is called via __aexit__ of AsyncSessionLocal
            # which triggers session.close() in the finally block

    @pytest.mark.asyncio
    async def test_get_db_rolls_back_on_sqlalchemy_error(self) -> None:
        """Test get_db rolls back on SQLAlchemyError."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_factory = MagicMock(return_value=mock_session)

        with patch("feedback_service.database.AsyncSessionLocal", mock_factory):
            # Act & Assert
            gen: AsyncGenerator = get_db()
            await gen.__anext__()

            with pytest.raises(SQLAlchemyError, match="Database error"):
                await gen.athrow(SQLAlchemyError("Database error"))

            mock_session.rollback.assert_called_once()


class TestInitDb:
    """Tests for init_db function."""

    @pytest.mark.asyncio
    async def test_init_db_creates_schema_and_tables(self) -> None:
        """Test init_db creates schema and tables."""
        # Arrange
        mock_conn = AsyncMock()
        mock_conn.run_sync = AsyncMock()

        # Create proper async context manager for engine.begin()
        mock_begin_cm = MagicMock()
        mock_begin_cm.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin_cm.__aexit__ = AsyncMock(return_value=None)

        with patch("feedback_service.database.engine") as mock_engine:
            mock_engine.begin = MagicMock(return_value=mock_begin_cm)

            # Act
            from feedback_service.database import init_db
            await init_db()

            # Assert
            assert mock_conn.run_sync.call_count == 2  # Once for schema, once for tables
            mock_engine.begin.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_db_handles_connection_error(self) -> None:
        """Test init_db propagates connection errors."""
        # Arrange
        mock_begin_cm = MagicMock()
        mock_begin_cm.__aenter__ = AsyncMock(side_effect=SQLAlchemyError("Connection failed"))
        mock_begin_cm.__aexit__ = AsyncMock(return_value=None)

        with patch("feedback_service.database.engine") as mock_engine:
            mock_engine.begin = MagicMock(return_value=mock_begin_cm)

            # Act & Assert
            from feedback_service.database import init_db
            with pytest.raises(SQLAlchemyError, match="Connection failed"):
                await init_db()
