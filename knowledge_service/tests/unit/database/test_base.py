"""Tests for database module (database/base.py)."""

import contextlib
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.database import AsyncSessionLocal, Base, get_db, init_db
from knowledge_service.database.base import _create_search_indexes, engine, metadata_obj


class TestBaseMetadata:
    """Test Base metadata configuration."""

    def test_base_has_metadata(self) -> None:
        """Test that Base class has metadata attribute."""
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None

    def test_base_metadata_is_metadata_obj(self) -> None:
        """Test that Base.metadata is the metadata_obj instance."""
        assert Base.metadata is metadata_obj

    def test_metadata_has_schema(self) -> None:
        """Test that metadata has schema configured."""
        assert metadata_obj.schema is not None


class TestGetDB:
    """Test get_db async generator dependency."""

    @patch("knowledge_service.database.base.AsyncSessionLocal")
    async def test_get_db_yields_session(self, mock_session_local: Mock) -> None:
        """Test get_db yields a database session."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value = mock_session
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        async for session in get_db():
            assert session == mock_session

    @patch("knowledge_service.database.base.AsyncSessionLocal")
    async def test_get_db_commits_on_success(self, mock_session_local: Mock) -> None:
        """Test get_db commits session on successful iteration."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value = mock_session
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        async for session in get_db():
            pass  # Just iterate

        mock_session.commit.assert_called_once()
        mock_session.close.assert_awaited_once()

    @patch("knowledge_service.database.base.AsyncSessionLocal")
    async def test_get_db_rollbacks_on_exception(self, mock_session_local: Mock) -> None:
        """Test get_db rolls back session on exception thrown into generator."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value = mock_session
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        # Use direct generator interaction to properly test exception handling
        gen = get_db()
        session = await gen.__anext__()
        assert session == mock_session

        # Throw exception into the generator - this simulates what happens
        # when an exception occurs in a route using the dependency
        with contextlib.suppress(ValueError):
            await gen.athrow(ValueError("Test exception"))

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_awaited_once()

    @patch("knowledge_service.database.base.AsyncSessionLocal")
    async def test_get_db_always_closes(self, mock_session_local: Mock) -> None:
        """Test get_db always closes session even on exception."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value = mock_session
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        # Use direct generator interaction to properly test exception handling
        gen = get_db()
        session = await gen.__anext__()
        assert session == mock_session

        with pytest.raises(ValueError):
            await gen.athrow(ValueError("Test exception"))

        mock_session.close.assert_awaited_once()


class TestInitDB:
    """Test init_db function."""

    @patch("knowledge_service.database.base.engine")
    async def test_init_db_creates_schema(self, mock_engine: Mock) -> None:
        """Test init_db creates schema and tables."""
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=None)

        await init_db()

        # Verify connection was used
        mock_conn.run_sync.assert_called()

    @patch("knowledge_service.database.base.engine")
    async def test_init_db_creates_search_indexes(self, mock_engine: Mock) -> None:
        """Test init_db calls search index creation."""
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=None)

        await init_db()

        # Verify _create_search_indexes was called via run_sync
        calls = mock_conn.run_sync.call_args_list
        assert len(calls) >= 2  # At least create_all and search indexes


class TestCreateSearchIndexes:
    """Test _create_search_indexes function."""

    def test_create_search_indexes_executes_sql(self) -> None:
        """Test that _create_search_indexes executes expected SQL."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute = MagicMock()

        _create_search_indexes(mock_conn)

        # Verify SQL execution calls
        assert mock_conn.execute.call_count >= 8  # Multiple index creations + extension

        # Check that all calls are with text() wrapped SQL
        calls = mock_conn.execute.call_args_list
        for call in calls:
            assert call[0][0] is not None  # First argument should be the SQL text

    def test_create_search_indexes_creates_article_vector_index(self) -> None:
        """Test creation of article search vector index."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute = MagicMock()

        _create_search_indexes(mock_conn)

        calls = mock_conn.execute.call_args_list
        sql_texts = [str(call[0][0]) for call in calls]

        # Check for GIN index on search_vector
        assert any("idx_articles_search_vector" in sql for sql in sql_texts)

    def test_create_search_indexes_creates_status_index(self) -> None:
        """Test creation of article status index."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute = MagicMock()

        _create_search_indexes(mock_conn)

        calls = mock_conn.execute.call_args_list
        sql_texts = [str(call[0][0]) for call in calls]

        assert any("idx_articles_status" in sql for sql in sql_texts)

    def test_create_search_indexes_creates_department_index(self) -> None:
        """Test creation of article department_id index."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute = MagicMock()

        _create_search_indexes(mock_conn)

        calls = mock_conn.execute.call_args_list
        sql_texts = [str(call[0][0]) for call in calls]

        assert any("idx_articles_department_id" in sql for sql in sql_texts)

    def test_create_search_indexes_creates_category_index(self) -> None:
        """Test creation of article category_id index."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute = MagicMock()

        _create_search_indexes(mock_conn)

        calls = mock_conn.execute.call_args_list
        sql_texts = [str(call[0][0]) for call in calls]

        assert any("idx_articles_category_id" in sql for sql in sql_texts)

    def test_create_search_indexes_creates_category_parent_index(self) -> None:
        """Test creation of category parent_id index."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute = MagicMock()

        _create_search_indexes(mock_conn)

        calls = mock_conn.execute.call_args_list
        sql_texts = [str(call[0][0]) for call in calls]

        assert any("idx_categories_parent_id" in sql for sql in sql_texts)

    def test_create_search_indexes_creates_article_views_index(self) -> None:
        """Test creation of article views composite index."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute = MagicMock()

        _create_search_indexes(mock_conn)

        calls = mock_conn.execute.call_args_list
        sql_texts = [str(call[0][0]) for call in calls]

        assert any("idx_article_views_article_id_viewed_at" in sql for sql in sql_texts)

    def test_create_search_indexes_creates_pg_trgm_extension(self) -> None:
        """Test creation of pg_trgm extension."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute = MagicMock()

        _create_search_indexes(mock_conn)

        calls = mock_conn.execute.call_args_list
        sql_texts = [str(call[0][0]) for call in calls]

        assert any("pg_trgm" in sql for sql in sql_texts)

    def test_create_search_indexes_creates_title_trgm_index(self) -> None:
        """Test creation of title trigram index."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute = MagicMock()

        _create_search_indexes(mock_conn)

        calls = mock_conn.execute.call_args_list
        sql_texts = [str(call[0][0]) for call in calls]

        assert any("idx_articles_title_trgm" in sql for sql in sql_texts)

    def test_create_search_indexes_creates_tags_trgm_index(self) -> None:
        """Test creation of tags trigram index."""
        mock_conn = MagicMock(spec=Connection)
        mock_conn.execute = MagicMock()

        _create_search_indexes(mock_conn)

        calls = mock_conn.execute.call_args_list
        sql_texts = [str(call[0][0]) for call in calls]

        assert any("idx_tags_name_trgm" in sql for sql in sql_texts)


class TestEngineConfiguration:
    """Test engine configuration."""

    def test_engine_exists(self) -> None:
        """Test that engine is defined."""
        assert engine is not None

    def test_engine_is_async(self) -> None:
        """Test that engine is async type."""
        from sqlalchemy.ext.asyncio import AsyncEngine
        assert isinstance(engine, AsyncEngine)


class TestAsyncSessionLocal:
    """Test AsyncSessionLocal session factory."""

    def test_async_session_local_exists(self) -> None:
        """Test that AsyncSessionLocal is defined."""
        assert AsyncSessionLocal is not None

    def test_async_session_local_is_async_sessionmaker(self) -> None:
        """Test that AsyncSessionLocal is an async_sessionmaker."""
        from sqlalchemy.ext.asyncio import async_sessionmaker
        assert isinstance(AsyncSessionLocal, async_sessionmaker)
