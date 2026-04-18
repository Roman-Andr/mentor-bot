"""Unit tests for telegram_bot/keyboards/common_kb.py."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.common_kb import (
    get_help_keyboard,
    get_my_mentor_keyboard,
    get_my_mentor_no_mentor_keyboard,
    get_progress_keyboard,
    get_schedule_mentor_keyboard,
    get_mentor_tasks_keyboard,
)


class TestGetHelpKeyboard:
    """Test cases for get_help_keyboard function."""

    def test_basic_keyboard(self):
        """Test basic help keyboard."""
        keyboard = get_help_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardBuilder)

    def test_buttons_exist(self):
        """Test that expected buttons exist."""
        keyboard = get_help_keyboard(locale="en")
        markup = keyboard.as_markup()

        all_buttons = [btn for row in markup.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in all_buttons]

        assert "menu" in callback_data
        assert "my_mentor" in callback_data

    def test_different_locales(self):
        """Test keyboard with different locales."""
        for locale in ["en", "ru"]:
            keyboard = get_help_keyboard(locale=locale)
            assert isinstance(keyboard, InlineKeyboardBuilder)


class TestGetMyMentorNoMentorKeyboard:
    """Test cases for get_my_mentor_no_mentor_keyboard function."""

    def test_basic_keyboard(self):
        """Test basic keyboard when no mentor assigned."""
        keyboard = get_my_mentor_no_mentor_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardBuilder)

    def test_only_menu_button(self):
        """Test that only menu button is present."""
        keyboard = get_my_mentor_no_mentor_keyboard(locale="en")
        markup = keyboard.as_markup()

        all_buttons = [btn for row in markup.inline_keyboard for btn in row]

        assert len(all_buttons) == 1
        assert all_buttons[0].callback_data == "menu"

    def test_back_arrow_emoji(self):
        """Test back button has arrow emoji."""
        keyboard = get_my_mentor_no_mentor_keyboard(locale="en")
        markup = keyboard.as_markup()

        button = markup.inline_keyboard[0][0]
        assert "\u2190" in button.text


class TestGetMyMentorKeyboard:
    """Test cases for get_my_mentor_keyboard function."""

    def test_basic_keyboard(self):
        """Test basic keyboard when mentor is assigned."""
        keyboard = get_my_mentor_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardBuilder)

    def test_all_buttons_present(self):
        """Test that all expected buttons are present."""
        keyboard = get_my_mentor_keyboard(locale="en")
        markup = keyboard.as_markup()

        all_buttons = [btn for row in markup.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in all_buttons]

        assert "message_mentor" in callback_data
        assert "schedule_mentor" in callback_data
        assert "mentor_tasks" in callback_data
        assert "menu" in callback_data

    def test_button_emojis(self):
        """Test that buttons have appropriate emojis."""
        keyboard = get_my_mentor_keyboard(locale="en")
        markup = keyboard.as_markup()

        all_texts = [btn.text for row in markup.inline_keyboard for btn in row]

        assert any("\U0001f4ac" in text for text in all_texts)  # Message bubble
        assert any("\U0001f4c5" in text for text in all_texts)  # Calendar
        assert any("\U0001f4cb" in text for text in all_texts)  # Clipboard
        assert any("\u2190" in text for text in all_texts)  # Back arrow

    def test_menu_button_last(self):
        """Test that menu button is last."""
        keyboard = get_my_mentor_keyboard(locale="en")
        markup = keyboard.as_markup()

        # Last button should be menu
        last_button = markup.inline_keyboard[-1][0]
        assert last_button.callback_data == "menu"


class TestGetScheduleMentorKeyboard:
    """Test cases for get_schedule_mentor_keyboard function."""

    def test_basic_keyboard(self):
        """Test basic schedule mentor keyboard."""
        keyboard = get_schedule_mentor_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardBuilder)

    def test_buttons_present(self):
        """Test expected buttons are present."""
        keyboard = get_schedule_mentor_keyboard(locale="en")
        markup = keyboard.as_markup()

        all_buttons = [btn for row in markup.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in all_buttons]

        assert "meetings_menu" in callback_data
        assert "my_mentor" in callback_data


class TestGetMentorTasksKeyboard:
    """Test cases for get_mentor_tasks_keyboard function."""

    def test_basic_keyboard(self):
        """Test basic mentor tasks keyboard."""
        keyboard = get_mentor_tasks_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardBuilder)

    def test_buttons_present(self):
        """Test expected buttons are present."""
        keyboard = get_mentor_tasks_keyboard(locale="en")
        markup = keyboard.as_markup()

        all_buttons = [btn for row in markup.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in all_buttons]

        assert "my_tasks" in callback_data
        assert "my_mentor" in callback_data

    def test_back_button_has_arrow(self):
        """Test back button has arrow emoji."""
        keyboard = get_mentor_tasks_keyboard(locale="en")
        markup = keyboard.as_markup()

        # Find back button
        back_button = None
        for row in markup.inline_keyboard:
            for btn in row:
                if btn.callback_data == "my_mentor":
                    back_button = btn
                    break

        assert back_button is not None
        assert "\u2190" in back_button.text


class TestGetProgressKeyboard:
    """Test cases for get_progress_keyboard function."""

    def test_basic_keyboard(self):
        """Test basic progress keyboard."""
        keyboard = get_progress_keyboard(checklist_id=1, locale="en")

        assert isinstance(keyboard, InlineKeyboardBuilder)

    def test_buttons_present(self):
        """Test expected buttons are present."""
        keyboard = get_progress_keyboard(checklist_id=1, locale="en")
        markup = keyboard.as_markup()

        all_buttons = [btn for row in markup.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in all_buttons]

        assert "my_tasks" in callback_data  # From progress.btn_my_tasks
        assert "meetings_menu" in callback_data  # From progress.btn_meetings
        assert "my_tasks" in callback_data  # Back button goes to my_tasks

    def test_back_button_callback(self):
        """Test back button callback."""
        keyboard = get_progress_keyboard(checklist_id=5, locale="en")
        markup = keyboard.as_markup()

        # Last button should be back
        last_button = markup.inline_keyboard[-1][0]
        assert last_button.callback_data == "my_tasks"

    def test_without_checklist_id(self):
        """Test keyboard without checklist_id."""
        keyboard = get_progress_keyboard(checklist_id=None, locale="en")

        assert isinstance(keyboard, InlineKeyboardBuilder)

    def test_different_locales(self):
        """Test keyboard with different locales."""
        for locale in ["en", "ru", "de"]:
            keyboard = get_progress_keyboard(checklist_id=1, locale=locale)
            assert isinstance(keyboard, InlineKeyboardBuilder)

    def test_button_count(self):
        """Test correct number of buttons."""
        keyboard = get_progress_keyboard(checklist_id=1, locale="en")
        markup = keyboard.as_markup()

        all_buttons = [btn for row in markup.inline_keyboard for btn in row]
        assert len(all_buttons) == 3  # my_tasks, meetings, back

    def test_primary_style_buttons(self):
        """Test that primary buttons are present."""
        keyboard = get_progress_keyboard(checklist_id=1, locale="en")
        markup = keyboard.as_markup()

        # Verify callbacks for primary actions
        all_callbacks = [btn.callback_data for row in markup.inline_keyboard for btn in row]
        assert "my_tasks" in all_callbacks
        assert "meetings_menu" in all_callbacks
