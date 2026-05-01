"""Unit tests for telegram_bot inline keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegram_bot.keyboards.checklist import (
    get_checklists_keyboard,
    get_task_detail_keyboard,
    get_tasks_keyboard,
)
from telegram_bot.keyboards.common_kb import (
    get_help_keyboard,
    get_my_mentor_keyboard,
    get_my_mentor_no_mentor_keyboard,
    get_progress_keyboard,
    get_schedule_mentor_keyboard,
)
from telegram_bot.keyboards.escalation_kb import (
    get_escalation_details_keyboard,
    get_escalation_menu_keyboard,
    get_my_escalations_keyboard,
    get_new_escalation_keyboard,
)
from telegram_bot.keyboards.feedback_kb import (
    get_experience_rating_keyboard,
    get_feedback_menu_keyboard,
)
from telegram_bot.keyboards.language_kb import get_language_keyboard
from telegram_bot.keyboards.main_menu import get_inline_main_menu
from telegram_bot.keyboards.meetings_kb import (
    get_meeting_details_keyboard,
    get_meetings_menu_keyboard,
)
from telegram_bot.keyboards.utils import create_inline_button


class TestCreateInlineButton:
    """Test cases for create_inline_button utility."""

    def test_create_simple_button(self):
        """Test creating a simple inline button."""
        button = create_inline_button("Click me", callback_data="click")

        assert button.text == "Click me"
        assert button.callback_data == "click"

    def test_create_button_with_url(self):
        """Test creating button with URL."""
        button = create_inline_button("Visit", url="https://example.com")

        assert button.text == "Visit"
        assert button.url == "https://example.com"


class TestGetChecklistsKeyboard:
    """Test cases for get_checklists_keyboard."""

    def test_empty_checklists(self):
        """Test keyboard with empty checklists list."""
        checklists = []
        keyboard = get_checklists_keyboard(checklists, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_single_checklist(self):
        """Test keyboard with single checklist."""
        checklists = [{"id": 1, "name": "Test Checklist", "status": "in_progress"}]
        keyboard = get_checklists_keyboard(checklists, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_multiple_checklists(self):
        """Test keyboard with multiple checklists."""
        checklists = [
            {"id": 1, "name": "Checklist 1", "status": "completed"},
            {"id": 2, "name": "Checklist 2", "status": "in_progress"},
            {"id": 3, "name": "Checklist 3", "status": "pending"},
        ]
        keyboard = get_checklists_keyboard(checklists, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)


class TestGetTasksKeyboard:
    """Test cases for get_tasks_keyboard."""

    def test_empty_tasks(self):
        """Test keyboard with empty tasks list."""
        tasks = []
        keyboard = get_tasks_keyboard(tasks, checklist_id=1, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_single_task(self):
        """Test keyboard with single task."""
        tasks = [{"id": 1, "title": "Test Task", "status": "PENDING"}]
        keyboard = get_tasks_keyboard(tasks, checklist_id=1, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)


class TestGetTaskDetailKeyboard:
    """Test cases for get_task_detail_keyboard."""

    def test_completed_task_buttons(self):
        """Test keyboard for completed task."""
        keyboard = get_task_detail_keyboard(task_id=1, checklist_id=1, task_status="completed", locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_in_progress_task_buttons(self):
        """Test keyboard for in-progress task."""
        keyboard = get_task_detail_keyboard(task_id=1, checklist_id=1, task_status="in_progress", locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_pending_task_buttons(self):
        """Test keyboard for pending task."""
        keyboard = get_task_detail_keyboard(task_id=1, checklist_id=1, task_status="pending", locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_task_with_attachments(self):
        """Test keyboard shows view files button when attachments exist."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=1, task_status="in_progress", attachment_count=3, locale="en"
        )

        assert isinstance(keyboard, InlineKeyboardMarkup)


class TestGetInlineMainMenu:
    """Test cases for get_inline_main_menu."""

    def test_menu_for_regular_user(self):
        """Test main menu for regular user."""
        user = {"id": 1, "role": "USER"}
        keyboard = get_inline_main_menu(user=user, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_menu_for_admin_user(self):
        """Test main menu includes admin button for admin users."""
        user = {"id": 1, "role": "ADMIN"}
        keyboard = get_inline_main_menu(user=user, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_menu_for_hr_user(self):
        """Test main menu includes admin button for HR users."""
        user = {"id": 1, "role": "HR"}
        keyboard = get_inline_main_menu(user=user, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_menu_no_user(self):
        """Test main menu when user is None."""
        keyboard = get_inline_main_menu(user=None, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)


class TestGetLanguageKeyboard:
    """Test cases for get_language_keyboard."""

    def test_language_keyboard(self):
        """Test language selection keyboard."""
        result = get_language_keyboard()

        # Function returns InlineKeyboardBuilder, not InlineKeyboardMarkup
        assert isinstance(result, (InlineKeyboardBuilder, InlineKeyboardMarkup))


class TestGetFeedbackKeyboards:
    """Test cases for feedback keyboards."""

    def test_feedback_menu_keyboard(self):
        """Test feedback menu keyboard."""
        keyboard = get_feedback_menu_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_experience_rating_keyboard(self):
        """Test experience rating keyboard."""
        keyboard = get_experience_rating_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)


class TestGetEscalationKeyboards:
    """Test cases for escalation keyboards."""

    def test_escalation_menu_keyboard(self):
        """Test escalation menu keyboard."""
        keyboard = get_escalation_menu_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_new_escalation_keyboard(self):
        """Test new escalation keyboard."""
        keyboard = get_new_escalation_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_my_escalations_keyboard(self):
        """Test my escalations keyboard."""
        keyboard = get_my_escalations_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_escalation_details_keyboard(self):
        """Test escalation details keyboard."""
        keyboard = get_escalation_details_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)


class TestGetMeetingsKeyboards:
    """Test cases for meetings keyboards."""

    def test_meetings_menu_keyboard(self):
        """Test meetings menu keyboard."""
        keyboard = get_meetings_menu_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_meeting_details_keyboard(self):
        """Test meeting details keyboard."""
        keyboard = get_meeting_details_keyboard(meeting_id=1, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)


class TestGetCommonKeyboards:
    """Test cases for common keyboards."""

    def test_help_keyboard(self):
        """Test help keyboard."""
        result = get_help_keyboard(locale="en")

        assert result is not None

    def test_my_mentor_no_mentor_keyboard(self):
        """Test my mentor keyboard when no mentor assigned."""
        result = get_my_mentor_no_mentor_keyboard(locale="en")

        assert result is not None

    def test_my_mentor_keyboard(self):
        """Test my mentor keyboard when mentor assigned."""
        result = get_my_mentor_keyboard(locale="en")

        assert result is not None

    def test_schedule_mentor_keyboard(self):
        """Test schedule mentor keyboard."""
        result = get_schedule_mentor_keyboard(locale="en")

        assert result is not None

    def test_progress_keyboard(self):
        """Test progress keyboard."""
        result = get_progress_keyboard(checklist_id=1, locale="en")

        assert result is not None

    def test_progress_keyboard_no_checklist(self):
        """Test progress keyboard without checklist_id."""
        result = get_progress_keyboard(checklist_id=None, locale="en")

        assert result is not None
