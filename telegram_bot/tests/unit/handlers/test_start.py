"""Unit tests for telegram_bot/handlers/start.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext

from telegram_bot.handlers.start import cb_menu, cmd_menu, cmd_start
from telegram_bot.states.auth_states import RegistrationStates


class TestStartHandlers:
    """Test cases for start handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 123456
        msg.from_user.first_name = "John"
        msg.from_user.last_name = "Doe"
        msg.from_user.username = "johndoe"
        msg.text = "/start"
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query."""
        cb = MagicMock()
        cb.id = "callback_123"
        cb.from_user = MagicMock()
        cb.from_user.id = 123456
        cb.data = "menu"
        cb.answer = AsyncMock()
        cb.message = MagicMock()
        cb.message.chat = MagicMock()
        cb.message.chat.id = 123456
        cb.message.edit_text = AsyncMock()
        return cb

    @pytest.fixture
    def mock_state(self):
        """Create a mock FSM state."""
        state = MagicMock(spec=FSMContext)
        state.clear = AsyncMock()
        state.set_state = AsyncMock()
        return state

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        return {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "role": "USER",
        }

    async def test_cmd_start_authenticated(self, mock_message, mock_state, mock_user):
        """Test start command for authenticated user."""
        with patch("telegram_bot.handlers.start.format_welcome_message", return_value="Welcome!"):
            with patch("telegram_bot.handlers.start.get_main_menu_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await cmd_start(
                    mock_message,
                    mock_state,
                    is_authenticated=True,
                    user=mock_user,
                    locale="en",
                )

        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called_once()

    async def test_cmd_start_with_token_success(self, mock_message, mock_state):
        """Test start command with invitation token - success."""
        mock_message.text = "/start token123"

        registered_user = {"id": 1, "first_name": "John", "role": "USER"}

        with patch("telegram_bot.handlers.start.register_by_token", return_value=(True, registered_user)):
            with patch("telegram_bot.handlers.start.format_welcome_message", return_value="Welcome!"):
                with patch("telegram_bot.handlers.start.get_main_menu_keyboard") as mock_kb:
                    mock_kb.return_value = MagicMock()

                    await cmd_start(
                        mock_message,
                        mock_state,
                        is_authenticated=False,
                        user=None,
                        locale="en",
                    )

        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called_once()

    async def test_cmd_start_with_token_failure(self, mock_message, mock_state):
        """Test start command with invitation token - failure."""
        mock_message.text = "/start invalid_token"

        with patch("telegram_bot.handlers.start.register_by_token", return_value=(False, "Invalid token")):
            await cmd_start(
                mock_message,
                mock_state,
                is_authenticated=False,
                user=None,
                locale="en",
            )

        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(RegistrationStates.waiting_for_token)

    async def test_cmd_start_no_token(self, mock_message, mock_state):
        """Test start command without token."""
        mock_message.text = "/start"

        await cmd_start(
            mock_message,
            mock_state,
            is_authenticated=False,
            user=None,
            locale="en",
        )

        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(RegistrationStates.waiting_for_token)

    async def test_cmd_menu_authenticated(self, mock_message, mock_user):
        """Test menu command for authenticated user."""
        with patch("telegram_bot.handlers.start.get_inline_main_menu") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cmd_menu(
                mock_message,
                is_authenticated=True,
                user=mock_user,
                locale="en",
            )

        mock_message.answer.assert_called_once()

    async def test_cmd_menu_not_authenticated(self, mock_message):
        """Test menu command for non-authenticated user."""
        await cmd_menu(
            mock_message,
            is_authenticated=False,
            user=None,
            locale="en",
        )

        mock_message.answer.assert_called_once()

    async def test_cb_menu_authenticated(self, mock_callback, mock_user):
        """Test menu callback for authenticated user."""
        with patch("telegram_bot.handlers.start.get_inline_main_menu") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cb_menu(
                mock_callback,
                is_authenticated=True,
                user=mock_user,
                locale="en",
            )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_cb_menu_not_authenticated(self, mock_callback):
        """Test menu callback for non-authenticated user."""
        await cb_menu(
            mock_callback,
            is_authenticated=False,
            user=None,
            locale="en",
        )

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_not_called()

    async def test_cb_menu_no_message(self, mock_callback, mock_user):
        """Test menu callback when message is None."""
        mock_callback.message = None

        await cb_menu(
            mock_callback,
            is_authenticated=True,
            user=mock_user,
            locale="en",
        )

        mock_callback.answer.assert_called_once()
