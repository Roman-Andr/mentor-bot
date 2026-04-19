"""Unit tests for telegram_bot/bot.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent, Message

from telegram_bot.bot import global_error_handler, setup_bot
from telegram_bot.config import settings


class TestGlobalErrorHandler:
    """Test cases for global error handler."""

    @pytest.fixture
    def mock_error_event(self):
        """Create a mock error event."""
        event = MagicMock(spec=ErrorEvent)
        event.update = MagicMock()
        event.update.update_id = 12345
        event.exception = ValueError("Test error")
        return event

    @pytest.fixture
    def mock_error_event_with_message(self):
        """Create a mock error event with message."""
        event = MagicMock(spec=ErrorEvent)
        event.update = MagicMock()
        event.update.update_id = 12345
        event.update.callback_query = None
        event.update.message = MagicMock(spec=Message)
        event.exception = ValueError("Test error")
        return event

    @pytest.fixture
    def mock_error_event_with_callback(self):
        """Create a mock error event with callback."""
        event = MagicMock(spec=ErrorEvent)
        event.update = MagicMock()
        event.update.update_id = 12345
        event.update.message = None
        callback = MagicMock()
        callback.message = None  # Must be None to trigger callback path
        callback.answer = AsyncMock()
        event.update.callback_query = callback
        event.exception = ValueError("Test error")
        return event

    async def test_global_error_handler_with_message(self, mock_error_event_with_message):
        """Test error handler with message."""
        mock_error_event_with_message.update.message.answer = AsyncMock()

        result = await global_error_handler(mock_error_event_with_message)

        assert result is True
        mock_error_event_with_message.update.message.answer.assert_called_once()

    async def test_global_error_handler_with_callback(self, mock_error_event_with_callback):
        """Test error handler with callback."""
        result = await global_error_handler(mock_error_event_with_callback)

        assert result is True
        mock_error_event_with_callback.update.callback_query.answer.assert_called_once()

    async def test_global_error_handler_message_send_fails(self, mock_error_event_with_message):
        """Test error handler when message send fails."""
        mock_error_event_with_message.update.message.answer = AsyncMock(
            side_effect=Exception("Send failed")
        )

        with patch("telegram_bot.bot.logger") as mock_logger:
            result = await global_error_handler(mock_error_event_with_message)

        assert result is True
        mock_logger.warning.assert_called_once()

    async def test_global_error_handler_callback_send_fails(self, mock_error_event_with_callback):
        """Test error handler when callback answer fails."""
        # Set answer to fail
        mock_error_event_with_callback.update.callback_query.answer = AsyncMock(
            side_effect=Exception("Answer failed")
        )

        with patch("telegram_bot.bot.logger") as mock_logger:
            result = await global_error_handler(mock_error_event_with_callback)

        assert result is True
        mock_logger.warning.assert_called_once()

    async def test_global_error_handler_no_message_or_callback(self, mock_error_event):
        """Test error handler with no message or callback."""
        mock_error_event.update.message = None
        mock_error_event.update.callback_query = None

        with patch("telegram_bot.bot.logger") as mock_logger:
            result = await global_error_handler(mock_error_event)

        assert result is True
        mock_logger.error.assert_called_once()


class TestSetupBot:
    """Test cases for bot setup."""

    @pytest.fixture
    def mock_dispatcher(self):
        """Create a mock dispatcher."""
        dp = MagicMock(spec=Dispatcher)
        dp.update = MagicMock()
        dp.update.outer_middleware = MagicMock()
        dp.errors = MagicMock()
        dp.errors.register = MagicMock()
        dp.include_router = MagicMock()
        return dp

    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot."""
        return MagicMock(spec=Bot)

    def test_setup_bot_registers_middleware(self, mock_dispatcher, mock_bot):
        """Test that setup_bot registers middleware."""
        with patch.object(settings, "THROTTLING_ENABLED", False):
            result = setup_bot(mock_dispatcher, mock_bot)

        assert mock_dispatcher.update.outer_middleware.call_count >= 2
        assert result == mock_dispatcher

    def test_setup_bot_with_throttling_enabled(self, mock_dispatcher, mock_bot):
        """Test setup with throttling enabled."""
        with patch.object(settings, "THROTTLING_ENABLED", True):
            with patch("telegram_bot.bot.logger") as mock_logger:
                result = setup_bot(mock_dispatcher, mock_bot)

        assert result == mock_dispatcher
        mock_logger.info.assert_any_call("Throttling middleware enabled (Redis-based)")

    def test_setup_bot_with_throttling_disabled(self, mock_dispatcher, mock_bot):
        """Test setup with throttling disabled."""
        with patch.object(settings, "THROTTLING_ENABLED", False):
            with patch("telegram_bot.bot.logger") as mock_logger:
                result = setup_bot(mock_dispatcher, mock_bot)

        assert result == mock_dispatcher
        mock_logger.info.assert_any_call("Throttling middleware disabled")

    def test_setup_bot_registers_error_handler(self, mock_dispatcher, mock_bot):
        """Test that error handler is registered."""
        with patch.object(settings, "THROTTLING_ENABLED", False):
            setup_bot(mock_dispatcher, mock_bot)

        mock_dispatcher.errors.register.assert_called_once_with(global_error_handler)

    def test_setup_bot_includes_routers(self, mock_dispatcher, mock_bot):
        """Test that all routers are included."""
        with patch.object(settings, "THROTTLING_ENABLED", False):
            setup_bot(mock_dispatcher, mock_bot)

        assert mock_dispatcher.include_router.call_count >= 10
