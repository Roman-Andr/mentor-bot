"""Unit tests for telegram_bot/handlers/admin.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, Message

from telegram_bot.handlers.admin import (
    add_user,
    admin_alerts,
    admin_checklists,
    admin_panel,
    admin_reports,
    admin_settings,
    admin_stats,
    admin_users,
    checklist_progress,
    cmd_admin,
    detailed_report,
    export_data,
    list_templates,
    list_users,
    overdue_tasks,
    send_invite,
)


class TestAdminHandlers:
    """Test cases for admin handlers."""

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
        cb.answer = AsyncMock()
        msg_mock = MagicMock()
        msg_mock.edit_text = AsyncMock()
        cb.message = msg_mock
        return cb

    @pytest.fixture
    def mock_admin_user(self):
        """Create a mock admin user."""
        return {"id": 1, "first_name": "Admin", "role": "ADMIN"}

    @pytest.fixture
    def mock_hr_user(self):
        """Create a mock HR user."""
        return {"id": 2, "first_name": "HR", "role": "HR"}

    @pytest.fixture
    def mock_regular_user(self):
        """Create a mock regular user."""
        return {"id": 3, "first_name": "User", "role": "NEWBIE"}

    @pytest.fixture
    def mock_auth_token(self):
        """Create a mock auth token."""
        return "test_auth_token_123"

    # Tests for cmd_admin
    async def test_cmd_admin_as_admin(self, mock_message, mock_admin_user):
        """Test admin command as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_admin_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await cmd_admin(mock_message, mock_admin_user, locale="en")

        mock_message.answer.assert_called_once()

    async def test_cmd_admin_as_hr(self, mock_message, mock_hr_user):
        """Test admin command as HR."""
        with patch(
            "telegram_bot.handlers.admin.get_admin_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await cmd_admin(mock_message, mock_hr_user, locale="en")

        mock_message.answer.assert_called_once()

    async def test_cmd_admin_as_regular_user(self, mock_message, mock_regular_user):
        """Test admin command as regular user - should be denied."""
        await cmd_admin(mock_message, mock_regular_user, locale="en")

        mock_message.answer.assert_called_once()
        assert "[common.access_denied]" in mock_message.answer.call_args[0][0]

    async def test_cmd_admin_no_user(self, mock_message):
        """Test admin command with no user."""
        await cmd_admin(mock_message, None, locale="en")

        mock_message.answer.assert_called_once()
        assert "[common.access_denied]" in mock_message.answer.call_args[0][0]

    # Tests for admin_panel
    async def test_admin_panel_as_admin(self, mock_callback, mock_admin_user):
        """Test admin panel callback as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_admin_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await admin_panel(mock_callback, mock_admin_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_admin_panel_as_regular_user(self, mock_callback, mock_regular_user):
        """Test admin panel callback as regular user."""
        await admin_panel(mock_callback, mock_regular_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for admin_stats
    async def test_admin_stats_success(self, mock_callback, mock_admin_user, mock_auth_token):
        """Test admin stats with successful data fetch."""
        with patch(
            "telegram_bot.handlers.admin.auth_client.get_total_users",
            new_callable=AsyncMock,
            return_value=100,
        ):
            with patch(
                "telegram_bot.handlers.admin.checklists_client.get_admin_stats",
                new_callable=AsyncMock,
                return_value={
                    "active_checklists": 50,
                    "completed_tasks": 200,
                    "pending_tasks": 100,
                    "avg_onboarding_days": 15,
                },
            ):
                with patch(
                    "telegram_bot.handlers.admin.get_admin_stats_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await admin_stats(
                        mock_callback, mock_admin_user, mock_auth_token, locale="en"
                    )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_admin_stats_unauthorized(self, mock_callback, mock_regular_user, mock_auth_token):
        """Test admin stats as regular user."""
        await admin_stats(mock_callback, mock_regular_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for admin_users
    async def test_admin_users_as_admin(self, mock_callback, mock_admin_user):
        """Test admin users as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_admin_users_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await admin_users(mock_callback, mock_admin_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_admin_users_unauthorized(self, mock_callback, mock_regular_user):
        """Test admin users as regular user."""
        await admin_users(mock_callback, mock_regular_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for admin_checklists
    async def test_admin_checklists_as_admin(self, mock_callback, mock_admin_user):
        """Test admin checklists as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_admin_checklists_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await admin_checklists(mock_callback, mock_admin_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_admin_checklists_unauthorized(self, mock_callback, mock_regular_user):
        """Test admin checklists as regular user."""
        await admin_checklists(mock_callback, mock_regular_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for list_users
    async def test_list_users_with_data(self, mock_callback, mock_admin_user, mock_auth_token):
        """Test list users with data."""
        mock_users_data = {
            "users": [
                {"first_name": "John", "last_name": "Doe", "role": "ADMIN"},
                {"first_name": "Jane", "last_name": "Smith", "role": "NEWBIE"},
            ],
            "total": 2,
        }

        with patch(
            "telegram_bot.handlers.admin.auth_client.list_users",
            new_callable=AsyncMock,
            return_value=mock_users_data,
        ):
            with patch(
                "telegram_bot.handlers.admin.get_back_to_admin_users_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await list_users(
                    mock_callback, mock_admin_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_list_users_empty(self, mock_callback, mock_admin_user, mock_auth_token):
        """Test list users with no data."""
        with patch(
            "telegram_bot.handlers.admin.auth_client.list_users",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with patch(
                "telegram_bot.handlers.admin.get_back_to_admin_users_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await list_users(
                    mock_callback, mock_admin_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()

    async def test_list_users_unauthorized(self, mock_callback, mock_regular_user, mock_auth_token):
        """Test list users as regular user."""
        await list_users(mock_callback, mock_regular_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for add_user
    async def test_add_user_as_admin(self, mock_callback, mock_admin_user):
        """Test add user as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_back_to_admin_users_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await add_user(mock_callback, mock_admin_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_add_user_unauthorized(self, mock_callback, mock_regular_user):
        """Test add user as regular user."""
        await add_user(mock_callback, mock_regular_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for send_invite
    async def test_send_invite_as_admin(self, mock_callback, mock_admin_user):
        """Test send invite as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_back_to_admin_users_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await send_invite(mock_callback, mock_admin_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_send_invite_unauthorized(self, mock_callback, mock_regular_user):
        """Test send invite as regular user."""
        await send_invite(mock_callback, mock_regular_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for list_templates
    async def test_list_templates_with_data(self, mock_callback, mock_admin_user, mock_auth_token):
        """Test list templates with data."""
        mock_templates = [
            {"name": "Template 1", "total_tasks": 5},
            {"name": "Template 2", "total_tasks": 10},
        ]

        with patch(
            "telegram_bot.handlers.admin.checklists_client.get_templates",
            new_callable=AsyncMock,
            return_value=mock_templates,
        ):
            with patch(
                "telegram_bot.handlers.admin.get_back_to_admin_checklists_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await list_templates(
                    mock_callback, mock_admin_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_list_templates_empty(self, mock_callback, mock_admin_user, mock_auth_token):
        """Test list templates with no data."""
        with patch(
            "telegram_bot.handlers.admin.checklists_client.get_templates",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with patch(
                "telegram_bot.handlers.admin.get_back_to_admin_checklists_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await list_templates(
                    mock_callback, mock_admin_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()

    async def test_list_templates_unauthorized(self, mock_callback, mock_regular_user, mock_auth_token):
        """Test list templates as regular user."""
        await list_templates(mock_callback, mock_regular_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for checklist_progress
    async def test_checklist_progress_success(self, mock_callback, mock_admin_user, mock_auth_token):
        """Test checklist progress as admin."""
        mock_stats = {
            "active_checklists": 10,
            "completed_tasks": 50,
            "pending_tasks": 20,
        }

        with patch(
            "telegram_bot.handlers.admin.checklists_client.get_admin_stats",
            new_callable=AsyncMock,
            return_value=mock_stats,
        ):
            with patch(
                "telegram_bot.handlers.admin.get_back_to_admin_checklists_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await checklist_progress(
                    mock_callback, mock_admin_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_checklist_progress_unauthorized(self, mock_callback, mock_regular_user, mock_auth_token):
        """Test checklist progress as regular user."""
        await checklist_progress(mock_callback, mock_regular_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for overdue_tasks
    async def test_overdue_tasks_with_data(self, mock_callback, mock_admin_user, mock_auth_token):
        """Test overdue tasks with data."""
        mock_tasks = [
            {"title": "Task 1", "due_date": "2024-01-01"},
            {"title": "Task 2", "due_date": "2024-01-02"},
        ]

        with patch(
            "telegram_bot.handlers.admin.checklists_client.get_overdue_tasks",
            new_callable=AsyncMock,
            return_value=mock_tasks,
        ):
            with patch(
                "telegram_bot.handlers.admin.get_back_to_admin_checklists_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await overdue_tasks(
                    mock_callback, mock_admin_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_overdue_tasks_empty(self, mock_callback, mock_admin_user, mock_auth_token):
        """Test overdue tasks with no data."""
        with patch(
            "telegram_bot.handlers.admin.checklists_client.get_overdue_tasks",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with patch(
                "telegram_bot.handlers.admin.get_back_to_admin_checklists_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await overdue_tasks(
                    mock_callback, mock_admin_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()

    async def test_overdue_tasks_unauthorized(self, mock_callback, mock_regular_user, mock_auth_token):
        """Test overdue tasks as regular user."""
        await overdue_tasks(mock_callback, mock_regular_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for admin_settings
    async def test_admin_settings_as_admin(self, mock_callback, mock_admin_user):
        """Test admin settings as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_back_to_admin_panel_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await admin_settings(mock_callback, mock_admin_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_admin_settings_unauthorized(self, mock_callback, mock_regular_user):
        """Test admin settings as regular user."""
        await admin_settings(mock_callback, mock_regular_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for admin_reports
    async def test_admin_reports_as_admin(self, mock_callback, mock_admin_user):
        """Test admin reports as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_back_to_admin_panel_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await admin_reports(mock_callback, mock_admin_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_admin_reports_unauthorized(self, mock_callback, mock_regular_user):
        """Test admin reports as regular user."""
        await admin_reports(mock_callback, mock_regular_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for admin_alerts
    async def test_admin_alerts_as_admin(self, mock_callback, mock_admin_user):
        """Test admin alerts as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_back_to_admin_panel_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await admin_alerts(mock_callback, mock_admin_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_admin_alerts_unauthorized(self, mock_callback, mock_regular_user):
        """Test admin alerts as regular user."""
        await admin_alerts(mock_callback, mock_regular_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for detailed_report
    async def test_detailed_report_as_admin(self, mock_callback, mock_admin_user):
        """Test detailed report as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_back_to_admin_stats_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await detailed_report(mock_callback, mock_admin_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_detailed_report_unauthorized(self, mock_callback, mock_regular_user):
        """Test detailed report as regular user."""
        await detailed_report(mock_callback, mock_regular_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    # Tests for export_data
    async def test_export_data_as_admin(self, mock_callback, mock_admin_user):
        """Test export data as admin."""
        with patch(
            "telegram_bot.handlers.admin.get_back_to_admin_stats_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await export_data(mock_callback, mock_admin_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_export_data_unauthorized(self, mock_callback, mock_regular_user):
        """Test export data as regular user."""
        await export_data(mock_callback, mock_regular_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs
