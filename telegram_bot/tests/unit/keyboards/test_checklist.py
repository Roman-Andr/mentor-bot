"""Unit tests for telegram_bot/keyboards/checklist.py."""

from aiogram.types import InlineKeyboardMarkup
from telegram_bot.keyboards.checklist import (
    get_checklists_keyboard,
    get_task_detail_keyboard,
    get_tasks_keyboard,
)


class TestGetChecklistsKeyboard:
    """Test cases for get_checklists_keyboard function."""

    def test_basic_checklists_keyboard(self):
        """Test basic keyboard generation with checklists."""
        checklists = [
            {"id": 1, "name": "Onboarding", "status": "in_progress"},
            {"id": 2, "name": "Training", "status": "completed"},
        ]

        keyboard = get_checklists_keyboard(checklists, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3  # 2 checklists + menu button

    def test_empty_checklists(self):
        """Test keyboard with empty checklists."""
        keyboard = get_checklists_keyboard([], locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Should still have menu button
        assert len(keyboard.inline_keyboard) >= 1

    def test_checklist_status_emojis(self):
        """Test that correct emojis are used for different statuses."""
        checklists = [
            {"id": 1, "name": "Completed", "status": "completed"},
            {"id": 2, "name": "In Progress", "status": "in_progress"},
            {"id": 3, "name": "Pending", "status": "pending"},
        ]

        keyboard = get_checklists_keyboard(checklists, locale="en")

        # Get all button texts
        all_buttons = [btn.text for row in keyboard.inline_keyboard for btn in row]

        # Check for different emojis based on status
        assert any("\u2705" in btn for btn in all_buttons)  # Completed emoji
        assert any("\U0001f4cb" in btn for btn in all_buttons)  # In progress emoji
        assert any("\u23f3" in btn for btn in all_buttons)  # Pending emoji

    def test_checklist_fallback_name(self):
        """Test that fallback name is used when name missing."""
        checklists = [{"id": 999, "status": "in_progress"}]  # No name

        keyboard = get_checklists_keyboard(checklists, locale="en")

        # Should use "Checklist #999" as fallback
        all_buttons = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert any("Checklist #999" in btn for btn in all_buttons)

    def test_checklist_limit_to_5(self):
        """Test that only first 5 checklists are shown."""
        checklists = [{"id": i, "name": f"Checklist {i}", "status": "in_progress"} for i in range(10)]

        keyboard = get_checklists_keyboard(checklists, locale="en")

        # Should only have 5 checklist buttons + menu button
        assert len(keyboard.inline_keyboard) == 6

    def test_menu_button_callback(self):
        """Test that menu button has correct callback."""
        checklists = [{"id": 1, "name": "Test", "status": "in_progress"}]

        keyboard = get_checklists_keyboard(checklists, locale="en")

        # Find menu button (last row)
        last_row = keyboard.inline_keyboard[-1]
        menu_button = last_row[0]

        assert menu_button.callback_data == "menu"


class TestGetTasksKeyboard:
    """Test cases for get_tasks_keyboard function."""

    def test_basic_tasks_keyboard(self):
        """Test basic keyboard generation with tasks."""
        tasks = [
            {"id": 1, "title": "Task 1", "status": "PENDING"},
            {"id": 2, "title": "Task 2", "status": "COMPLETED"},
        ]

        keyboard = get_tasks_keyboard(tasks, checklist_id=1, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Tasks + back button
        assert len(keyboard.inline_keyboard) == 3

    def test_task_status_emojis(self):
        """Test that correct emojis are used for different task statuses."""
        tasks = [
            {"id": 1, "title": "Completed", "status": "COMPLETED"},
            {"id": 2, "title": "In Progress", "status": "IN_PROGRESS"},
            {"id": 3, "title": "Blocked", "status": "BLOCKED"},
            {"id": 4, "title": "Pending", "status": "PENDING"},
        ]

        keyboard = get_tasks_keyboard(tasks, locale="en")

        all_buttons = [btn.text for row in keyboard.inline_keyboard for btn in row]

        assert any("\u2705" in btn for btn in all_buttons)  # Completed
        assert any("\U0001f504" in btn for btn in all_buttons)  # In progress
        assert any("\U0001f6ab" in btn for btn in all_buttons)  # Blocked
        assert any("\U0001f4dd" in btn for btn in all_buttons)  # Pending

    def test_task_with_due_date(self):
        """Test task keyboard with due date formatting."""
        tasks = [
            {"id": 1, "title": "Task with due date", "status": "PENDING", "due_date": "2024-12-25T10:00:00"},
        ]

        keyboard = get_tasks_keyboard(tasks, locale="en")

        # Find task button (first row)
        task_button = keyboard.inline_keyboard[0][0]

        # Should include formatted date (25.12)
        assert "25.12" in task_button.text or "12.25" in task_button.text or "\ud83d\udcc5" in task_button.text

    def test_task_with_invalid_due_date(self):
        """Test task keyboard with invalid due date."""
        tasks = [
            {"id": 1, "title": "Task", "status": "PENDING", "due_date": "invalid-date"},
        ]

        keyboard = get_tasks_keyboard(tasks, locale="en")

        # Should still work without crashing
        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_tasks_limit_to_10(self):
        """Test that only first 10 tasks are shown."""
        tasks = [{"id": i, "title": f"Task {i}", "status": "PENDING"} for i in range(15)]

        keyboard = get_tasks_keyboard(tasks, locale="en")

        # Should have 10 task buttons + back button
        assert len(keyboard.inline_keyboard) == 11

    def test_callback_data_with_checklist_id(self):
        """Test that callback data includes checklist_id when provided."""
        tasks = [{"id": 1, "title": "Task", "status": "PENDING"}]

        keyboard = get_tasks_keyboard(tasks, checklist_id=5, locale="en")

        task_button = keyboard.inline_keyboard[0][0]
        assert "task_1_5" in task_button.callback_data

    def test_callback_data_without_checklist_id(self):
        """Test that callback data doesn't include checklist_id when not provided."""
        tasks = [{"id": 1, "title": "Task", "status": "PENDING"}]

        keyboard = get_tasks_keyboard(tasks, checklist_id=None, locale="en")

        task_button = keyboard.inline_keyboard[0][0]
        assert task_button.callback_data == "task_1"


class TestGetTaskDetailKeyboard:
    """Test cases for get_task_detail_keyboard function."""

    def test_completed_task_keyboard(self):
        """Test keyboard for completed task."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=5, task_status="COMPLETED", attachment_count=0, locale="en"
        )

        assert isinstance(keyboard, InlineKeyboardMarkup)

        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in all_buttons]

        # Completed task should have status button with noop callback
        assert "noop" in callback_data

    def test_in_progress_task_keyboard(self):
        """Test keyboard for in-progress task."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=5, task_status="IN_PROGRESS", attachment_count=0, locale="en"
        )

        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in all_buttons]

        # Should have complete and attach buttons
        assert any("complete_task" in cd for cd in callback_data)
        assert any("attach_task" in cd for cd in callback_data)

    def test_pending_task_keyboard(self):
        """Test keyboard for pending task."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=5, task_status="PENDING", attachment_count=0, locale="en"
        )

        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in all_buttons]

        # Should have start and attach buttons
        assert any("start_task" in cd for cd in callback_data)
        assert any("attach_task" in cd for cd in callback_data)

    def test_task_with_attachments(self):
        """Test keyboard includes view files button when attachments exist."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=5, task_status="IN_PROGRESS", attachment_count=3, locale="en"
        )

        all_buttons = [btn.text for row in keyboard.inline_keyboard for btn in row]

        # Should have view files button with count
        assert any("(3)" in btn for btn in all_buttons)

    def test_task_without_attachments(self):
        """Test keyboard doesn't include view files button when no attachments."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=5, task_status="IN_PROGRESS", attachment_count=0, locale="en"
        )

        all_buttons = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]

        # Should not have task_files callback
        assert not any("task_files" in cd for cd in all_buttons)

    def test_back_callback_with_checklist_id(self):
        """Test back button callback when checklist_id provided."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=5, task_status="PENDING", attachment_count=0, locale="en"
        )

        # Find back button (last row)
        last_row = keyboard.inline_keyboard[-1]
        back_button = last_row[0]

        assert back_button.callback_data == "checklist_5"

    def test_back_callback_without_checklist_id(self):
        """Test back button callback when checklist_id not provided."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=None, task_status="PENDING", attachment_count=0, locale="en"
        )

        # Find back button
        last_row = keyboard.inline_keyboard[-1]
        back_button = last_row[0]

        assert back_button.callback_data == "my_tasks"

    def test_lowercase_status_handling(self):
        """Test that lowercase status is handled correctly."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=5, task_status="completed", attachment_count=0, locale="en"
        )

        # Should treat lowercase as completed
        all_callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "noop" in all_callbacks

    def test_none_status_handling(self):
        """Test handling of None status."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=5, task_status=None, attachment_count=0, locale="en"
        )

        # Should default to pending behavior
        all_callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert any("start_task" in cd for cd in all_callbacks)

    def test_zero_checklist_id(self):
        """Test handling of checklist_id=0 (falsy but valid)."""
        keyboard = get_task_detail_keyboard(
            task_id=1, checklist_id=0, task_status="PENDING", attachment_count=0, locale="en"
        )

        # Back button should go to checklist_0
        last_row = keyboard.inline_keyboard[-1]
        back_button = last_row[0]

        # When checklist_id is 0, it should still be used
        assert "0" in back_button.callback_data
