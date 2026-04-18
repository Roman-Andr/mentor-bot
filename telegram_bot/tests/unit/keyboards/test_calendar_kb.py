"""Unit tests for telegram_bot calendar keyboards."""

from aiogram.types import InlineKeyboardMarkup

from telegram_bot.keyboards.calendar_kb import (
    get_calendar_connect_keyboard,
    get_calendar_connected_keyboard,
    get_calendar_not_connected_keyboard,
)


class TestGetCalendarConnectedKeyboard:
    """Test cases for get_calendar_connected_keyboard."""

    def test_connected_keyboard_structure(self):
        """Test keyboard when calendar is connected."""
        keyboard = get_calendar_connected_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3  # Reconnect, disconnect, back

    def test_connected_keyboard_buttons(self):
        """Test buttons in connected keyboard."""
        keyboard = get_calendar_connected_keyboard(locale="en")

        # First button should be reconnect
        assert "\U0001f504" in keyboard.inline_keyboard[0][0].text
        # Second button should be disconnect
        assert "\u274c" in keyboard.inline_keyboard[1][0].text
        # Third button should be menu
        assert "\u2190" in keyboard.inline_keyboard[2][0].text


class TestGetCalendarNotConnectedKeyboard:
    """Test cases for get_calendar_not_connected_keyboard."""

    def test_not_connected_keyboard_structure(self):
        """Test keyboard when calendar is not connected."""
        keyboard = get_calendar_not_connected_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Connect, back

    def test_not_connected_keyboard_buttons(self):
        """Test buttons in not-connected keyboard."""
        keyboard = get_calendar_not_connected_keyboard(locale="en")

        # First button should be connect
        assert "\U0001f517" in keyboard.inline_keyboard[0][0].text
        # Second button should be menu
        assert "\u2190" in keyboard.inline_keyboard[1][0].text


class TestGetCalendarConnectKeyboard:
    """Test cases for get_calendar_connect_keyboard."""

    def test_connect_keyboard_with_url(self):
        """Test keyboard with authorization URL."""
        connect_url = "https://accounts.google.com/oauth/authorize?test=1"
        keyboard = get_calendar_connect_keyboard(connect_url, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Buttons are in one row with 2 buttons
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 2  # Authorize URL, back

    def test_connect_keyboard_url_button(self):
        """Test that authorize button has URL."""
        connect_url = "https://accounts.google.com/oauth/authorize"
        keyboard = get_calendar_connect_keyboard(connect_url, locale="en")

        # First button should have URL
        assert keyboard.inline_keyboard[0][0].url == connect_url

    def test_connect_keyboard_back_button(self):
        """Test back button in connect keyboard."""
        keyboard = get_calendar_connect_keyboard("https://example.com", locale="en")

        # Second button in first row should be back
        assert "\u2190" in keyboard.inline_keyboard[0][1].text
        assert keyboard.inline_keyboard[0][1].callback_data == "calendar_menu"
