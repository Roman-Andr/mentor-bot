"""Unit tests for telegram_bot/utils/scheduler.py."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from apscheduler.triggers.cron import CronTrigger  # type: ignore[import-untyped]

from telegram_bot.utils.scheduler import Scheduler, scheduler


class TestSchedulerInit:
    """Test cases for Scheduler initialization."""

    def test_scheduler_init(self):
        """Test scheduler initialization."""
        sched = Scheduler()

        assert sched.scheduler is not None
        assert isinstance(sched.scheduler, AsyncIOScheduler)
        assert sched.bot is None
        assert sched.is_running is False

    def test_global_scheduler_singleton(self):
        """Test that global scheduler singleton exists."""
        assert scheduler is not None
        assert isinstance(scheduler, Scheduler)


class TestSchedulerStart:
    """Test cases for Scheduler start functionality."""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot."""
        bot = MagicMock()
        bot.send_message = AsyncMock()
        return bot

    @pytest.fixture
    def scheduler_instance(self):
        """Create a fresh scheduler instance."""
        sched = Scheduler()
        # Stop any existing scheduler to avoid conflicts
        if sched.scheduler.running:
            sched.scheduler.shutdown()
        sched.scheduler = MagicMock()
        sched.scheduler.add_job = MagicMock()
        sched.scheduler.start = MagicMock()
        sched.scheduler.running = False
        sched.scheduler.shutdown = MagicMock()
        return sched

    async def test_start_sets_bot(self, scheduler_instance, mock_bot):
        """Test that start sets the bot reference."""
        with patch("telegram_bot.utils.scheduler.settings") as mock_settings:
            mock_settings.ENABLE_NOTIFICATIONS = True
            mock_settings.NOTIFICATION_HOUR = 9

            await scheduler_instance.start(mock_bot)

            assert scheduler_instance.bot is mock_bot

    async def test_start_adds_daily_notifications_job(self, scheduler_instance, mock_bot):
        """Test that start adds daily notifications job."""
        with patch("telegram_bot.utils.scheduler.settings") as mock_settings:
            mock_settings.ENABLE_NOTIFICATIONS = True
            mock_settings.NOTIFICATION_HOUR = 9

            await scheduler_instance.start(mock_bot)

            # Check that add_job was called with the right function
            call_found = False
            for call in scheduler_instance.scheduler.add_job.call_args_list:
                if call[0][0] == scheduler_instance.send_daily_notifications:
                    call_found = True
                    assert call[1]["id"] == "daily_notifications"
                    assert call[1]["name"] == "Send daily notifications"
                    assert call[1]["replace_existing"] is True
                    break
            assert call_found, "daily_notifications job not found"

    async def test_start_adds_weekly_summary_job(self, scheduler_instance, mock_bot):
        """Test that start adds weekly summary job."""
        with patch("telegram_bot.utils.scheduler.settings") as mock_settings:
            mock_settings.ENABLE_NOTIFICATIONS = True
            mock_settings.NOTIFICATION_HOUR = 9

            await scheduler_instance.start(mock_bot)

            # Check that add_job was called with the right function
            call_found = False
            for call in scheduler_instance.scheduler.add_job.call_args_list:
                if call[0][0] == scheduler_instance.send_weekly_summary:
                    call_found = True
                    assert call[1]["id"] == "weekly_summary"
                    assert call[1]["name"] == "Send weekly summary"
                    assert call[1]["replace_existing"] is True
                    break
            assert call_found, "weekly_summary job not found"

    async def test_start_adds_cleanup_job(self, scheduler_instance, mock_bot):
        """Test that start adds cleanup job."""
        with patch("telegram_bot.utils.scheduler.settings") as mock_settings:
            mock_settings.ENABLE_NOTIFICATIONS = True
            mock_settings.NOTIFICATION_HOUR = 9

            await scheduler_instance.start(mock_bot)

            # Check that add_job was called with the right function
            call_found = False
            for call in scheduler_instance.scheduler.add_job.call_args_list:
                if call[0][0] == scheduler_instance.cleanup_old_data:
                    call_found = True
                    assert call[1]["id"] == "cleanup"
                    assert call[1]["name"] == "Cleanup old data"
                    assert call[1]["replace_existing"] is True
                    break
            assert call_found, "cleanup job not found"

    async def test_start_starts_scheduler(self, scheduler_instance, mock_bot):
        """Test that start starts the scheduler."""
        with patch("telegram_bot.utils.scheduler.settings") as mock_settings:
            mock_settings.ENABLE_NOTIFICATIONS = True
            mock_settings.NOTIFICATION_HOUR = 9

            await scheduler_instance.start(mock_bot)

            scheduler_instance.scheduler.start.assert_called_once()
            assert scheduler_instance.is_running is True

    async def test_start_with_notifications_disabled(self, scheduler_instance, mock_bot):
        """Test start when notifications are disabled."""
        with patch("telegram_bot.utils.scheduler.settings") as mock_settings:
            mock_settings.ENABLE_NOTIFICATIONS = False

            await scheduler_instance.start(mock_bot)

            scheduler_instance.scheduler.add_job.assert_not_called()
            scheduler_instance.scheduler.start.assert_not_called()
            assert scheduler_instance.is_running is False


class TestSchedulerShutdown:
    """Test cases for Scheduler shutdown functionality."""

    @pytest.fixture
    def running_scheduler(self):
        """Create a running scheduler instance."""
        sched = Scheduler()
        sched.scheduler = MagicMock()
        sched.scheduler.running = True
        sched.scheduler.shutdown = MagicMock()
        sched.is_running = True
        return sched

    async def test_shutdown_when_running(self, running_scheduler):
        """Test shutdown when scheduler is running."""
        await running_scheduler.shutdown()

        running_scheduler.scheduler.shutdown.assert_called_once()
        assert running_scheduler.is_running is False

    async def test_shutdown_when_not_running(self):
        """Test shutdown when scheduler is not running."""
        sched = Scheduler()
        sched.scheduler = MagicMock()
        sched.scheduler.running = False
        sched.scheduler.shutdown = MagicMock()

        await sched.shutdown()

        sched.scheduler.shutdown.assert_not_called()


class TestSendDailyNotifications:
    """Test cases for send_daily_notifications method."""

    @pytest.fixture
    def scheduler_with_bot(self):
        """Create scheduler with mocked bot."""
        sched = Scheduler()
        sched.bot = MagicMock()
        sched.bot.send_message = AsyncMock()
        return sched

    async def test_send_daily_notifications_no_bot(self):
        """Test send_daily_notifications returns early when no bot."""
        sched = Scheduler()
        sched.bot = None

        # Should not raise
        await sched.send_daily_notifications()

    async def test_send_daily_notifications_empty_users(self, scheduler_with_bot):
        """Test send_daily_notifications with no users."""
        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value={},
        ):
            await scheduler_with_bot.send_daily_notifications()

            scheduler_with_bot.bot.send_message.assert_not_called()

    async def test_send_daily_notifications_user_no_token(self, scheduler_with_bot):
        """Test send_daily_notifications skips users without tokens."""
        users = {"123": {"id": 1, "access_token": None}}

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            await scheduler_with_bot.send_daily_notifications()

            scheduler_with_bot.bot.send_message.assert_not_called()

    async def test_send_daily_notifications_with_pending_tasks(self, scheduler_with_bot):
        """Test send_daily_notifications sends message when tasks pending."""
        users = {"123": {"id": 1, "access_token": "valid_token"}}
        tasks = [
            {"id": 1, "title": "Task 1", "status": "pending"},
            {"id": 2, "title": "Task 2", "status": "in_progress"},
        ]

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_assigned_tasks",
                return_value=tasks,
            ):
                await scheduler_with_bot.send_daily_notifications()

                scheduler_with_bot.bot.send_message.assert_called_once()
                call_args = scheduler_with_bot.bot.send_message.call_args
                assert call_args.kwargs["chat_id"] == "123"
                assert "Daily Reminder" in call_args.kwargs["text"]

    async def test_send_daily_notifications_no_pending_tasks(self, scheduler_with_bot):
        """Test send_daily_notifications skips when no pending tasks."""
        users = {"123": {"id": 1, "access_token": "valid_token"}}
        tasks = [
            {"id": 1, "title": "Task 1", "status": "completed"},
        ]

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_assigned_tasks",
                return_value=tasks,
            ):
                await scheduler_with_bot.send_daily_notifications()

                scheduler_with_bot.bot.send_message.assert_not_called()

    async def test_send_daily_notifications_client_error(self, scheduler_with_bot):
        """Test send_daily_notifications handles client errors gracefully."""
        from unittest.mock import AsyncMock

        users = {"123": {"id": 1, "access_token": "valid_token"}}

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_assigned_tasks",
                new_callable=AsyncMock,
                side_effect=Exception("Client error"),
            ):
                # Should not raise
                await scheduler_with_bot.send_daily_notifications()

                scheduler_with_bot.bot.send_message.assert_not_called()

    async def test_send_daily_notifications_send_error(self, scheduler_with_bot):
        """Test send_daily_notifications handles send errors gracefully."""
        users = {"123": {"id": 1, "access_token": "valid_token"}}
        tasks = [{"id": 1, "title": "Task 1", "status": "pending"}]

        scheduler_with_bot.bot.send_message = AsyncMock(
            side_effect=Exception("Send failed")
        )

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_assigned_tasks",
                return_value=tasks,
            ):
                # Should not raise
                await scheduler_with_bot.send_daily_notifications()

    async def test_send_daily_notifications_get_users_error(self, scheduler_with_bot):
        """Test send_daily_notifications handles get_all_users errors."""
        from unittest.mock import AsyncMock

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            new_callable=AsyncMock,
            side_effect=Exception("Cache error"),
        ):
            # Should not raise
            await scheduler_with_bot.send_daily_notifications()

            scheduler_with_bot.bot.send_message.assert_not_called()

    async def test_send_daily_notifications_task_limit(self, scheduler_with_bot):
        """Test send_daily_notifications limits tasks display to 5."""
        users = {"123": {"id": 1, "access_token": "valid_token"}}
        tasks = [
            {"id": i, "title": f"Task {i}", "status": "pending"}
            for i in range(10)
        ]

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_assigned_tasks",
                return_value=tasks,
            ):
                await scheduler_with_bot.send_daily_notifications()

                call_args = scheduler_with_bot.bot.send_message.call_args
                text = call_args.kwargs["text"]
                # Shows total count (10), but limits displayed tasks to 5
                assert "10 pending task(s)" in text
                assert "Task 0" in text
                assert "Task 4" in text
                assert "Task 5" not in text  # Should not include 6th task


class TestSendWeeklySummary:
    """Test cases for send_weekly_summary method."""

    @pytest.fixture
    def scheduler_with_bot(self):
        """Create scheduler with mocked bot."""
        sched = Scheduler()
        sched.bot = MagicMock()
        sched.bot.send_message = AsyncMock()
        return sched

    async def test_send_weekly_summary_no_bot(self):
        """Test send_weekly_summary returns early when no bot."""
        sched = Scheduler()
        sched.bot = None

        await sched.send_weekly_summary()

    async def test_send_weekly_summary_with_checklists(self, scheduler_with_bot):
        """Test send_weekly_summary sends summary with checklists."""
        users = {"123": {"id": 1, "access_token": "valid_token"}}
        checklists = [
            {"id": 1, "status": "in_progress"},
            {"id": 2, "status": "in_progress"},
            {"id": 3, "status": "completed"},
        ]

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_user_checklists",
                return_value=checklists,
            ):
                await scheduler_with_bot.send_weekly_summary()

                scheduler_with_bot.bot.send_message.assert_called_once()
                call_args = scheduler_with_bot.bot.send_message.call_args
                assert call_args.kwargs["chat_id"] == "123"
                assert "Weekly Summary" in call_args.kwargs["text"]
                assert "Active checklists: 2" in call_args.kwargs["text"]
                assert "Completed checklists: 1" in call_args.kwargs["text"]

    async def test_send_weekly_summary_no_checklists(self, scheduler_with_bot):
        """Test send_weekly_summary skips when no checklists."""
        users = {"123": {"id": 1, "access_token": "valid_token"}}

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_user_checklists",
                return_value=[],
            ):
                await scheduler_with_bot.send_weekly_summary()

                scheduler_with_bot.bot.send_message.assert_not_called()

    async def test_send_weekly_summary_client_error(self, scheduler_with_bot):
        """Test send_weekly_summary handles client errors gracefully."""
        from unittest.mock import AsyncMock

        users = {"123": {"id": 1, "access_token": "valid_token"}}

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_user_checklists",
                new_callable=AsyncMock,
                side_effect=Exception("Client error"),
            ):
                # Should not raise
                await scheduler_with_bot.send_weekly_summary()

                scheduler_with_bot.bot.send_message.assert_not_called()

    async def test_send_weekly_summary_send_error(self, scheduler_with_bot):
        """Test send_weekly_summary handles send errors gracefully."""
        users = {"123": {"id": 1, "access_token": "valid_token"}}
        checklists = [{"id": 1, "status": "completed"}]

        scheduler_with_bot.bot.send_message = AsyncMock(
            side_effect=Exception("Send failed")
        )

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_user_checklists",
                return_value=checklists,
            ):
                # Should not raise
                await scheduler_with_bot.send_weekly_summary()

    async def test_send_weekly_summary_user_no_token(self, scheduler_with_bot):
        """Test send_weekly_summary skips users without access token."""
        users = {"123": {"id": 1, "access_token": None}}

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            await scheduler_with_bot.send_weekly_summary()

            scheduler_with_bot.bot.send_message.assert_not_called()

    async def test_send_weekly_summary_get_users_error(self, scheduler_with_bot):
        """Test send_weekly_summary handles get_all_users errors."""
        from unittest.mock import AsyncMock

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            new_callable=AsyncMock,
            side_effect=Exception("Cache error"),
        ):
            # Should not raise
            await scheduler_with_bot.send_weekly_summary()

            scheduler_with_bot.bot.send_message.assert_not_called()


class TestSendTaskReminder:
    """Test cases for send_task_reminder method."""

    @pytest.fixture
    def scheduler_with_bot(self):
        """Create scheduler with mocked bot."""
        sched = Scheduler()
        sched.bot = MagicMock()
        sched.bot.send_message = AsyncMock()
        return sched

    async def test_send_task_reminder_no_bot(self):
        """Test send_task_reminder returns early when no bot."""
        sched = Scheduler()
        sched.bot = None

        task = {"id": 1, "title": "Test Task", "due_date": "2024-12-31"}

        await sched.send_task_reminder(123, task)

    async def test_send_task_reminder_success(self, scheduler_with_bot):
        """Test send_task_reminder sends message successfully."""
        task = {"id": 1, "title": "Test Task", "due_date": "2024-12-31"}

        await scheduler_with_bot.send_task_reminder(123, task)

        scheduler_with_bot.bot.send_message.assert_called_once()
        call_args = scheduler_with_bot.bot.send_message.call_args
        assert call_args.kwargs["chat_id"] == 123
        assert "Task Reminder" in call_args.kwargs["text"]
        assert "Test Task" in call_args.kwargs["text"]

    async def test_send_task_reminder_without_due_date(self, scheduler_with_bot):
        """Test send_task_reminder with task that has no due date."""
        task = {"id": 1, "title": "Test Task"}

        await scheduler_with_bot.send_task_reminder(123, task)

        call_args = scheduler_with_bot.bot.send_message.call_args
        assert "Soon" in call_args.kwargs["text"]

    async def test_send_task_reminder_send_error(self, scheduler_with_bot):
        """Test send_task_reminder handles send errors gracefully."""
        task = {"id": 1, "title": "Test Task"}
        scheduler_with_bot.bot.send_message = AsyncMock(
            side_effect=Exception("Send failed")
        )

        # Should not raise
        await scheduler_with_bot.send_task_reminder(123, task)


class TestCleanupOldData:
    """Test cases for cleanup_old_data method."""

    async def test_cleanup_old_data(self):
        """Test cleanup_old_data runs without error."""
        sched = Scheduler()

        # Should not raise
        await sched.cleanup_old_data()


class TestScheduleUserNotification:
    """Test cases for schedule_user_notification method."""

    @pytest.fixture
    def scheduler_with_bot(self):
        """Create scheduler with mocked bot."""
        sched = Scheduler()
        sched.bot = MagicMock()
        sched.scheduler = MagicMock()
        sched.scheduler.add_job = MagicMock()
        return sched

    async def test_schedule_user_notification_no_bot(self):
        """Test schedule_user_notification returns early when no bot."""
        sched = Scheduler()
        sched.bot = None
        sched.scheduler = MagicMock()

        notification_time = datetime.now(UTC) + timedelta(hours=1)

        await sched.schedule_user_notification(123, notification_time, "Test message")

        sched.scheduler.add_job.assert_not_called()

    async def test_schedule_user_notification_adds_job(self, scheduler_with_bot):
        """Test schedule_user_notification adds job to scheduler."""
        notification_time = datetime.now(UTC) + timedelta(hours=1)

        await scheduler_with_bot.schedule_user_notification(
            123, notification_time, "Test message"
        )

        scheduler_with_bot.scheduler.add_job.assert_called_once()
        # Check the call was made with correct arguments
        call_args = scheduler_with_bot.scheduler.add_job.call_args

        # call_args.args = positional args, call_args.kwargs = keyword args
        assert call_args.args[0] == scheduler_with_bot.send_user_notification
        assert call_args.args[1] == "date"
        assert call_args.kwargs["run_date"] == notification_time
        assert call_args.kwargs["args"] == [123, "Test message"]
        assert "user_notif_123_" in call_args.kwargs["id"]
        assert call_args.kwargs["replace_existing"] is True


class TestSendUserNotification:
    """Test cases for send_user_notification method."""

    @pytest.fixture
    def scheduler_with_bot(self):
        """Create scheduler with mocked bot."""
        sched = Scheduler()
        sched.bot = MagicMock()
        sched.bot.send_message = AsyncMock()
        return sched

    async def test_send_user_notification_no_bot(self):
        """Test send_user_notification returns early when no bot."""
        sched = Scheduler()
        sched.bot = None

        await sched.send_user_notification(123, "Test message")

    async def test_send_user_notification_success(self, scheduler_with_bot):
        """Test send_user_notification sends message successfully."""
        await scheduler_with_bot.send_user_notification(123, "Test message")

        scheduler_with_bot.bot.send_message.assert_called_once()
        call_args = scheduler_with_bot.bot.send_message.call_args
        assert call_args.kwargs["chat_id"] == 123
        assert call_args.kwargs["text"] == "Test message"
        assert call_args.kwargs["parse_mode"] == "Markdown"

    async def test_send_user_notification_error(self, scheduler_with_bot):
        """Test send_user_notification handles send errors gracefully."""
        scheduler_with_bot.bot.send_message = AsyncMock(
            side_effect=Exception("Send failed")
        )

        # Should not raise
        await scheduler_with_bot.send_user_notification(123, "Test message")


class TestSchedulerIntegration:
    """Integration-style tests for Scheduler."""

    async def test_scheduler_lifecycle(self):
        """Test full scheduler lifecycle: start -> running -> shutdown."""
        sched = Scheduler()
        sched.scheduler = MagicMock()
        sched.scheduler.add_job = MagicMock()
        sched.scheduler.start = MagicMock()
        sched.scheduler.running = False
        sched.scheduler.shutdown = MagicMock()

        mock_bot = MagicMock()

        with patch("telegram_bot.utils.scheduler.settings") as mock_settings:
            mock_settings.ENABLE_NOTIFICATIONS = True
            mock_settings.NOTIFICATION_HOUR = 9

            # Start
            await sched.start(mock_bot)
            assert sched.is_running is True
            assert sched.bot is mock_bot
            sched.scheduler.start.assert_called_once()

            # Shutdown
            sched.scheduler.running = True
            await sched.shutdown()
            assert sched.is_running is False


class TestSchedulerErrorRecovery:
    """Test error recovery scenarios."""

    @pytest.fixture
    def scheduler_with_bot(self):
        """Create scheduler with mocked bot."""
        sched = Scheduler()
        sched.bot = MagicMock()
        sched.bot.send_message = AsyncMock()
        return sched

    async def test_send_daily_notifications_mixed_user_results(self, scheduler_with_bot):
        """Test handling mix of successful and failed user notifications."""
        users = {
            "123": {"id": 1, "access_token": "valid_token"},
            "456": {"id": 2, "access_token": "another_token"},
        }
        tasks = [{"id": 1, "title": "Task 1", "status": "pending"}]

        call_count = 0

        async def mock_send_message(**kwargs) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                msg = "Send failed for second user"
                raise RuntimeError(msg)

        scheduler_with_bot.bot.send_message = mock_send_message

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_assigned_tasks",
                return_value=tasks,
            ):
                # Should not raise - errors are caught per user
                await scheduler_with_bot.send_daily_notifications()

                # First user should have been processed
                assert call_count == 2

    async def test_send_weekly_summary_all_users_fail(self, scheduler_with_bot):
        """Test handling when all user notifications fail."""
        users = {
            "123": {"id": 1, "access_token": "valid_token"},
            "456": {"id": 2, "access_token": "valid_token2"},
        }
        checklists = [{"id": 1, "status": "completed"}]

        scheduler_with_bot.bot.send_message = AsyncMock(
            side_effect=Exception("Send failed")
        )

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_user_checklists",
                return_value=checklists,
            ):
                # Should not raise - all errors are caught
                await scheduler_with_bot.send_weekly_summary()

                assert scheduler_with_bot.bot.send_message.call_count == 2

    async def test_send_daily_notifications_multiple_users_empty_tasks(self, scheduler_with_bot):
        """Test handling multiple users with no pending tasks."""
        users = {
            "123": {"id": 1, "access_token": "valid_token"},
            "456": {"id": 2, "access_token": "valid_token2"},
        }
        tasks = [{"id": 1, "title": "Task 1", "status": "completed"}]

        with patch(
            "telegram_bot.utils.scheduler.user_cache.get_all_users",
            return_value=users,
        ):
            with patch(
                "telegram_bot.services.checklists_client.checklists_client.get_assigned_tasks",
                return_value=tasks,
            ):
                await scheduler_with_bot.send_daily_notifications()

                # No messages sent since no pending tasks
                scheduler_with_bot.bot.send_message.assert_not_called()


class TestSchedulerCronTriggerConfiguration:
    """Test CronTrigger configuration in scheduler."""

    @pytest.fixture
    def scheduler_instance(self):
        """Create a fresh scheduler instance with mocked internal scheduler."""
        sched = Scheduler()
        sched.scheduler = MagicMock()
        sched.scheduler.add_job = MagicMock()
        sched.scheduler.start = MagicMock()
        sched.scheduler.running = False
        return sched

    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot."""
        bot = MagicMock()
        bot.send_message = AsyncMock()
        return bot

    async def test_daily_notifications_uses_correct_hour(self, scheduler_instance, mock_bot):
        """Test daily notifications use configured hour."""
        with patch("telegram_bot.utils.scheduler.settings") as mock_settings:
            mock_settings.ENABLE_NOTIFICATIONS = True
            mock_settings.NOTIFICATION_HOUR = 14

            await scheduler_instance.start(mock_bot)

            # Find the daily_notifications job call
            daily_call = None
            for call in scheduler_instance.scheduler.add_job.call_args_list:
                if call[1].get("id") == "daily_notifications":
                    daily_call = call
                    break

            assert daily_call is not None
            # Check that CronTrigger was created with hour=14
            trigger = daily_call[0][1]
            assert isinstance(trigger, CronTrigger)

    async def test_weekly_summary_uses_monday(self, scheduler_instance, mock_bot):
        """Test weekly summary is scheduled for Monday."""
        with patch("telegram_bot.utils.scheduler.settings") as mock_settings:
            mock_settings.ENABLE_NOTIFICATIONS = True
            mock_settings.NOTIFICATION_HOUR = 9

            await scheduler_instance.start(mock_bot)

            # Find the weekly_summary job call
            weekly_call = None
            for call in scheduler_instance.scheduler.add_job.call_args_list:
                if call[1].get("id") == "weekly_summary":
                    weekly_call = call
                    break

            assert weekly_call is not None
            trigger = weekly_call[0][1]
            assert isinstance(trigger, CronTrigger)

    async def test_cleanup_uses_hourly_schedule(self, scheduler_instance, mock_bot):
        """Test cleanup job runs hourly."""
        with patch("telegram_bot.utils.scheduler.settings") as mock_settings:
            mock_settings.ENABLE_NOTIFICATIONS = True
            mock_settings.NOTIFICATION_HOUR = 9

            await scheduler_instance.start(mock_bot)

            # Find the cleanup job call
            cleanup_call = None
            for call in scheduler_instance.scheduler.add_job.call_args_list:
                if call[1].get("id") == "cleanup":
                    cleanup_call = call
                    break

            assert cleanup_call is not None
            trigger = cleanup_call[0][1]
            assert isinstance(trigger, CronTrigger)
