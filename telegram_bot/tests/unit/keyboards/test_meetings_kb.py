"""Unit tests for telegram_bot/keyboards/meetings_kb.py."""

from aiogram.types import InlineKeyboardMarkup

from telegram_bot.keyboards.meetings_kb import (
    get_meeting_details_keyboard,
    get_meetings_menu_keyboard,
    get_my_meetings_keyboard,
)


class TestGetMeetingsMenuKeyboard:
    """Test cases for get_meetings_menu_keyboard function."""

    def test_basic_keyboard(self):
        """Test basic meetings menu keyboard."""
        keyboard = get_meetings_menu_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3  # My meetings, Schedule, Menu

    def test_button_callbacks(self):
        """Test that buttons have correct callbacks."""
        keyboard = get_meetings_menu_keyboard(locale="en")

        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in all_buttons]

        assert "my_meetings" in callback_data
        assert "schedule_meeting" in callback_data
        assert "menu" in callback_data

    def test_button_emojis(self):
        """Test that buttons have correct emojis."""
        keyboard = get_meetings_menu_keyboard(locale="en")

        all_texts = [btn.text for row in keyboard.inline_keyboard for btn in row]

        assert any("\U0001f4cb" in text for text in all_texts)  # List emoji
        assert any("\u2795" in text for text in all_texts)  # Plus emoji
        assert any("\u2190" in text for text in all_texts)  # Back arrow

    def test_different_locale(self):
        """Test keyboard with different locale."""
        keyboard_en = get_meetings_menu_keyboard(locale="en")
        keyboard_ru = get_meetings_menu_keyboard(locale="ru")

        assert isinstance(keyboard_en, InlineKeyboardMarkup)
        assert isinstance(keyboard_ru, InlineKeyboardMarkup)


class TestGetMyMeetingsKeyboard:
    """Test cases for get_my_meetings_keyboard function."""

    def test_basic_keyboard(self):
        """Test basic my meetings keyboard."""
        keyboard = get_my_meetings_keyboard(locale="en")

        # Returns InlineKeyboardBuilder, not InlineKeyboardMarkup
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        assert isinstance(keyboard, InlineKeyboardBuilder)

    def test_back_button_callback(self):
        """Test back button has correct callback."""
        keyboard = get_my_meetings_keyboard(locale="en")

        markup = keyboard.as_markup()
        all_buttons = [btn for row in markup.inline_keyboard for btn in row]
        callback_data_values = [btn.callback_data for btn in all_buttons]

        assert "meetings_menu" in callback_data_values

    def test_back_button_emoji(self):
        """Test back button has emoji."""
        keyboard = get_my_meetings_keyboard(locale="en")

        markup = keyboard.as_markup()
        all_texts = [btn.text for row in markup.inline_keyboard for btn in row]

        assert any("\u2190" in text for text in all_texts)


class TestGetMeetingDetailsKeyboard:
    """Test cases for get_meeting_details_keyboard function."""

    def test_basic_keyboard(self):
        """Test basic meeting details keyboard."""
        keyboard = get_meeting_details_keyboard(meeting_id=123, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Confirm/Cancel row + Back row

    def test_button_callbacks_contain_meeting_id(self):
        """Test that button callbacks include meeting ID."""
        keyboard = get_meeting_details_keyboard(meeting_id=123, locale="en")

        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        callback_data_values = [btn.callback_data for btn in all_buttons]

        assert any("confirm_meeting_123" in cd for cd in callback_data_values)
        assert any("cancel_meeting_123" in cd for cd in callback_data_values)

    def test_button_layout(self):
        """Test that buttons are arranged correctly (2 on first row, 1 on second)."""
        keyboard = get_meeting_details_keyboard(meeting_id=123, locale="en")

        assert len(keyboard.inline_keyboard) == 2
        assert len(keyboard.inline_keyboard[0]) == 2  # Confirm, Cancel
        assert len(keyboard.inline_keyboard[1]) == 1  # Back

    def test_button_styles(self):
        """Test that buttons have appropriate styles (success for confirm, danger for cancel)."""
        keyboard = get_meeting_details_keyboard(meeting_id=123, locale="en")

        confirm_button = None
        cancel_button = None

        for row in keyboard.inline_keyboard:
            for btn in row:
                if "confirm" in btn.callback_data:
                    confirm_button = btn
                if "cancel" in btn.callback_data:
                    cancel_button = btn

        # Check for style indication in text (emojis)
        assert confirm_button is not None
        assert cancel_button is not None
        assert "\u2705" in confirm_button.text  # Checkmark
        assert "\u274c" in cancel_button.text  # X mark

    def test_back_button(self):
        """Test back button callback and text."""
        keyboard = get_meeting_details_keyboard(meeting_id=123, locale="en")

        back_button = keyboard.inline_keyboard[1][0]

        assert back_button.callback_data == "my_meetings"
        assert "\u2190" in back_button.text  # Back arrow

    def test_different_meeting_ids(self):
        """Test keyboard generation with different meeting IDs."""
        for meeting_id in [1, 999, 123456]:
            keyboard = get_meeting_details_keyboard(meeting_id=meeting_id, locale="en")

            all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
            callback_data_values = [btn.callback_data for btn in all_buttons]

            assert any(f"confirm_meeting_{meeting_id}" in cd for cd in callback_data_values)
            assert any(f"cancel_meeting_{meeting_id}" in cd for cd in callback_data_values)

    def test_different_locales(self):
        """Test keyboard with different locales."""
        for locale in ["en", "ru", "de"]:
            keyboard = get_meeting_details_keyboard(meeting_id=123, locale=locale)

            assert isinstance(keyboard, InlineKeyboardMarkup)
            assert len(keyboard.inline_keyboard) == 2
