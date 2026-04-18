"""Unit tests for telegram_bot/handlers/checklists.py."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import CallbackQuery, Message

from telegram_bot.handlers.checklists import (
    _respond_with_auth_error,
    noop_callback,
)


class TestNoopCallback:
    """Test cases for noop_callback handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.data = "noop"

    async def test_noop_callback(self):
        """Test that noop callback simply answers."""
        await noop_callback(self.mock_callback, locale="en")

        self.mock_callback.answer.assert_called_once()


class TestRespondWithAuthError:
    """Test cases for _respond_with_auth_error helper."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()

        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()

    async def test_auth_error_callback(self):
        """Test auth error response for callback."""
        await _respond_with_auth_error(self.mock_callback, locale="en")

        self.mock_callback.answer.assert_called_once()

    async def test_auth_error_message(self):
        """Test auth error response for message."""
        await _respond_with_auth_error(self.mock_message, locale="en")

        self.mock_message.answer.assert_called_once()
