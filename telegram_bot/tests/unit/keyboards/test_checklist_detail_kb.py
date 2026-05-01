"""Unit tests for telegram_bot/keyboards/checklist_detail.py."""

from telegram_bot.keyboards.checklist_detail import (
    get_attach_task_keyboard,
    get_back_to_task_keyboard,
    get_no_checklists_keyboard,
    get_no_tasks_keyboard,
    get_skip_description_keyboard,
    get_task_attachments_keyboard,
    get_task_completed_keyboard,
    get_task_info_keyboard,
)


class TestChecklistDetailKeyboards:
    """Test cases for checklist detail keyboards."""

    def test_get_no_checklists_keyboard(self):
        """Test no checklists keyboard."""
        builder = get_no_checklists_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_no_checklists_keyboard_russian(self):
        """Test no checklists keyboard - Russian locale."""
        builder = get_no_checklists_keyboard(locale="ru")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_no_tasks_keyboard(self):
        """Test no tasks keyboard."""
        builder = get_no_tasks_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_attach_task_keyboard(self):
        """Test attach task keyboard."""
        builder = get_attach_task_keyboard(1, 2, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_attach_task_keyboard_without_checklist(self):
        """Test attach task keyboard without checklist ID."""
        builder = get_attach_task_keyboard(1, None, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_info_keyboard_completed(self):
        """Test task info keyboard for completed task."""
        builder = get_task_info_keyboard(1, 2, "COMPLETED", 0, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_info_keyboard_completed_with_attachments(self):
        """Test task info keyboard for completed task with attachments."""
        builder = get_task_info_keyboard(1, 2, "COMPLETED", 3, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_info_keyboard_in_progress(self):
        """Test task info keyboard for in-progress task."""
        builder = get_task_info_keyboard(1, 2, "IN_PROGRESS", 0, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_info_keyboard_pending(self):
        """Test task info keyboard for pending task."""
        builder = get_task_info_keyboard(1, 2, "PENDING", 0, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_info_keyboard_blocked(self):
        """Test task info keyboard for blocked task."""
        builder = get_task_info_keyboard(1, 2, "BLOCKED", 0, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_info_keyboard_lowercase_status(self):
        """Test task info keyboard with lowercase status."""
        builder = get_task_info_keyboard(1, 2, "completed", 0, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_info_keyboard_without_checklist(self):
        """Test task info keyboard without checklist ID."""
        builder = get_task_info_keyboard(1, None, "COMPLETED", 0, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_info_keyboard_none_status(self):
        """Test task info keyboard with None status."""
        builder = get_task_info_keyboard(1, 2, None, 0, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_completed_keyboard(self):
        """Test task completed keyboard."""
        builder = get_task_completed_keyboard(1, 2, 0, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_completed_keyboard_with_attachments(self):
        """Test task completed keyboard with attachments."""
        builder = get_task_completed_keyboard(1, 2, 2, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_completed_keyboard_without_checklist(self):
        """Test task completed keyboard without checklist ID."""
        builder = get_task_completed_keyboard(1, None, 0, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_skip_description_keyboard(self):
        """Test skip description keyboard."""
        builder = get_skip_description_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_back_to_task_keyboard(self):
        """Test back to task keyboard."""
        builder = get_back_to_task_keyboard(1, 2, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_back_to_task_keyboard_without_checklist(self):
        """Test back to task keyboard without checklist ID."""
        builder = get_back_to_task_keyboard(1, None, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_attachments_keyboard(self):
        """Test task attachments keyboard."""
        attachments = [
            {"id": 1, "filename": "document.pdf"},
            {"id": 2, "filename": "image.png"},
        ]
        builder = get_task_attachments_keyboard(attachments, 1, 2, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_attachments_keyboard_with_images(self):
        """Test task attachments keyboard with image files."""
        attachments = [
            {"id": 1, "filename": "photo.jpg"},
            {"id": 2, "filename": "pic.jpeg"},
            {"id": 3, "filename": "img.png"},
            {"id": 4, "filename": "anim.gif"},
            {"id": 5, "filename": "sticker.webp"},
        ]
        builder = get_task_attachments_keyboard(attachments, 1, 2, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_attachments_keyboard_long_filename(self):
        """Test task attachments keyboard with long filename."""
        attachments = [
            {"id": 1, "filename": "a" * 50 + ".pdf"},
        ]
        builder = get_task_attachments_keyboard(attachments, 1, 2, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_attachments_keyboard_many_attachments(self):
        """Test task attachments keyboard with many attachments (should limit to 10)."""
        attachments = [{"id": i, "filename": f"file{i}.pdf"} for i in range(15)]
        builder = get_task_attachments_keyboard(attachments, 1, 2, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_attachments_keyboard_empty(self):
        """Test task attachments keyboard with empty list."""
        builder = get_task_attachments_keyboard([], 1, 2, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_task_attachments_keyboard_without_checklist(self):
        """Test task attachments keyboard without checklist ID."""
        attachments = [{"id": 1, "filename": "file.pdf"}]
        builder = get_task_attachments_keyboard(attachments, 1, None, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")
