"""Tests for database module."""

from types import TracebackType  # noqa: TC003
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from checklists_service.database import base as database_base
from checklists_service.database.base import AsyncSessionLocal, engine, get_db, init_db


class TestAsyncSessionLocal:
    """Test AsyncSessionLocal configuration."""

    def test_async_session_local_exists(self):
        """Test AsyncSessionLocal is created."""
        assert AsyncSessionLocal is not None

    def test_async_session_local_is_sessionmaker(self):
        """Test AsyncSessionLocal is a sessionmaker."""
        assert isinstance(AsyncSessionLocal, async_sessionmaker)


class TestEngineConfiguration:
    """Test engine configuration."""

    def test_engine_exists(self):
        """Test engine is created."""
        assert engine is not None

    def test_engine_has_pool_settings(self):
        """Test engine is configured with pool settings."""
        # Check engine has pool configuration
        assert engine.pool is not None

    def test_engine_configuration(self):
        """Test engine has correct configuration from settings."""
        assert engine.url is not None
        assert engine.pool is not None

    def test_get_engine_from_settings(self):
        """Test engine is created with settings configuration."""
        with patch("checklists_service.database.base.settings") as mock_settings:
            mock_settings.DATABASE_URL = "postgresql+asyncpg://test:test@localhost/test"
            mock_settings.DEBUG = True
            mock_settings.DATABASE_POOL_SIZE = 5
            mock_settings.DATABASE_MAX_OVERFLOW = 10

            # Import fresh to get engine with mocked settings
            import importlib  # noqa: PLC0415
            from checklists_service.database import base  # noqa: PLC0415
            importlib.reload(base)

            assert base.engine is not None
            assert base.engine.pool is not None


class TestInitDb:
    """Test init_db function."""

    async def test_init_db_creates_schema_and_tables(self):
        """Test init_db creates schema and tables."""
        mock_conn = MagicMock()
        mock_conn.run_sync = AsyncMock()

        # Create async context manager mock for engine.begin()
        class MockBeginContextManager:
            async def __aenter__(self) -> MagicMock:
                return mock_conn
            async def __aexit__(
                self,
                exc_type: type[BaseException] | None,
                exc: BaseException | None,
                tb: TracebackType | None,
            ) -> bool:
                return False

        # Create mock engine with begin() method
        mock_engine = MagicMock()
        mock_engine.begin = MagicMock(return_value=MockBeginContextManager())

        # Patch the engine in the database.base module
        import checklists_service.database.base as db_base  # noqa: PLC0415

        original_engine = db_base.engine
        db_base.engine = mock_engine
        try:
            await init_db()
            # Verify run_sync was called for schema creation and table creation
            assert mock_conn.run_sync.call_count == 2
        finally:
            db_base.engine = original_engine


class TestBaseModel:
    """Test Base model configuration."""

    def test_base_has_metadata(self):
        """Test Base model has metadata."""
        assert database_base.Base.metadata is not None

    def test_base_metadata_has_schema(self):
        """Test Base metadata has schema configured."""
        assert database_base.Base.metadata.schema == "checklists"


class TestGetDB:
    """Test get_db dependency function."""

    async def test_get_db_success(self):
        """Test database session creation and cleanup."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        class MockSessionLocal:
            async def __aenter__(self):
                return mock_session
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False

        with patch("checklists_service.database.base.AsyncSessionLocal", MockSessionLocal):
            gen = get_db()
            session = await gen.__anext__()

            assert session == mock_session

            # Complete the generator (simulate end of request)
            try:
                await gen.__anext__()
            except StopAsyncIteration:
                pass

            mock_session.commit.assert_awaited_once()
            mock_session.close.assert_awaited_once()

    async def test_get_db_rollback_on_error(self):
        """Test database session rolls back on error."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        class MockSessionLocal:
            async def __aenter__(self):
                return mock_session
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False

        with patch("checklists_service.database.base.AsyncSessionLocal", MockSessionLocal):
            gen = get_db()
            await gen.__anext__()

            # Simulate an exception during request
            try:
                await gen.athrow(ValueError("Test error"))
            except ValueError:
                pass

            mock_session.rollback.assert_awaited_once()
            mock_session.close.assert_awaited_once()
