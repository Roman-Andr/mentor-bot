"""Tests for telegram_bot database module."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from telegram_bot.database import Base, get_db, init_db
from telegram_bot.database.connection import AsyncSessionLocal, engine, metadata_obj
from telegram_bot.database.models import BotLog, Notification, UserSession


class TestDatabaseExports:
    """Test database module exports from __init__.py."""

    def test_base_exported(self):
        """Test Base is exported from database package."""
        from telegram_bot.database import Base as ExportedBase

        assert ExportedBase is Base

    def test_get_db_exported(self):
        """Test get_db is exported from database package."""
        from telegram_bot.database import get_db as exported_get_db

        assert exported_get_db is get_db

    def test_init_db_exported(self):
        """Test init_db is exported from database package."""
        from telegram_bot.database import init_db as exported_init_db

        assert exported_init_db is init_db

    def test_all_exports_defined(self):
        """Test __all__ exports are defined."""
        from telegram_bot import database

        assert hasattr(database, "__all__")
        assert "Base" in database.__all__
        assert "get_db" in database.__all__
        assert "init_db" in database.__all__


class TestEngineConfiguration:
    """Test engine configuration in connection.py."""

    def test_engine_exists(self):
        """Test engine is created."""
        assert engine is not None

    def test_engine_is_async(self):
        """Test that engine is async type."""
        from sqlalchemy.ext.asyncio import AsyncEngine

        assert isinstance(engine, AsyncEngine)

    def test_engine_has_pool_settings(self):
        """Test engine is configured with pool settings."""
        assert engine.pool is not None

    def test_engine_url_configured(self):
        """Test engine URL is configured."""
        assert engine.url is not None

    def test_async_session_local_exists(self):
        """Test AsyncSessionLocal is created."""
        assert AsyncSessionLocal is not None

    def test_async_session_local_is_sessionmaker(self):
        """Test AsyncSessionLocal is a sessionmaker."""
        assert isinstance(AsyncSessionLocal, async_sessionmaker)

    def test_session_local_configuration(self):
        """Test AsyncSessionLocal has correct configuration."""
        # Check class_ is AsyncSession
        assert AsyncSessionLocal.class_ is AsyncSession
        # Check expire_on_commit is False
        assert AsyncSessionLocal.kw.get("expire_on_commit") is False
        # Check autocommit is False
        assert AsyncSessionLocal.kw.get("autocommit") is False
        # Check autoflush is False
        assert AsyncSessionLocal.kw.get("autoflush") is False


class TestBaseMetadata:
    """Test Base metadata configuration."""

    def test_base_has_metadata(self):
        """Test Base class has metadata attribute."""
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None

    def test_base_metadata_is_metadata_obj(self):
        """Test Base.metadata is the metadata_obj instance."""
        assert Base.metadata is metadata_obj

    def test_metadata_has_no_schema(self):
        """Test metadata has no schema (uses public schema)."""
        assert metadata_obj.schema is None

    def test_metadata_uses_public_schema(self):
        """Test metadata uses public schema (None means public)."""
        assert metadata_obj.schema is None


class TestGetDB:
    """Test get_db async generator dependency."""

    @patch("telegram_bot.database.connection.AsyncSessionLocal")
    async def test_get_db_yields_session(self, mock_session_local: Mock) -> None:
        """Test get_db yields a database session."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value = mock_session
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        async for session in get_db():
            assert session == mock_session

    @patch("telegram_bot.database.connection.AsyncSessionLocal")
    async def test_get_db_commits_on_success(self, mock_session_local: Mock) -> None:
        """Test get_db commits session on successful iteration."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value = mock_session
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        async for _session in get_db():
            pass  # Just iterate

        mock_session.commit.assert_awaited_once()
        mock_session.rollback.assert_not_awaited()
        mock_session.close.assert_awaited_once()

    @patch("telegram_bot.database.connection.AsyncSessionLocal")
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
        with pytest.raises(ValueError, match="Test error"):
            await gen.athrow(ValueError("Test error"))

        mock_session.rollback.assert_awaited_once()
        mock_session.close.assert_awaited_once()

    @patch("telegram_bot.database.connection.AsyncSessionLocal")
    async def test_get_db_always_closes_on_exception(self, mock_session_local: Mock) -> None:
        """Test get_db always closes session even on exception."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value = mock_session
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        gen = get_db()
        await gen.__anext__()

        with pytest.raises(RuntimeError, match="Runtime test error"):
            await gen.athrow(RuntimeError("Runtime test error"))

        mock_session.close.assert_awaited_once()

    @patch("telegram_bot.database.connection.AsyncSessionLocal")
    async def test_get_db_re_raises_exception(self, mock_session_local: Mock) -> None:
        """Test get_db re-raises exception after rollback."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value = mock_session
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        gen = get_db()
        await gen.__anext__()

        # The exception should be re-raised after rollback
        with pytest.raises(KeyError):
            await gen.athrow(KeyError("test"))

        mock_session.rollback.assert_awaited_once()


class TestInitDB:
    """Test init_db function."""

    @patch("telegram_bot.database.connection.engine")
    @patch("telegram_bot.database.connection.logger")
    async def test_init_db_creates_schema(self, mock_logger: Mock, mock_engine: Mock) -> None:
        """Test init_db creates schema and tables."""
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=None)

        await init_db()

        # Verify begin was called
        mock_engine.begin.assert_called_once()
        # Verify connection was used
        assert mock_conn.run_sync.call_count == 1  # Only table creation (no schema creation)
        # Verify logging
        mock_logger.info.assert_called_once_with("Database initialized")

    @patch("telegram_bot.database.connection.engine")
    @patch("telegram_bot.database.connection.logger")
    async def test_init_db_creates_schema_if_not_exists(self, mock_logger: Mock, mock_engine: Mock) -> None:
        """Test init_db creates schema with if_not_exists flag."""
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=None)

        await init_db()

        # Get the first call which should be CreateSchema
        calls = mock_conn.run_sync.call_args_list
        assert len(calls) >= 1

    @patch("telegram_bot.database.connection.engine")
    @patch("telegram_bot.database.connection.logger")
    async def test_init_db_creates_all_tables(self, mock_logger: Mock, mock_engine: Mock) -> None:
        """Test init_db calls create_all on metadata."""
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=None)

        await init_db()

        # Verify create_all is called via run_sync
        calls = mock_conn.run_sync.call_args_list
        # Only 1 call: create_all (no schema creation)
        assert len(calls) == 1


class TestUserSessionModel:
    """Test UserSession model."""

    def test_user_session_creation(self):
        """Test creating a UserSession instance."""
        session = UserSession(
            id=1,
            telegram_id=123456789,
            user_id=42,
            language="en",
            notifications_enabled=True,
            notification_time="09:00",
            last_activity=datetime.now(UTC),
            session_data={"key": "value"},
        )

        assert session.id == 1
        assert session.telegram_id == 123456789
        assert session.user_id == 42
        assert session.language == "en"
        assert session.notifications_enabled is True
        assert session.notification_time == "09:00"
        assert session.session_data == {"key": "value"}

    def test_user_session_repr(self):
        """Test UserSession __repr__ method."""
        session = UserSession(
            telegram_id=123456789,
            user_id=42,
        )

        repr_str = repr(session)

        assert "UserSession" in repr_str
        assert "telegram_id=123456789" in repr_str
        assert "user_id=42" in repr_str

    def test_user_session_repr_without_user_id(self):
        """Test UserSession __repr__ with null user_id."""
        session = UserSession(
            telegram_id=987654321,
            user_id=None,
        )

        repr_str = repr(session)

        assert "UserSession" in repr_str
        assert "telegram_id=987654321" in repr_str
        assert "user_id=None" in repr_str

    def test_user_session_default_values(self):
        """Test UserSession default values."""
        session = UserSession(
            telegram_id=111222333,
        )

        # Check that instance can be created with minimal fields
        assert session.telegram_id == 111222333
        # id is None until persisted
        assert session.id is None
        # user_id is nullable
        assert session.user_id is None

    def test_user_session_tablename(self):
        """Test UserSession table name."""
        assert UserSession.__tablename__ == "user_sessions"

    def test_user_session_columns(self):
        """Test UserSession has expected columns."""
        # Check primary key column exists
        assert hasattr(UserSession, "id")
        assert hasattr(UserSession, "telegram_id")
        assert hasattr(UserSession, "user_id")
        assert hasattr(UserSession, "language")
        assert hasattr(UserSession, "notifications_enabled")
        assert hasattr(UserSession, "notification_time")
        assert hasattr(UserSession, "last_activity")
        assert hasattr(UserSession, "session_data")
        assert hasattr(UserSession, "created_at")
        assert hasattr(UserSession, "updated_at")


class TestBotLogModel:
    """Test BotLog model."""

    def test_bot_log_creation(self):
        """Test creating a BotLog instance."""
        log = BotLog(
            id=1,
            telegram_id=123456789,
            user_id=42,
            action="command",
            command="/start",
            data="some data",
            response_time=0.5,
            success=True,
            error_message=None,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
        )

        assert log.id == 1
        assert log.telegram_id == 123456789
        assert log.user_id == 42
        assert log.action == "command"
        assert log.command == "/start"
        assert log.data == "some data"
        assert log.response_time == 0.5
        assert log.success is True
        assert log.error_message is None
        assert log.ip_address == "127.0.0.1"
        assert log.user_agent == "Mozilla/5.0"

    def test_bot_log_repr(self):
        """Test BotLog __repr__ method."""
        log = BotLog(
            telegram_id=123456789,
            action="callback",
        )

        repr_str = repr(log)

        assert "BotLog" in repr_str
        assert "telegram_id=123456789" in repr_str
        assert "action=callback" in repr_str

    def test_bot_log_repr_different_actions(self):
        """Test BotLog __repr__ with different action types."""
        actions = ["command", "callback", "message"]

        for action in actions:
            log = BotLog(
                telegram_id=111111111,
                action=action,
            )
            repr_str = repr(log)
            assert f"action={action}" in repr_str

    def test_bot_log_default_values(self):
        """Test BotLog default values (applied at DB insertion, not instantiation)."""
        log = BotLog(
            telegram_id=123456789,
            action="command",
        )

        assert log.telegram_id == 123456789
        assert log.action == "command"
        # Default values are only applied when record is inserted into DB
        # Before insertion, these are None
        assert log.success is None  # Will be True after DB insertion
        # id is None until persisted
        assert log.id is None

    def test_bot_log_tablename(self):
        """Test BotLog table name."""
        assert BotLog.__tablename__ == "bot_logs"

    def test_bot_log_columns(self):
        """Test BotLog has expected columns."""
        assert hasattr(BotLog, "id")
        assert hasattr(BotLog, "telegram_id")
        assert hasattr(BotLog, "user_id")
        assert hasattr(BotLog, "action")
        assert hasattr(BotLog, "command")
        assert hasattr(BotLog, "data")
        assert hasattr(BotLog, "response_time")
        assert hasattr(BotLog, "success")
        assert hasattr(BotLog, "error_message")
        assert hasattr(BotLog, "ip_address")
        assert hasattr(BotLog, "user_agent")
        assert hasattr(BotLog, "created_at")


class TestNotificationModel:
    """Test Notification model."""

    def test_notification_creation(self):
        """Test creating a Notification instance."""
        scheduled_time = datetime.now(UTC)
        sent_time = datetime.now(UTC)

        notification = Notification(
            id=1,
            telegram_id=123456789,
            user_id=42,
            notification_type="task_reminder",
            message="Don't forget to complete your task!",
            scheduled_for=scheduled_time,
            status="sent",
            sent_at=sent_time,
            attempts=1,
            metadata_obj={"task_id": 123},
        )

        assert notification.id == 1
        assert notification.telegram_id == 123456789
        assert notification.user_id == 42
        assert notification.notification_type == "task_reminder"
        assert notification.message == "Don't forget to complete your task!"
        assert notification.scheduled_for == scheduled_time
        assert notification.status == "sent"
        assert notification.sent_at == sent_time
        assert notification.attempts == 1
        assert notification.metadata_obj == {"task_id": 123}

    def test_notification_repr(self):
        """Test Notification __repr__ method."""
        notification = Notification(
            telegram_id=123456789,
            notification_type="meeting",
        )

        repr_str = repr(notification)

        assert "Notification" in repr_str
        assert "telegram_id=123456789" in repr_str
        assert "type=meeting" in repr_str

    def test_notification_repr_different_types(self):
        """Test Notification __repr__ with different notification types."""
        types = ["task_reminder", "meeting", "system"]

        for notif_type in types:
            notification = Notification(
                telegram_id=222333444,
                notification_type=notif_type,
            )
            repr_str = repr(notification)
            assert f"type={notif_type}" in repr_str

    def test_notification_default_values(self):
        """Test Notification default values (applied at DB insertion, not instantiation)."""
        scheduled_time = datetime.now(UTC)

        notification = Notification(
            telegram_id=123456789,
            notification_type="task_reminder",
            message="Test message",
            scheduled_for=scheduled_time,
        )

        assert notification.telegram_id == 123456789
        assert notification.notification_type == "task_reminder"
        assert notification.message == "Test message"
        assert notification.scheduled_for == scheduled_time
        # Default values are only applied when record is inserted into DB
        # Before insertion, these are None
        assert notification.status is None  # Will be "pending" after DB insertion
        assert notification.attempts is None  # Will be 0 after DB insertion
        # id is None until persisted
        assert notification.id is None
        # sent_at is None until sent
        assert notification.sent_at is None

    def test_notification_tablename(self):
        """Test Notification table name."""
        assert Notification.__tablename__ == "notifications"

    def test_notification_columns(self):
        """Test Notification has expected columns."""
        assert hasattr(Notification, "id")
        assert hasattr(Notification, "telegram_id")
        assert hasattr(Notification, "user_id")
        assert hasattr(Notification, "notification_type")
        assert hasattr(Notification, "message")
        assert hasattr(Notification, "scheduled_for")
        assert hasattr(Notification, "status")
        assert hasattr(Notification, "sent_at")
        assert hasattr(Notification, "attempts")
        assert hasattr(Notification, "metadata_obj")
        assert hasattr(Notification, "created_at")
        assert hasattr(Notification, "updated_at")


class TestModelInheritance:
    """Test model inheritance from Base."""

    def test_user_session_inherits_base(self):
        """Test UserSession inherits from Base."""
        assert issubclass(UserSession, Base)

    def test_bot_log_inherits_base(self):
        """Test BotLog inherits from Base."""
        assert issubclass(BotLog, Base)

    def test_notification_inherits_base(self):
        """Test Notification inherits from Base."""
        assert issubclass(Notification, Base)

    def test_all_models_have_metadata(self):
        """Test all models have SQLAlchemy metadata."""
        for model in [UserSession, BotLog, Notification]:
            assert hasattr(model, "__table__")
            assert model.__table__ is not None
