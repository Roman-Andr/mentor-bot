"""Extended unit tests for telegram_bot/handlers/checklists.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, Document, Message

from telegram_bot.handlers.checklists import (
    attach_task,
    complete_task,
    download_task_file,
    receive_task_description,
    receive_task_file,
    receive_task_file_invalid,
    receive_task_photo,
    show_checklist_tasks,
    show_checklists,
    show_task_attachments,
    show_task_detail,
    skip_description,
    start_task,
    task_info,
)
from telegram_bot.states.checklist_states import TaskAttachmentStates


class TestShowChecklists:
    """Test cases for show_checklists handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()
        self.mock_message.from_user = MagicMock()
        self.mock_message.from_user.id = 123456

        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "my_tasks"
        # Use spec=Message for callback.message so isinstance checks work
        self.mock_callback.message = MagicMock(spec=Message)
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_user = {"id": 1, "first_name": "John", "role": "USER"}
        self.auth_token = "test_token_123"  # noqa: S105

    async def test_show_checklists_no_auth(self):
        """Test show checklists without auth."""
        with patch(
            "telegram_bot.handlers.checklists._respond_with_auth_error",
            new_callable=AsyncMock,
        ) as mock_error:
            await show_checklists(self.mock_message, None, None, locale="en")
            mock_error.assert_called_once()

    async def test_show_checklists_empty(self):
        """Test show checklists with no checklists."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = []
            with patch(
                "telegram_bot.handlers.checklists.get_no_checklists_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await show_checklists(
                    self.mock_message, self.auth_token, self.mock_user, locale="en"
                )

                mock_get.assert_called_once_with(self.mock_user["id"], self.auth_token)
                self.mock_message.answer.assert_called_once()

    async def test_show_checklists_empty_callback(self):
        """Test show checklists with no checklists via callback (edit_text branch)."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = []
            with patch(
                "telegram_bot.handlers.checklists.get_no_checklists_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await show_checklists(
                    self.mock_callback, self.auth_token, self.mock_user, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()
                self.mock_callback.answer.assert_called_once()

    async def test_show_checklists_success(self):
        """Test show checklists with data."""
        checklists = [
            {"id": 1, "name": "Onboarding", "progress_percentage": 50, "completed_tasks": 5, "total_tasks": 10},
            {"id": 2, "name": "Training", "progress_percentage": 30, "completed_tasks": 3, "total_tasks": 10},
        ]

        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = checklists
            with patch(
                "telegram_bot.handlers.checklists.get_checklists_keyboard"
            ) as mock_kb:
                mock_kb.return_value = MagicMock()
                with patch(
                    "telegram_bot.handlers.checklists.format_checklist_progress",
                    return_value="Checklist info",
                ):

                    await show_checklists(
                        self.mock_message, self.auth_token, self.mock_user, locale="en"
                    )

                    self.mock_message.answer.assert_called_once()

    async def test_show_checklists_callback_success(self):
        """Test show checklists via callback."""
        checklists = [
            {"id": 1, "name": "Onboarding", "progress_percentage": 50, "completed_tasks": 5, "total_tasks": 10},
        ]

        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = checklists
            with patch(
                "telegram_bot.handlers.checklists.get_checklists_keyboard"
            ) as mock_kb:
                mock_kb.return_value = MagicMock()
                with patch(
                    "telegram_bot.handlers.checklists.format_checklist_progress",
                    return_value="Checklist info",
                ):

                    await show_checklists(
                        self.mock_callback, self.auth_token, self.mock_user, locale="en"
                    )

                    self.mock_callback.answer.assert_called_once()
                    self.mock_callback.message.edit_text.assert_called_once()

    async def test_show_checklists_many_items(self):
        """Test show checklists with more than max displayed."""
        checklists = [
            {"id": i, "name": f"Checklist {i}", "progress_percentage": 50, "completed_tasks": 5, "total_tasks": 10}
            for i in range(10)
        ]

        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = checklists
            with patch(
                "telegram_bot.handlers.checklists.get_checklists_keyboard"
            ) as mock_kb:
                mock_kb.return_value = MagicMock()
                with patch(
                    "telegram_bot.handlers.checklists.format_checklist_progress",
                    return_value="Checklist info",
                ):

                    await show_checklists(
                        self.mock_message, self.auth_token, self.mock_user, locale="en"
                    )

                    self.mock_message.answer.assert_called_once()


class TestShowChecklistTasks:
    """Test cases for show_checklist_tasks handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "checklist_1"
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_show_checklist_tasks_no_auth(self):
        """Test show checklist tasks without auth."""
        await show_checklist_tasks(self.mock_callback, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_show_checklist_tasks_empty(self):
        """Test show checklist tasks with no tasks."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
        ) as mock_get_cl:
            mock_get_cl.return_value = [{"id": 1, "name": "Test Checklist"}]
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.get_checklist_tasks",
                new_callable=AsyncMock,
            ) as mock_get_tasks:
                mock_get_tasks.return_value = []
                with patch(
                    "telegram_bot.handlers.checklists.get_no_tasks_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await show_checklist_tasks(
                        self.mock_callback, self.auth_token, locale="en"
                    )

                    self.mock_callback.message.edit_text.assert_called_once()

    async def test_show_checklist_tasks_no_current_checklist(self):
        """Test show checklist tasks when checklist not found in user's checklists."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
        ) as mock_get_cl:
            # Return checklists that don't include the requested one (checklist_1)
            mock_get_cl.return_value = [{"id": 999, "name": "Other Checklist"}]
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.get_checklist_tasks",
                new_callable=AsyncMock,
            ) as mock_get_tasks:
                mock_get_tasks.return_value = [
                    {"id": 1, "title": "Task 1", "status": "pending"},
                    {"id": 2, "title": "Task 2", "status": "completed"},
                ]
                with patch(
                    "telegram_bot.handlers.checklists.get_tasks_keyboard"
                ) as mock_kb:
                    mock_kb.return_value = MagicMock()

                    await show_checklist_tasks(
                        self.mock_callback, self.auth_token, locale="en"
                    )

                    # Should still work with generic title when checklist not found
                    self.mock_callback.message.edit_text.assert_called_once()
                    self.mock_callback.answer.assert_called_once()

    async def test_show_checklist_tasks_success(self):
        """Test show checklist tasks with data."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_user_checklists",
            new_callable=AsyncMock,
        ) as mock_get_cl:
            mock_get_cl.return_value = [
                {"id": 1, "name": "Test Checklist", "progress_percentage": 50, "completed_tasks": 5, "total_tasks": 10}
            ]
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.get_checklist_tasks",
                new_callable=AsyncMock,
            ) as mock_get_tasks:
                mock_get_tasks.return_value = [
                    {"id": 1, "title": "Task 1", "status": "pending"},
                    {"id": 2, "title": "Task 2", "status": "completed"},
                ]
                with patch(
                    "telegram_bot.handlers.checklists.get_tasks_keyboard"
                ) as mock_kb:
                    mock_kb.return_value = MagicMock()

                    await show_checklist_tasks(
                        self.mock_callback, self.auth_token, locale="en"
                    )

                    self.mock_callback.message.edit_text.assert_called_once()


class TestShowTaskDetail:
    """Test cases for show_task_detail handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "task_1_1"
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_show_task_detail_no_auth(self):
        """Test show task detail without auth."""
        await show_task_detail(self.mock_callback, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_show_task_detail_not_found(self):
        """Test show task detail when task not found."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.invalidate_task_cache",
            new_callable=AsyncMock,
        ):
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.get_assigned_tasks",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = [{"id": 999, "title": "Other Task"}]
                with patch(
                    "telegram_bot.handlers.checklists.checklists_client.get_checklist_tasks",
                    new_callable=AsyncMock,
                ) as mock_get_cl:
                    mock_get_cl.return_value = []

                    await show_task_detail(
                        self.mock_callback, self.auth_token, locale="en"
                    )

                    self.mock_callback.answer.assert_called_once()

    async def test_show_task_detail_found_in_checklist_tasks(self):
        """Test show task detail when task found in checklist tasks (lines 185-190)."""
        task = {"id": 1, "title": "Test Task", "description": "Desc", "status": "pending"}

        with patch(
            "telegram_bot.handlers.checklists.checklists_client.invalidate_task_cache",
            new_callable=AsyncMock,
        ):
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.get_assigned_tasks",
                new_callable=AsyncMock,
            ) as mock_get:
                # Task not found in assigned tasks initially
                mock_get.return_value = [{"id": 999, "title": "Other Task"}]
                with patch(
                    "telegram_bot.handlers.checklists.checklists_client.get_checklist_tasks",
                    new_callable=AsyncMock,
                ) as mock_get_cl:
                    # Task found in checklist tasks
                    mock_get_cl.return_value = [task]
                    with patch(
                        "telegram_bot.handlers.checklists.checklists_client.get_task_attachments",
                        new_callable=AsyncMock,
                    ) as mock_get_att:
                        mock_get_att.return_value = []
                        with patch(
                            "telegram_bot.handlers.checklists.format_task_detail",
                            return_value="Task detail",
                        ):
                            with patch(
                                "telegram_bot.handlers.checklists.get_task_detail_keyboard"
                            ) as mock_kb:
                                mock_kb.return_value = MagicMock()

                                await show_task_detail(
                                    self.mock_callback, self.auth_token, locale="en"
                                )

                                self.mock_callback.message.edit_text.assert_called_once()

    async def test_show_task_detail_success(self):
        """Test show task detail success."""
        task = {"id": 1, "title": "Test Task", "description": "Desc", "status": "pending"}

        with patch(
            "telegram_bot.handlers.checklists.checklists_client.invalidate_task_cache",
            new_callable=AsyncMock,
        ):
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.get_assigned_tasks",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = [task]
                with patch(
                    "telegram_bot.handlers.checklists.checklists_client.get_task_attachments",
                    new_callable=AsyncMock,
                ) as mock_get_att:
                    mock_get_att.return_value = [{"id": 1, "filename": "file.pdf"}]
                    with patch(
                        "telegram_bot.handlers.checklists.format_task_detail",
                        return_value="Task detail",
                    ):
                        with patch(
                            "telegram_bot.handlers.checklists.get_task_detail_keyboard"
                        ) as mock_kb:
                            mock_kb.return_value = MagicMock()

                            await show_task_detail(
                                self.mock_callback, self.auth_token, locale="en"
                            )

                            self.mock_callback.message.edit_text.assert_called_once()


class TestStartTask:
    """Test cases for start_task handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "start_task_1_1"
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_reply_markup = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_start_task_no_auth(self):
        """Test start task without auth."""
        await start_task(self.mock_callback, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_start_task_already_completed(self):
        """Test start task when already completed."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_assigned_tasks",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "status": "COMPLETED"}]

            await start_task(self.mock_callback, self.auth_token, locale="en")

            self.mock_callback.answer.assert_called_once()

    async def test_start_task_already_in_progress(self):
        """Test start task when already in progress."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_assigned_tasks",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "status": "IN_PROGRESS"}]
            with patch(
                "telegram_bot.handlers.checklists.get_task_detail_keyboard"
            ) as mock_kb:
                mock_kb.return_value = MagicMock()

                await start_task(self.mock_callback, self.auth_token, locale="en")

                self.mock_callback.answer.assert_called_once()

    async def test_start_task_success(self):
        """Test start task success."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_assigned_tasks",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "status": "PENDING"}]
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.start_task",
                new_callable=AsyncMock,
            ) as mock_start:
                mock_start.return_value = {"id": 1, "status": "IN_PROGRESS"}
                with patch(
                    "telegram_bot.handlers.checklists.checklists_client.invalidate_task_cache",
                    new_callable=AsyncMock,
                ):
                    with patch(
                        "telegram_bot.handlers.checklists.get_task_detail_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value = MagicMock()

                        await start_task(
                            self.mock_callback, self.auth_token, locale="en"
                        )

                        mock_start.assert_called_once_with(1, self.auth_token)

    async def test_start_task_failure(self):
        """Test start task failure."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_assigned_tasks",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "status": "PENDING"}]
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.start_task",
                new_callable=AsyncMock,
            ) as mock_start:
                mock_start.return_value = None

                await start_task(self.mock_callback, self.auth_token, locale="en")

                self.mock_callback.answer.assert_called_once()


class TestAttachTask:
    """Test cases for attach_task handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.data = "attach_task_1_1"
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.update_data = AsyncMock()
        self.mock_state.set_state = AsyncMock()

    async def test_attach_task_success(self):
        """Test attach task success."""
        with patch(
            "telegram_bot.handlers.checklists.get_attach_task_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await attach_task(self.mock_callback, self.mock_state, locale="en")

            self.mock_state.update_data.assert_called_once()
            self.mock_state.set_state.assert_called_once_with(
                TaskAttachmentStates.waiting_for_file
            )

    async def test_attach_task_no_message(self):
        """Test attach task with no message."""
        self.mock_callback.message = None

        await attach_task(self.mock_callback, self.mock_state, locale="en")

        self.mock_state.update_data.assert_not_called()

    async def test_attach_task_zero_checklist(self):
        """Test attach task with checklist_id 0."""
        self.mock_callback.data = "attach_task_1_0"

        with patch(
            "telegram_bot.handlers.checklists.get_attach_task_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await attach_task(self.mock_callback, self.mock_state, locale="en")

            self.mock_state.update_data.assert_called_once()


class TestCompleteTask:
    """Test cases for complete_task handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "complete_task_1_1"
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_user = {"id": 1, "first_name": "John"}
        self.auth_token = "test_token_123"  # noqa: S105

    async def test_complete_task_no_auth(self):
        """Test complete task without auth."""
        await complete_task(self.mock_callback, None, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_complete_task_success(self):
        """Test complete task success."""
        completed_task = {"id": 1, "title": "Test", "status": "COMPLETED"}

        with patch(
            "telegram_bot.handlers.checklists.checklists_client.complete_task",
            new_callable=AsyncMock,
        ) as mock_complete:
            mock_complete.return_value = completed_task
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.invalidate_task_cache",
                new_callable=AsyncMock,
            ):
                with patch(
                    "telegram_bot.handlers.checklists.format_task_detail",
                    return_value="Task detail",
                ):
                    with patch(
                        "telegram_bot.handlers.checklists.checklists_client.get_task_attachments",
                        new_callable=AsyncMock,
                    ) as mock_att:
                        mock_att.return_value = []
                        with patch(
                            "telegram_bot.handlers.checklists.get_task_completed_keyboard"
                        ) as mock_kb:
                            mock_kb.return_value.as_markup.return_value = MagicMock()

                            await complete_task(
                                self.mock_callback, self.auth_token, self.mock_user, locale="en"
                            )

                            mock_complete.assert_called_once()

    async def test_complete_task_failure(self):
        """Test complete task failure."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.complete_task",
            new_callable=AsyncMock,
        ) as mock_complete:
            mock_complete.return_value = None

            await complete_task(
                self.mock_callback, self.auth_token, self.mock_user, locale="en"
            )

            self.mock_callback.answer.assert_called_once()


class TestTaskInfo:
    """Test cases for task_info handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "task_info_1_1"
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_task_info_no_auth(self):
        """Test task info without auth."""
        await task_info(self.mock_callback, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_task_info_not_found(self):
        """Test task info when not found."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_task_details",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            await task_info(self.mock_callback, self.auth_token, locale="en")

            self.mock_callback.answer.assert_called_once()

    async def test_task_info_success(self):
        """Test task info success."""
        task = {
            "id": 1,
            "title": "Test Task",
            "description": "Desc",
            "status": "pending",
            "checklist_id": 1,
            "depends_on": [{"id": 2}],
            "assignee": "John Doe"
        }

        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_task_details",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = task
            with patch(
                "telegram_bot.handlers.checklists.format_task_detail",
                return_value="Task detail",
            ):
                with patch(
                    "telegram_bot.handlers.checklists.checklists_client.get_task_attachments",
                    new_callable=AsyncMock,
                ) as mock_att:
                    mock_att.return_value = [{"id": 1, "filename": "file.pdf"}]
                    with patch(
                        "telegram_bot.handlers.checklists.get_task_info_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value.as_markup.return_value = MagicMock()

                        await task_info(
                            self.mock_callback, self.auth_token, locale="en"
                        )

                        self.mock_callback.message.edit_text.assert_called_once()


class TestReceiveTaskFile:
    """Test cases for receive_task_file handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()
        self.mock_message.document = MagicMock(spec=Document)
        self.mock_message.document.file_size = 1024
        self.mock_message.document.file_id = "file_123"
        self.mock_message.document.file_name = "test.pdf"

        self.mock_state = MagicMock()
        self.mock_state.update_data = AsyncMock()
        self.mock_state.set_state = AsyncMock()
        self.mock_state.clear = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_receive_task_file_no_auth(self):
        """Test receive task file without auth."""
        await receive_task_file(self.mock_message, self.mock_state, None, locale="en")
        self.mock_state.clear.assert_called_once()

    async def test_receive_task_file_no_document(self):
        """Test receive task file with no document."""
        self.mock_message.document = None

        await receive_task_file(self.mock_message, self.mock_state, self.auth_token, locale="en")
        self.mock_message.answer.assert_called_once()

    async def test_receive_task_file_too_large(self):
        """Test receive task file too large."""
        self.mock_message.document.file_size = 20 * 1024 * 1024  # 20 MB

        await receive_task_file(self.mock_message, self.mock_state, self.auth_token, locale="en")
        self.mock_message.answer.assert_called_once()

    async def test_receive_task_file_success(self):
        """Test receive task file success."""
        with patch(
            "telegram_bot.handlers.checklists.get_skip_description_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await receive_task_file(
                self.mock_message, self.mock_state, self.auth_token, locale="en"
            )

            self.mock_state.update_data.assert_called_once()
            self.mock_state.set_state.assert_called_once()


class TestReceiveTaskPhoto:
    """Test cases for receive_task_photo handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()

        # Mock photo array (largest last)
        mock_photo = MagicMock()
        mock_photo.file_size = 1024
        mock_photo.file_id = "photo_123"
        self.mock_message.photo = [mock_photo]

        self.mock_state = MagicMock()
        self.mock_state.update_data = AsyncMock()
        self.mock_state.set_state = AsyncMock()
        self.mock_state.clear = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_receive_task_photo_no_auth(self):
        """Test receive task photo without auth."""
        await receive_task_photo(self.mock_message, self.mock_state, None, locale="en")
        self.mock_state.clear.assert_called_once()

    async def test_receive_task_photo_no_photo(self):
        """Test receive task photo with no photo."""
        self.mock_message.photo = None

        await receive_task_photo(
            self.mock_message, self.mock_state, self.auth_token, locale="en"
        )
        self.mock_message.answer.assert_called_once()

    async def test_receive_task_photo_too_large(self):
        """Test receive task photo too large."""
        mock_photo = MagicMock()
        mock_photo.file_size = 20 * 1024 * 1024  # 20 MB
        self.mock_message.photo = [mock_photo]

        await receive_task_photo(
            self.mock_message, self.mock_state, self.auth_token, locale="en"
        )
        self.mock_message.answer.assert_called_once()

    async def test_receive_task_photo_success(self):
        """Test receive task photo success."""
        with patch(
            "telegram_bot.handlers.checklists.get_skip_description_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await receive_task_photo(
                self.mock_message, self.mock_state, self.auth_token, locale="en"
            )

            self.mock_state.update_data.assert_called_once()
            self.mock_state.set_state.assert_called_once()


class TestReceiveTaskFileInvalid:
    """Test cases for receive_task_file_invalid handler."""

    async def test_receive_task_file_invalid(self):
        """Test receive invalid file type."""
        mock_message = MagicMock(spec=Message)
        mock_message.answer = AsyncMock()

        mock_state = MagicMock()

        await receive_task_file_invalid(mock_message, mock_state, locale="en")

        mock_message.answer.assert_called_once()


class TestReceiveTaskDescription:
    """Test cases for receive_task_description handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()
        self.mock_message.text = "File description"
        self.mock_message.bot = MagicMock()
        self.mock_message.bot.get_file = AsyncMock(
            return_value=MagicMock(file_path="path/to/file")
        )
        self.mock_message.bot.download_file = AsyncMock(return_value=b"file content")

        self.mock_state = MagicMock()
        self.mock_state.get_data = AsyncMock(return_value={
            "attach_task_id": 1,
            "attach_checklist_id": 1,
            "attach_file_id": "file_123",
            "attach_filename": "test.pdf",
        })
        self.mock_state.clear = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_receive_task_description_no_auth(self):
        """Test receive description without auth."""
        await receive_task_description(self.mock_message, self.mock_state, None, locale="en")
        self.mock_state.clear.assert_called_once()

    async def test_receive_task_description_no_task_data(self):
        """Test receive description with no task data."""
        self.mock_state.get_data = AsyncMock(return_value={})

        await receive_task_description(self.mock_message, self.mock_state, self.auth_token, locale="en")
        self.mock_message.answer.assert_called_once()

    async def test_receive_task_description_download_error(self):
        """Test receive description with download error."""
        self.mock_message.bot.get_file = AsyncMock(
            side_effect=Exception("Download failed")
        )

        await receive_task_description(
            self.mock_message, self.mock_state, self.auth_token, locale="en"
        )
        self.mock_message.answer.assert_called_once()

    async def test_receive_task_description_success(self):
        """Test receive description success."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.upload_task_attachment",
            new_callable=AsyncMock,
        ) as mock_upload:
            mock_upload.return_value = {"id": 1}
            with patch(
                "telegram_bot.handlers.checklists.get_back_to_task_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await receive_task_description(
                    self.mock_message, self.mock_state, self.auth_token, locale="en"
                )

                mock_upload.assert_called_once()
                self.mock_state.clear.assert_called_once()

    async def test_receive_task_description_upload_failure(self):
        """Test receive description with upload failure."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.upload_task_attachment",
            new_callable=AsyncMock,
        ) as mock_upload:
            mock_upload.return_value = None

            await receive_task_description(
                self.mock_message, self.mock_state, self.auth_token, locale="en"
            )

            mock_upload.assert_called_once()


class TestSkipDescription:
    """Test cases for skip_description handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.data = "skip_description"
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()
        self.mock_callback.bot = MagicMock()
        self.mock_callback.bot.get_file = AsyncMock(
            return_value=MagicMock(file_path="path/to/file")
        )
        self.mock_callback.bot.download_file = AsyncMock(return_value=b"file content")

        self.mock_state = MagicMock()
        self.mock_state.get_data = AsyncMock(return_value={
            "attach_task_id": 1,
            "attach_checklist_id": 1,
            "attach_file_id": "file_123",
            "attach_filename": "test.pdf",
        })
        self.mock_state.clear = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_skip_description_no_auth(self):
        """Test skip description without auth."""
        await skip_description(self.mock_callback, self.mock_state, None, locale="en")
        self.mock_state.clear.assert_called_once()

    async def test_skip_description_no_task_data(self):
        """Test skip description with no task data."""
        self.mock_state.get_data = AsyncMock(return_value={})

        await skip_description(
            self.mock_callback, self.mock_state, self.auth_token, locale="en"
        )
        self.mock_callback.answer.assert_called_once()

    async def test_skip_description_download_error(self):
        """Test skip description with download error."""
        self.mock_callback.bot.get_file = AsyncMock(
            side_effect=Exception("Download failed")
        )

        await skip_description(
            self.mock_callback, self.mock_state, self.auth_token, locale="en"
        )
        self.mock_callback.answer.assert_called_once()

    async def test_skip_description_success(self):
        """Test skip description success."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.upload_task_attachment",
            new_callable=AsyncMock,
        ) as mock_upload:
            mock_upload.return_value = {"id": 1}
            with patch(
                "telegram_bot.handlers.checklists.get_back_to_task_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await skip_description(
                    self.mock_callback, self.mock_state, self.auth_token, locale="en"
                )

                mock_upload.assert_called_once()

    async def test_skip_description_upload_failure(self):
        """Test skip description with upload failure."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.upload_task_attachment",
            new_callable=AsyncMock,
        ) as mock_upload:
            mock_upload.return_value = None

            await skip_description(
                self.mock_callback, self.mock_state, self.auth_token, locale="en"
            )

            # Handler calls answer() for error alert, then at the end of handler
            assert self.mock_callback.answer.call_count >= 1
            # Verify the error message was shown
            error_call_found = any(
                call.args and "tasks.attachment_failed" in str(call.args[0])
                for call in self.mock_callback.answer.call_args_list
            )
            assert error_call_found


class TestShowTaskAttachments:
    """Test cases for show_task_attachments handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "task_files_1_1"
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_show_task_attachments_no_auth(self):
        """Test show attachments without auth."""
        await show_task_attachments(self.mock_callback, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_show_task_attachments_empty(self):
        """Test show attachments with no attachments."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_task_attachments",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = []

            await show_task_attachments(
                self.mock_callback, self.auth_token, locale="en"
            )

            self.mock_callback.answer.assert_called_once()

    async def test_show_task_attachments_success(self):
        """Test show attachments success."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_task_attachments",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [
                {"id": 1, "filename": "file1.pdf"},
                {"id": 2, "filename": "file2.doc"},
            ]
            with patch(
                "telegram_bot.handlers.checklists.get_task_attachments_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await show_task_attachments(
                    self.mock_callback, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()


class TestDownloadTaskFile:
    """Test cases for download_task_file handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "download_task_file_1_1_1"
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.answer_document = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_download_task_file_no_auth(self):
        """Test download file without auth."""
        await download_task_file(self.mock_callback, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_download_task_file_not_found(self):
        """Test download file when attachment not found."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_task_attachments",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 999, "filename": "other.pdf"}]

            await download_task_file(
                self.mock_callback, self.auth_token, locale="en"
            )

            self.mock_callback.answer.assert_called_once()

    async def test_download_task_file_success(self):
        """Test download file success."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_task_attachments",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "filename": "file.pdf"}]
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.download_task_attachment",
                new_callable=AsyncMock,
            ) as mock_dl:
                mock_dl.return_value = b"file content"

                await download_task_file(
                    self.mock_callback, self.auth_token, locale="en"
                )

                self.mock_callback.message.answer_document.assert_called_once()

    async def test_download_task_file_no_data(self):
        """Test download file when download returns None."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_task_attachments",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "filename": "file.pdf"}]
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.download_task_attachment",
                new_callable=AsyncMock,
            ) as mock_dl:
                mock_dl.return_value = None

                await download_task_file(
                    self.mock_callback, self.auth_token, locale="en"
                )

                # Handler calls answer() for loading, then for error alert
                assert self.mock_callback.answer.call_count >= 2
                # Verify the loading message was shown
                loading_call_found = any(
                    call.args and "common.loading" in str(call.args[0])
                    for call in self.mock_callback.answer.call_args_list
                )
                assert loading_call_found

    async def test_download_task_file_send_error(self):
        """Test download file with send error."""
        with patch(
            "telegram_bot.handlers.checklists.checklists_client.get_task_attachments",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "filename": "file.pdf"}]
            with patch(
                "telegram_bot.handlers.checklists.checklists_client.download_task_attachment",
                new_callable=AsyncMock,
            ) as mock_dl:
                mock_dl.return_value = b"file content"
                self.mock_callback.message.answer_document = AsyncMock(
                    side_effect=Exception("Send failed")
                )

                await download_task_file(
                    self.mock_callback, self.auth_token, locale="en"
                )

                # Handler calls answer() for loading, then for error alert on exception
                assert self.mock_callback.answer.call_count >= 2
                # Verify the loading message was shown
                loading_call_found = any(
                    call.args and "common.loading" in str(call.args[0])
                    for call in self.mock_callback.answer.call_args_list
                )
                assert loading_call_found
