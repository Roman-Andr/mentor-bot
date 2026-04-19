"""Unit tests for telegram_bot/handlers/common.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.handlers.common import (
    cmd_about,
    cmd_help,
    mentor_tasks,
    message_mentor,
    my_mentor,
    progress,
    schedule_mentor,
)
from telegram_bot.states.escalation_states import EscalationStates


class TestCommonHandlers:
    """Test cases for common handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        msg = MagicMock(spec=Message)
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "callback_data"
        cb.answer = AsyncMock()
        msg_mock = MagicMock(spec=Message)
        msg_mock.edit_text = AsyncMock()
        msg_mock.answer = AsyncMock()
        cb.message = msg_mock
        return cb

    @pytest.fixture
    def mock_state(self):
        """Create a mock FSM state."""
        state = MagicMock(spec=FSMContext)
        state.set_state = AsyncMock()
        state.update_data = AsyncMock()
        state.clear = AsyncMock()
        return state

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        return {"id": 1, "first_name": "John", "mentor_id": 2}

    @pytest.fixture
    def mock_user_no_mentor(self):
        """Create a mock user without mentor."""
        return {"id": 1, "first_name": "John", "mentor_id": None}

    @pytest.fixture
    def mock_auth_token(self):
        """Create a mock auth token."""
        return "test_auth_token_123"

    # Tests for cmd_help
    async def test_cmd_help_callback(self, mock_callback):
        """Test help via callback."""
        with patch(
            "telegram_bot.handlers.common.get_help_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await cmd_help(mock_callback, locale="en")

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_cmd_help_message(self, mock_message):
        """Test help via message."""
        with patch(
            "telegram_bot.handlers.common.get_help_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await cmd_help(mock_message, locale="en")

        mock_message.answer.assert_called_once()

    async def test_cmd_help_no_message(self):
        """Test help with no message."""
        cb = MagicMock(spec=CallbackQuery)
        cb.answer = AsyncMock()
        cb.message = None

        result = await cmd_help(cb, locale="en")
        assert result is None

    # Tests for cmd_about
    async def test_cmd_about(self, mock_message):
        """Test about command."""
        await cmd_about(mock_message, locale="en")

        mock_message.answer.assert_called_once()
        assert "parse_mode" in mock_message.answer.call_args.kwargs

    # Tests for my_mentor
    async def test_my_mentor_with_mentor_callback(self, mock_callback, mock_user, mock_auth_token):
        """Test my mentor with mentor via callback."""
        mentor_info = {
            "first_name": "Jane",
            "last_name": "Smith",
            "position": "Senior Dev",
            "email": "jane@example.com",
            "phone": "+1234567890",
            "department": {"name": "Engineering"},
        }

        with patch(
            "telegram_bot.handlers.common.auth_client.get_mentor_info",
            new_callable=AsyncMock,
            return_value=mentor_info,
        ):
            with patch(
                "telegram_bot.handlers.common.get_my_mentor_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await my_mentor(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_my_mentor_with_mentor_message(self, mock_message, mock_user, mock_auth_token):
        """Test my mentor with mentor via message."""
        mentor_info = {
            "first_name": "Jane",
            "last_name": "Smith",
            "position": "Senior Dev",
            "email": "jane@example.com",
            "phone": "+1234567890",
            "department": {"name": "Engineering"},
        }

        with patch(
            "telegram_bot.handlers.common.auth_client.get_mentor_info",
            new_callable=AsyncMock,
            return_value=mentor_info,
        ):
            with patch(
                "telegram_bot.handlers.common.get_my_mentor_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await my_mentor(mock_message, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_my_mentor_no_mentor(self, mock_callback, mock_user_no_mentor, mock_auth_token):
        """Test my mentor without mentor."""
        with patch(
            "telegram_bot.handlers.common.get_my_mentor_no_mentor_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await my_mentor(mock_callback, mock_user_no_mentor, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_my_mentor_no_user(self, mock_callback, mock_auth_token):
        """Test my mentor with no user."""
        await my_mentor(mock_callback, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_my_mentor_mentor_info_none(self, mock_callback, mock_user, mock_auth_token):
        """Test my mentor when mentor info is None."""
        with patch(
            "telegram_bot.handlers.common.auth_client.get_mentor_info",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with patch(
                "telegram_bot.handlers.common.get_my_mentor_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await my_mentor(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_my_mentor_string_department(self, mock_callback, mock_user, mock_auth_token):
        """Test my mentor with string department."""
        mentor_info = {
            "first_name": "Jane",
            "last_name": "Smith",
            "position": "Senior Dev",
            "email": "jane@example.com",
            "phone": "+1234567890",
            "department": "Engineering",  # String instead of dict
        }

        with patch(
            "telegram_bot.handlers.common.auth_client.get_mentor_info",
            new_callable=AsyncMock,
            return_value=mentor_info,
        ):
            with patch(
                "telegram_bot.handlers.common.get_my_mentor_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await my_mentor(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_my_mentor_no_message(self, mock_callback):
        """Test my mentor with no message."""
        cb = MagicMock(spec=CallbackQuery)
        cb.answer = AsyncMock()
        cb.message = None
        user = {"id": 1, "mentor_id": None}

        result = await my_mentor(cb, user, "token", locale="en")
        assert result is None

    # Tests for message_mentor
    async def test_message_mentor(self, mock_callback, mock_state):
        """Test message mentor."""
        await message_mentor(mock_callback, mock_state, locale="en")

        mock_state.set_state.assert_called_once_with(EscalationStates.waiting_for_description)
        mock_state.update_data.assert_called_once_with(category="Contact Mentor")

    async def test_message_mentor_no_message(self, mock_callback, mock_state):
        """Test message mentor with no message."""
        cb = MagicMock(spec=CallbackQuery)
        cb.message = None

        result = await message_mentor(cb, mock_state, locale="en")
        assert result is None
        mock_state.set_state.assert_not_called()

    # Tests for schedule_mentor
    async def test_schedule_mentor(self, mock_callback):
        """Test schedule mentor."""
        with patch(
            "telegram_bot.handlers.common.get_schedule_mentor_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await schedule_mentor(mock_callback, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_schedule_mentor_no_message(self, mock_callback):
        """Test schedule mentor with no message."""
        cb = MagicMock(spec=CallbackQuery)
        cb.message = None

        result = await schedule_mentor(cb, locale="en")
        assert result is None

    # Tests for mentor_tasks
    async def test_mentor_tasks_with_tasks(self, mock_callback, mock_auth_token):
        """Test mentor tasks with pending tasks."""
        mock_tasks = [
            {"title": "Task 1", "status": "pending"},
            {"title": "Task 2", "status": "in_progress"},
            {"title": "Task 3", "status": "completed"},
        ]

        with patch(
            "telegram_bot.handlers.common.checklists_client.get_assigned_tasks",
            new_callable=AsyncMock,
            return_value=mock_tasks,
        ):
            with patch(
                "telegram_bot.handlers.common.get_mentor_tasks_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await mentor_tasks(mock_callback, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_mentor_tasks_no_tasks(self, mock_callback, mock_auth_token):
        """Test mentor tasks with no pending tasks."""
        mock_tasks = [
            {"title": "Task 1", "status": "completed"},
        ]

        with patch(
            "telegram_bot.handlers.common.checklists_client.get_assigned_tasks",
            new_callable=AsyncMock,
            return_value=mock_tasks,
        ):
            with patch(
                "telegram_bot.handlers.common.get_mentor_tasks_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await mentor_tasks(mock_callback, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_mentor_tasks_empty(self, mock_callback, mock_auth_token):
        """Test mentor tasks with empty list."""
        with patch(
            "telegram_bot.handlers.common.checklists_client.get_assigned_tasks",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with patch(
                "telegram_bot.handlers.common.get_mentor_tasks_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await mentor_tasks(mock_callback, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_mentor_tasks_no_message(self, mock_callback, mock_auth_token):
        """Test mentor tasks with no message."""
        cb = MagicMock(spec=CallbackQuery)
        cb.message = None

        result = await mentor_tasks(cb, mock_auth_token, locale="en")
        assert result is None

    # Tests for progress
    async def test_progress_callback_no_user(self, mock_callback):
        """Test progress callback with no user."""
        await progress(mock_callback, None, "token", locale="en")

        mock_callback.answer.assert_called_once()

    async def test_progress_message_no_user(self, mock_message):
        """Test progress message with no user."""
        await progress(mock_message, None, "token", locale="en")

        mock_message.answer.assert_called_once()

    async def test_progress_no_checklists(self, mock_callback, mock_user, mock_auth_token):
        """Test progress with no checklists."""
        with patch(
            "telegram_bot.handlers.common.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
            return_value=[],
        ):
            await progress(mock_callback, mock_user, mock_auth_token, locale="en")

        # When no checklists, it uses msg.answer not edit_text
        mock_callback.message.answer.assert_called_once()

    async def test_progress_with_checklist(self, mock_callback, mock_user, mock_auth_token):
        """Test progress with checklist."""
        mock_checklists = [
            {
                "id": 1,
                "progress_percentage": 50,
                "completed_tasks": 5,
                "total_tasks": 10,
                "due_date": "2024-12-31T00:00:00",
            }
        ]

        with patch(
            "telegram_bot.handlers.common.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
            return_value=mock_checklists,
        ):
            with patch(
                "telegram_bot.handlers.common.checklists_client.get_checklist_progress",
                new_callable=AsyncMock,
                return_value={
                    "progress_percentage": 50,
                    "completed_tasks": 5,
                    "total_tasks": 10,
                    "start_date": "2024-01-01T00:00:00+00:00",  # UTC timezone-aware
                    "due_date": "2024-12-31T00:00:00",
                    "days_remaining": 30,
                },
            ):
                with patch(
                    "telegram_bot.handlers.common.checklists_client.get_checklist_tasks",
                    new_callable=AsyncMock,
                    return_value=[
                        {"title": "Task 1", "status": "pending"},
                    ],
                ):
                    with patch(
                        "telegram_bot.handlers.common.get_progress_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value.as_markup.return_value = MagicMock()

                        await progress(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_progress_with_checklist_no_progress_info(self, mock_callback, mock_user, mock_auth_token):
        """Test progress with checklist but no progress info."""
        mock_checklists = [
            {
                "id": 1,
                "progress_percentage": 50,
                "completed_tasks": 5,
                "total_tasks": 10,
                "due_date": "2024-12-31T00:00:00",
            }
        ]

        with patch(
            "telegram_bot.handlers.common.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
            return_value=mock_checklists,
        ):
            with patch(
                "telegram_bot.handlers.common.checklists_client.get_checklist_progress",
                new_callable=AsyncMock,
                return_value=None,
            ):
                with patch(
                    "telegram_bot.handlers.common.checklists_client.get_checklist_tasks",
                    new_callable=AsyncMock,
                    return_value=[],
                ):
                    with patch(
                        "telegram_bot.handlers.common.get_progress_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value.as_markup.return_value = MagicMock()

                        await progress(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_progress_with_checklist_invalid_date(self, mock_callback, mock_user, mock_auth_token):
        """Test progress with invalid date format."""
        mock_checklists = [
            {
                "id": 1,
                "progress_percentage": 50,
                "completed_tasks": 5,
                "total_tasks": 10,
                "due_date": "invalid-date",
            }
        ]

        with patch(
            "telegram_bot.handlers.common.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
            return_value=mock_checklists,
        ):
            with patch(
                "telegram_bot.handlers.common.checklists_client.get_checklist_progress",
                new_callable=AsyncMock,
                return_value=None,
            ):
                with patch(
                    "telegram_bot.handlers.common.checklists_client.get_checklist_tasks",
                    new_callable=AsyncMock,
                    return_value=[],
                ):
                    with patch(
                        "telegram_bot.handlers.common.get_progress_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value.as_markup.return_value = MagicMock()

                        await progress(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_progress_with_progress_info_invalid_due_date(self, mock_callback, mock_user, mock_auth_token):
        """Test progress with progress_info but invalid due_date (lines 359-360)."""
        mock_checklists = [
            {
                "id": 1,
                "progress_percentage": 50,
                "completed_tasks": 5,
                "total_tasks": 10,
            }
        ]

        with patch(
            "telegram_bot.handlers.common.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
            return_value=mock_checklists,
        ):
            with patch(
                "telegram_bot.handlers.common.checklists_client.get_checklist_progress",
                new_callable=AsyncMock,
                return_value={
                    "progress_percentage": 50,
                    "completed_tasks": 5,
                    "total_tasks": 10,
                    "start_date": "2024-01-01T00:00:00+00:00",
                    "due_date": "invalid-date-format",  # Invalid date triggers ValueError handling
                    "days_remaining": 30,
                },
            ):
                with patch(
                    "telegram_bot.handlers.common.checklists_client.get_checklist_tasks",
                    new_callable=AsyncMock,
                    return_value=[{"title": "Task 1", "status": "pending"}],
                ):
                    with patch(
                        "telegram_bot.handlers.common.get_progress_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value.as_markup.return_value = MagicMock()

                        await progress(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_progress_with_specific_checklist_id(self, mock_callback, mock_user, mock_auth_token):
        """Test progress with specific checklist ID in callback data."""
        mock_callback.data = "progress_2"
        mock_checklists = [
            {"id": 1, "progress_percentage": 30},
            {"id": 2, "progress_percentage": 60, "completed_tasks": 6, "total_tasks": 10},
        ]

        with patch(
            "telegram_bot.handlers.common.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
            return_value=mock_checklists,
        ):
            with patch(
                "telegram_bot.handlers.common.checklists_client.get_checklist_progress",
                new_callable=AsyncMock,
                return_value={
                    "progress_percentage": 60,
                    "completed_tasks": 6,
                    "total_tasks": 10,
                    "days_remaining": 20,
                },
            ):
                with patch(
                    "telegram_bot.handlers.common.checklists_client.get_checklist_tasks",
                    new_callable=AsyncMock,
                    return_value=[],
                ):
                    with patch(
                        "telegram_bot.handlers.common.get_progress_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value.as_markup.return_value = MagicMock()

                        await progress(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_progress_with_invalid_checklist_id(self, mock_callback, mock_user, mock_auth_token):
        """Test progress with invalid checklist ID - fallback to first."""
        mock_callback.data = "progress_999"
        mock_checklists = [
            {"id": 1, "progress_percentage": 30, "completed_tasks": 3, "total_tasks": 10},
        ]

        with patch(
            "telegram_bot.handlers.common.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
            return_value=mock_checklists,
        ):
            with patch(
                "telegram_bot.handlers.common.checklists_client.get_checklist_progress",
                new_callable=AsyncMock,
                return_value={
                    "progress_percentage": 30,
                    "completed_tasks": 3,
                    "total_tasks": 10,
                    "days_remaining": 20,
                },
            ):
                with patch(
                    "telegram_bot.handlers.common.checklists_client.get_checklist_tasks",
                    new_callable=AsyncMock,
                    return_value=[],
                ):
                    with patch(
                        "telegram_bot.handlers.common.get_progress_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value.as_markup.return_value = MagicMock()

                        await progress(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_progress_via_message(self, mock_message, mock_user, mock_auth_token):
        """Test progress via message (not callback)."""
        mock_checklists = [
            {
                "id": 1,
                "progress_percentage": 50,
                "completed_tasks": 5,
                "total_tasks": 10,
            }
        ]

        with patch(
            "telegram_bot.handlers.common.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
            return_value=mock_checklists,
        ):
            with patch(
                "telegram_bot.handlers.common.checklists_client.get_checklist_progress",
                new_callable=AsyncMock,
                return_value={
                    "progress_percentage": 50,
                    "completed_tasks": 5,
                    "total_tasks": 10,
                    "days_remaining": 20,
                },
            ):
                with patch(
                    "telegram_bot.handlers.common.checklists_client.get_checklist_tasks",
                    new_callable=AsyncMock,
                    return_value=[],
                ):
                    with patch(
                        "telegram_bot.handlers.common.get_progress_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value.as_markup.return_value = MagicMock()

                        await progress(mock_message, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_progress_no_message(self, mock_callback):
        """Test progress with no message."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "progress_1"  # Add valid checklist ID
        cb.answer = AsyncMock()
        cb.message = None
        user = {"id": 1}

        result = await progress(cb, user, "token", locale="en")
        assert result is None
