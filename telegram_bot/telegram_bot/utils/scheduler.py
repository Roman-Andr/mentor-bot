"""Scheduler for notifications and periodic tasks."""

import logging
from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from telegram_bot.config import settings
from telegram_bot.services.cache import user_cache

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
        logger.info("Scheduler started with notifications at %s:00", hour)

    async def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler shutdown")

    async def send_daily_notifications(self) -> None:
        """Send daily notifications to users about pending tasks."""
        if not self.bot:
            return

        logger.info("Sending daily notifications")

        try:
            all_users = await user_cache.get_all_users()
            for telegram_id, user_data in all_users.items():
                access_token = user_data.get("access_token")
                if not access_token:
                    continue

                try:
                    from telegram_bot.services.checklists_client import (
                        checklists_client,
                    )

                    tasks = await checklists_client.get_assigned_tasks(access_token)
                    pending = [t for t in tasks if t.get("status") in ("pending", "in_progress")]

                    if pending:
                        task_list = "\n".join(f"  \u2022 {t.get('title', 'Untitled')}" for t in pending[:5])
                        await self.bot.send_message(
                            chat_id=telegram_id,
                            text=(
                                f"\u23f3 *Daily Reminder*\n\n"
                                f"You have {len(pending)} pending task(s):\n\n"
                                f"{task_list}\n\n"
                                f"Use /tasks to view your checklist."
                            ),
                            parse_mode="Markdown",
                        )
                except Exception:
                    logger.warning("Failed to send notification to user %s", telegram_id)
        except Exception:
            logger.exception("Failed to send daily notifications")

    async def send_weekly_summary(self) -> None:
        """Send weekly summary to users and admins."""
        if not self.bot:
            return

        logger.info("Sending weekly summary")

        try:
            all_users = await user_cache.get_all_users()
            for telegram_id, user_data in all_users.items():
                access_token = user_data.get("access_token")
                if not access_token:
                    continue

                try:
                    from telegram_bot.services.checklists_client import (
                        checklists_client,
                    )

                    checklists = await checklists_client.get_user_checklists(user_data.get("id", 0), access_token)
                    if checklists:
                        active = len([c for c in checklists if c.get("status") != "completed"])
                        completed = len([c for c in checklists if c.get("status") == "completed"])

                        await self.bot.send_message(
                            chat_id=telegram_id,
                            text=(
                                f"\U0001f4ca *Weekly Summary*\n\n"
                                f"Active checklists: {active}\n"
                                f"Completed checklists: {completed}\n\n"
                                f"Keep up the great work! Use /progress for details."
                            ),
                            parse_mode="Markdown",
                        )
                except Exception:
                    logger.warning("Failed to send weekly summary to user %s", telegram_id)
        except Exception:
            logger.exception("Failed to send weekly summary")

    async def send_task_reminder(self, user_id: int, task: dict) -> None:
        """Send reminder for specific task."""
        if not self.bot:
            return

        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=(
                    f"\u23f3 *Task Reminder*\n\n"
                    f"Task: {task.get('title')}\n"
                    f"Due: {task.get('due_date', 'Soon')}\n\n"
                    f"Don't forget to complete this task!"
                ),
                parse_mode="Markdown",
            )
        except Exception:
            logger.exception("Failed to send reminder to %s", user_id)

    async def cleanup_old_data(self) -> None:
        """Cleanup old cached data."""
        logger.debug("Running cleanup job")

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
        except Exception:
            logger.exception("Failed to send notification to %s", user_id)


# Global scheduler instance
scheduler = Scheduler()
