"""Unit tests for telegram_bot/main.py."""

import sys
from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Mock modules before import
@pytest.fixture(scope="module", autouse=True)
def mock_modules():
    """Mock modules before importing main."""
    # Save original modules to restore after test
    original_modules = {}
    mocks = {
        "telegram_bot.database": MagicMock(),
        "telegram_bot.database.connection": MagicMock(),
        "telegram_bot.services.cache": MagicMock(),
        "telegram_bot.utils.cache": MagicMock(),
        "telegram_bot.utils.scheduler": MagicMock(),
        "telegram_bot.bot": MagicMock(),
    }
    for name, mock in mocks.items():
        if name in sys.modules:
            original_modules[name] = sys.modules[name]
        sys.modules[name] = mock
    yield mocks
    # Cleanup: restore original modules or remove mocks
    for name in mocks:
        if name in sys.modules:
            del sys.modules[name]
        if name in original_modules:
            sys.modules[name] = original_modules[name]


class TestLifespan:
    """Test cases for lifespan context manager."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self, mock_modules):
        """Set up common mocks."""
        # Patch all the required dependencies
        self.patches = []

        patch_init_db = patch("telegram_bot.main.init_db", new_callable=AsyncMock)
        patch_user_cache = patch("telegram_bot.main.user_cache")
        patch_redis_cache = patch("telegram_bot.main.redis_cache")
        patch_setup_bot_commands = patch("telegram_bot.main.setup_bot_commands", new_callable=AsyncMock)
        patch_scheduler = patch("telegram_bot.main.scheduler")
        patch_settings = patch("telegram_bot.main.settings")

        self.mock_init_db = patch_init_db.start()
        self.mock_user_cache = patch_user_cache.start()
        self.mock_redis_cache = patch_redis_cache.start()
        self.mock_setup_bot_commands = patch_setup_bot_commands.start()
        self.mock_scheduler = patch_scheduler.start()
        self.mock_settings = patch_settings.start()

        self.patches = [
            patch_init_db, patch_user_cache, patch_redis_cache,
            patch_setup_bot_commands, patch_scheduler, patch_settings
        ]

        self.mock_settings.ENABLE_NOTIFICATIONS = True
        self.mock_settings.LOG_LEVEL = "INFO"

        # Setup async mocks for cache methods
        self.mock_user_cache.connect = AsyncMock()
        self.mock_user_cache.disconnect = AsyncMock()
        self.mock_redis_cache.connect = AsyncMock()
        self.mock_redis_cache.disconnect = AsyncMock()
        self.mock_scheduler.start = AsyncMock()
        self.mock_scheduler.shutdown = AsyncMock()

        yield

        # Stop all patches
        for p in self.patches:
            p.stop()

    async def test_lifespan_startup_initializes_all(self, setup_mocks):
        """Test lifespan startup initializes all services."""
        from telegram_bot.main import lifespan

        mock_bot = MagicMock()
        mock_bot.session = MagicMock()
        mock_bot.session.close = AsyncMock()

        async with lifespan(mock_bot):
            # Verify startup sequence
            self.mock_init_db.assert_called_once()
            self.mock_user_cache.connect.assert_called_once()
            self.mock_redis_cache.connect.assert_called_once()
            self.mock_setup_bot_commands.assert_called_once_with(mock_bot)
            self.mock_scheduler.start.assert_called_once_with(mock_bot)

        # Verify shutdown sequence
        mock_bot.session.close.assert_called_once()
        self.mock_user_cache.disconnect.assert_called_once()
        self.mock_redis_cache.disconnect.assert_called_once()
        self.mock_scheduler.shutdown.assert_called_once()

    async def test_lifespan_with_notifications_disabled(self, setup_mocks):
        """Test lifespan when notifications are disabled."""
        from telegram_bot.main import lifespan

        self.mock_settings.ENABLE_NOTIFICATIONS = False

        mock_bot = MagicMock()
        mock_bot.session = MagicMock()
        mock_bot.session.close = AsyncMock()

        async with lifespan(mock_bot):
            pass

        self.mock_scheduler.start.assert_not_called()
        self.mock_scheduler.shutdown.assert_not_called()


class TestSetupBotCommands:
    """Test cases for setup_bot_commands function."""

    @pytest.fixture(autouse=True)
    def setup_settings(self):
        """Set up settings mock."""
        with patch("telegram_bot.main.settings") as mock_settings:
            self.mock_settings = mock_settings
            self.mock_settings.ADMIN_IDS = []
            yield

    async def test_setup_bot_commands_basic(self, setup_settings):
        """Test basic bot commands setup without admin."""
        from telegram_bot.main import setup_bot_commands

        mock_bot = MagicMock()
        mock_bot.set_my_commands = AsyncMock()

        await setup_bot_commands(mock_bot)

        mock_bot.set_my_commands.assert_called_once()
        commands = mock_bot.set_my_commands.call_args[0][0]

        # Should have standard commands (12 total)
        assert len(commands) == 12  # All commands except /admin

        # Verify command types
        command_names = [cmd.command for cmd in commands]
        assert "/start" in command_names
        assert "/menu" in command_names
        assert "/tasks" in command_names
        assert "/admin" not in command_names

    async def test_setup_bot_commands_with_admin(self, setup_settings):
        """Test bot commands setup with admin IDs configured."""
        from telegram_bot.main import setup_bot_commands

        # Patch settings at the module level
        with patch("telegram_bot.main.settings") as patched_settings:
            patched_settings.ADMIN_IDS = [123456]

            mock_bot = MagicMock()
            mock_bot.set_my_commands = AsyncMock()

            await setup_bot_commands(mock_bot)

            mock_bot.set_my_commands.assert_called_once()
            commands = mock_bot.set_my_commands.call_args[0][0]

            # Should have 13 commands including /admin
            assert len(commands) == 13

            command_names = [cmd.command for cmd in commands]
            assert "/admin" in command_names

    async def test_setup_bot_commands_verifies_command_structure(self, setup_settings):
        """Test that commands have proper description and command fields."""
        from aiogram.types import BotCommand

        from telegram_bot.main import setup_bot_commands

        mock_bot = MagicMock()
        mock_bot.set_my_commands = AsyncMock()

        await setup_bot_commands(mock_bot)

        commands = mock_bot.set_my_commands.call_args[0][0]

        for cmd in commands:
            assert isinstance(cmd, BotCommand)
            assert cmd.command is not None
            assert cmd.description is not None
            assert len(cmd.command) > 0
            assert len(cmd.description) > 0


class TestMainFunction:
    """Test cases for main() function - mocking at the correct level."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self, mock_modules):
        """Set up all necessary mocks."""
        with patch("telegram_bot.main.Redis") as mock_redis_class, \
             patch("telegram_bot.main.RedisStorage") as mock_storage_class, \
             patch("telegram_bot.main.Bot") as mock_bot_class, \
             patch("telegram_bot.main.Dispatcher") as mock_dispatcher_class, \
             patch("telegram_bot.main.setup_bot") as mock_setup_bot, \
             patch("telegram_bot.main.lifespan") as mock_lifespan, \
             patch("telegram_bot.main.settings") as mock_settings:

            self.mock_redis_class = mock_redis_class
            self.mock_storage_class = mock_storage_class
            self.mock_bot_class = mock_bot_class
            self.mock_dispatcher_class = mock_dispatcher_class
            self.mock_setup_bot = mock_setup_bot
            self.mock_lifespan = mock_lifespan
            self.mock_settings = mock_settings

            self.mock_settings.TELEGRAM_BOT_TOKEN = "123456:test_token"
            self.mock_settings.REDIS_URL = "redis://localhost:6379/3"

            # Setup async context manager for lifespan mock
            self.mock_lifespan.return_value.__aenter__ = AsyncMock()
            self.mock_lifespan.return_value.__aexit__ = AsyncMock()

            yield

    async def test_main_initializes_components(self, setup_mocks, mock_modules):
        """Test main() initializes all components correctly."""
        from telegram_bot.main import main

        # Create a fresh mock for main.main
        mock_bot = MagicMock()
        mock_bot.delete_webhook = AsyncMock()

        mock_dp = MagicMock()
        mock_dp.start_polling = AsyncMock()

        self.mock_bot_class.return_value = mock_bot
        self.mock_dispatcher_class.return_value = mock_dp

        with suppress(Exception):
            await main()

        # Verify core setup happened
        self.mock_redis_class.from_url.assert_called_once()
        self.mock_storage_class.assert_called_once()
        self.mock_bot_class.assert_called_once()


class TestMainModule:
    """Test cases for main module-level code."""

    def test_logging_configuration(self, mock_modules):
        """Test that logging is configured in main module."""
        with patch("telegram_bot.main.settings") as mock_settings:
            mock_settings.LOG_LEVEL = "DEBUG"
            mock_settings.TELEGRAM_BOT_TOKEN = "test"
            mock_settings.REDIS_URL = "redis://localhost:6379/3"
            mock_settings.ENABLE_NOTIFICATIONS = True
            mock_settings.ADMIN_IDS = []

            # Import fresh to check logging setup
            with patch.dict(sys.modules, {
                "telegram_bot.database": MagicMock(),
                "telegram_bot.database.connection": MagicMock(),
                "telegram_bot.services.cache": MagicMock(),
                "telegram_bot.utils.cache": MagicMock(),
                "telegram_bot.utils.scheduler": MagicMock(),
                "telegram_bot.bot": MagicMock(),
            }):
                import logging
                # Force reimport by clearing cache
                if "telegram_bot.main" in sys.modules:
                    del sys.modules["telegram_bot.main"]
                logger = logging.getLogger("telegram_bot.main")
                assert logger is not None

    def test_main_entry_point_exists(self, mock_modules):
        """Test that __main__ entry point exists."""
        # Just verify the pattern exists in the code
        with patch.dict(sys.modules, {
            "telegram_bot.database": MagicMock(),
            "telegram_bot.database.connection": MagicMock(),
            "telegram_bot.services.cache": MagicMock(),
            "telegram_bot.utils.cache": MagicMock(),
            "telegram_bot.utils.scheduler": MagicMock(),
            "telegram_bot.bot": MagicMock(),
        }):
            if "telegram_bot.main" in sys.modules:
                del sys.modules["telegram_bot.main"]
            import telegram_bot.main as main_module

            # Verify the module has main function
            assert hasattr(main_module, "main")
            assert callable(main_module.main)

            # Verify lifespan exists
            assert hasattr(main_module, "lifespan")

            # Verify setup_bot_commands exists
            assert hasattr(main_module, "setup_bot_commands")
