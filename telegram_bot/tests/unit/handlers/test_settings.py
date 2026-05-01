"""Unit tests for telegram_bot/handlers/settings.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram_bot.handlers.settings import (
    cb_notifications_menu,
    cb_settings_menu,
    cb_toggle_email,
    cb_toggle_telegram,
    cmd_settings,
)


class TestSettingsHandlers:
    """Test cases for settings handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 123456
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query."""
        cb = MagicMock()
        cb.id = "callback_123"
        cb.from_user = MagicMock()
        cb.from_user.id = 123456
        cb.data = "settings_menu"
        cb.answer = AsyncMock()
        cb.message = MagicMock()
        cb.message.chat = MagicMock()
        cb.message.chat.id = 123456
        cb.message.edit_text = AsyncMock()
        return cb

    @pytest.fixture
    def mock_callback_no_message(self):
        """Create a mock callback query with no message."""
        cb = MagicMock()
        cb.id = "callback_123"
        cb.from_user = MagicMock()
        cb.from_user.id = 123456
        cb.data = "settings_menu"
        cb.answer = AsyncMock()
        cb.message = None
        return cb

    async def test_cmd_settings(self, mock_message):
        """Test settings command."""
        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences", new_callable=AsyncMock, return_value=None
        ):
            with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await cmd_settings(mock_message, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "parse_mode" in call_args.kwargs
        assert call_args.kwargs["parse_mode"] == "Markdown"

    async def test_cmd_settings_russian(self, mock_message):
        """Test settings command with Russian locale."""
        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences", new_callable=AsyncMock, return_value=None
        ):
            with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await cmd_settings(mock_message, auth_token="test_token", user={"id": 123456}, locale="ru")

        mock_message.answer.assert_called_once()

    async def test_cb_settings_menu(self, mock_callback):
        """Test settings menu callback."""
        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences", new_callable=AsyncMock, return_value=None
        ):
            with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await cb_settings_menu(mock_callback, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()
        call_args = mock_callback.message.edit_text.call_args
        assert "parse_mode" in call_args.kwargs
        assert call_args.kwargs["parse_mode"] == "Markdown"

    async def test_cb_settings_menu_no_message(self, mock_callback_no_message):
        """Test settings menu callback with no message."""
        with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cb_settings_menu(mock_callback_no_message, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_callback_no_message.answer.assert_called_once()

    async def test_cmd_settings_english_text(self, mock_message):
        """Test settings command triggered by English text."""
        mock_message.text = "Settings"

        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences", new_callable=AsyncMock, return_value=None
        ):
            with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await cmd_settings(mock_message, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_message.answer.assert_called_once()

    async def test_cmd_settings_russian_text(self, mock_message):
        """Test settings command triggered by Russian text."""
        mock_message.text = "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438"

        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences", new_callable=AsyncMock, return_value=None
        ):
            with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await cmd_settings(mock_message, auth_token="test_token", user={"id": 123456}, locale="ru")

        mock_message.answer.assert_called_once()

    async def test_cmd_settings_with_preferences(self, mock_message):
        """Test settings command with user preferences returned."""
        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences",
            new_callable=AsyncMock,
            return_value={"notification_telegram_enabled": False, "notification_email_enabled": True},
        ):
            with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await cmd_settings(mock_message, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_message.answer.assert_called_once()
        mock_kb.assert_called_once_with(locale="en", telegram_enabled=False, email_enabled=True)

    async def test_cb_settings_menu_with_preferences(self, mock_callback):
        """Test settings menu callback with user preferences returned."""
        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences",
            new_callable=AsyncMock,
            return_value={"notification_telegram_enabled": True, "notification_email_enabled": False},
        ):
            with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await cb_settings_menu(mock_callback, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_kb.assert_called_once_with(locale="en", telegram_enabled=True, email_enabled=False)

    async def test_cb_notifications_menu(self, mock_callback):
        """Test notifications menu callback."""
        mock_callback.data = "notifications_menu"
        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences", new_callable=AsyncMock, return_value=None
        ):
            with patch("telegram_bot.handlers.settings.get_notifications_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await cb_notifications_menu(mock_callback, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()
        mock_kb.assert_called_once_with(locale="en", telegram_enabled=True, email_enabled=True)

    async def test_cb_notifications_menu_with_preferences(self, mock_callback):
        """Test notifications menu callback with user preferences."""
        mock_callback.data = "notifications_menu"
        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences",
            new_callable=AsyncMock,
            return_value={"notification_telegram_enabled": False, "notification_email_enabled": True},
        ):
            with patch("telegram_bot.handlers.settings.get_notifications_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await cb_notifications_menu(mock_callback, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_kb.assert_called_once_with(locale="en", telegram_enabled=False, email_enabled=True)

    async def test_cb_notifications_menu_no_message(self, mock_callback_no_message):
        """Test notifications menu callback with no message."""
        mock_callback_no_message.data = "notifications_menu"
        with patch("telegram_bot.handlers.settings.get_notifications_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cb_notifications_menu(
                mock_callback_no_message, auth_token="test_token", user={"id": 123456}, locale="en"
            )

        mock_callback_no_message.answer.assert_called_once()

    async def test_cb_toggle_telegram(self, mock_callback):
        """Test toggle Telegram notifications callback."""
        mock_callback.data = "toggle_telegram"
        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences",
            new_callable=AsyncMock,
            return_value={"notification_telegram_enabled": True, "notification_email_enabled": True},
        ):
            with patch("telegram_bot.handlers.settings.auth_client.update_user_preferences", new_callable=AsyncMock):
                with patch("telegram_bot.handlers.settings.get_notifications_keyboard") as mock_kb:
                    mock_kb.return_value = MagicMock()

                    await cb_toggle_telegram(mock_callback, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()
        mock_kb.assert_called_once_with(locale="en", telegram_enabled=False, email_enabled=True)

    async def test_cb_toggle_telegram_no_message(self, mock_callback_no_message):
        """Test toggle Telegram callback with no message."""
        mock_callback_no_message.data = "toggle_telegram"
        with patch("telegram_bot.handlers.settings.get_notifications_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cb_toggle_telegram(
                mock_callback_no_message, auth_token="test_token", user={"id": 123456}, locale="en"
            )

        mock_callback_no_message.answer.assert_called_once()

    async def test_cb_toggle_email(self, mock_callback):
        """Test toggle Email notifications callback."""
        mock_callback.data = "toggle_email"
        with patch(
            "telegram_bot.handlers.settings.auth_client.get_user_preferences",
            new_callable=AsyncMock,
            return_value={"notification_telegram_enabled": True, "notification_email_enabled": True},
        ):
            with patch("telegram_bot.handlers.settings.auth_client.update_user_preferences", new_callable=AsyncMock):
                with patch("telegram_bot.handlers.settings.get_notifications_keyboard") as mock_kb:
                    mock_kb.return_value = MagicMock()

                    await cb_toggle_email(mock_callback, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()
        mock_kb.assert_called_once_with(locale="en", telegram_enabled=True, email_enabled=False)

    async def test_cb_toggle_email_no_message(self, mock_callback_no_message):
        """Test toggle Email callback with no message."""
        mock_callback_no_message.data = "toggle_email"
        with patch("telegram_bot.handlers.settings.get_notifications_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cb_toggle_email(mock_callback_no_message, auth_token="test_token", user={"id": 123456}, locale="en")

        mock_callback_no_message.answer.assert_called_once()
