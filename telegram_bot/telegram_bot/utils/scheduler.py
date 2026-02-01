"""Scheduler for notifications and periodic tasks."""

import logging
from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from telegram_bot.config import settings

logger = logging.getLogger(__name__)


class Scheduler:
    """Scheduler for bot notifications."""

    def __init__(self) -> None:
        """Initialize scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.bot: Bot | None = None
        self.is_running = False

    async def start(self, bot: Bot) -> None:
        """Start the scheduler."""
        self.bot = bot

        if not settings.ENABLE_NOTIFICATIONS:
            logger.info("Notifications are disabled")
            return

        hour = settings.NOTIFICATION_HOUR
        self.scheduler.add_job(
            self.send_daily_notifications,
            CronTrigger(hour=hour, minute=0),
            id="daily_notifications",
            name="Send daily notifications",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self.send_weekly_summary,
            CronTrigger(day_of_week="mon", hour=10, minute=0),
            id="weekly_summary",
            name="Send weekly summary",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self.cleanup_old_data,
            CronTrigger(hour="*", minute=30),
            id="cleanup",
            name="Cleanup old data",
            replace_existing=True,
        )

        self.scheduler.start()
        self.is_running = True
        logger.info(f"Scheduler started with notifications at {hour}:00")

    async def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler shutdown")

    async def send_daily_notifications(self) -> None:
        """Send daily notifications to users."""
        if not self.bot:
            return

        logger.info("Sending daily notifications")


    async def send_weekly_summary(self) -> None:
        """Send weekly summary to users and admins."""
        if not self.bot:
            return

        logger.info("Sending weekly summary")


    async def send_task_reminder(self, user_id: int, task: dict) -> None:
        """Send reminder for specific task."""
        if not self.bot:
            return

        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=f"⏰ *Task Reminder*\n\n"
                f"Task: {task.get('title')}\n"
                f"Due: {task.get('due_date', 'Soon')}\n\n"
                f"Don't forget to complete this task!",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.exception(f"Failed to send reminder to {user_id}: {e}")

    async def cleanup_old_data(self) -> None:
        """Cleanup old cached data."""
        logger.info("Running cleanup job")


    async def schedule_user_notification(self, user_id: int, notification_time: datetime, message: str) -> None:
        """Schedule a one-time notification for user."""
        if not self.bot:
            return

        self.scheduler.add_job(
            self.send_user_notification,
            "date",
            run_date=notification_time,
            args=[user_id, message],
            id=f"user_notif_{user_id}_{notification_time.timestamp()}",
            replace_existing=True,
        )

    async def send_user_notification(self, user_id: int, message: str) -> None:
        """Send notification to specific user."""
        if not self.bot:
            return

        try:
            await self.bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")
        except Exception as e:
            logger.exception(f"Failed to send notification to {user_id}: {e}")


# Global scheduler instance
scheduler = Scheduler()
