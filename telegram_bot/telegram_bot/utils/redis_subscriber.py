"""Redis pub/sub subscriber for Telegram notifications."""

import asyncio
import contextlib
import json
import logging

from aiogram import Bot
from redis.asyncio import Redis

from telegram_bot.config import settings
from telegram_bot.i18n import t
from telegram_bot.services.cache import user_cache

logger = logging.getLogger(__name__)


class RedisNotificationSubscriber:
    """Subscriber for Telegram notifications and events from Redis pub/sub."""

    def __init__(self, redis_url: str | None = None) -> None:
        """Initialize subscriber with Redis URL."""
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis: Redis | None = None
        self.bot: Bot | None = None
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self, bot: Bot) -> None:
        """Start the subscriber."""
        self.bot = bot
        self.redis = Redis.from_url(self.redis_url, decode_responses=True)
        self._running = True
        self._task = asyncio.create_task(self._subscribe())
        logger.info("Redis notification subscriber started")

    async def stop(self) -> None:
        """Stop the subscriber."""
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        if self.redis:
            try:
                await self.redis.aclose()
            except Exception:
                logger.exception("Failed to close Redis connection in subscriber")
        logger.info("Redis notification subscriber stopped")

    async def _subscribe(self) -> None:
        """Subscribe to Redis channels and process messages."""
        if not self.redis:
            return

        pubsub = self.redis.pubsub()
        await pubsub.subscribe("telegram_notifications", "telegram_events")

        logger.info("Subscribed to telegram_notifications and telegram_events channels")

        while self._running:
            try:
                message = await pubsub.get_message(timeout=1.0)
                if message and message["type"] == "message":
                    channel = message["channel"]
                    data = message["data"]

                    if channel == "telegram_notifications":
                        await self._handle_notification(data)
                    elif channel == "telegram_events":
                        await self._handle_event(data)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in Redis subscriber loop")
                await asyncio.sleep(1)

        await pubsub.unsubscribe("telegram_notifications", "telegram_events")
        await pubsub.close()

    async def _handle_notification(self, data: str) -> None:
        """Handle incoming notification message."""
        try:
            payload = json.loads(data)
            chat_id = payload.get("chat_id")
            text = payload.get("text")
            parse_mode = payload.get("parse_mode", "HTML")

            if not chat_id or not text:
                logger.warning("Invalid notification payload: %s", payload)
                return

            if not self.bot:
                logger.warning("Bot not initialized, cannot send message")
                return

            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
            )
            logger.info("Telegram notification sent via bot (chat_id=%s)", chat_id)
        except Exception:
            logger.exception("Failed to handle notification message")

    async def _handle_event(self, data: str) -> None:
        """Handle incoming event message."""
        try:
            payload = json.loads(data)
            event_type = payload.get("type")

            if event_type == "calendar_connected":
                await self._handle_calendar_connected(payload)
            elif event_type in {"user_deleted", "user_deactivated"}:
                await self._handle_user_removed(payload)
            else:
                logger.debug("Unknown event type: %s", event_type)
        except Exception:
            logger.exception("Failed to handle event message")

    async def _handle_user_removed(self, payload: dict) -> None:
        """Invalidate cached Telegram auth state when auth service removes a user."""
        telegram_id = payload.get("telegram_id")
        if not telegram_id:
            user_id = payload.get("user_id")
            if user_id:
                telegram_id = await user_cache.find_telegram_id_by_user_id(user_id)

        if not telegram_id:
            logger.warning("Missing telegram_id for user removal event: %s", payload)
            return

        deleted = await user_cache.delete_user(int(telegram_id))
        if deleted:
            logger.info("Telegram user cache invalidated (telegram_id=%s)", telegram_id)
        else:
            logger.warning("Telegram user cache invalidation failed (telegram_id=%s)", telegram_id)

    async def _handle_calendar_connected(self, payload: dict) -> None:
        """Handle calendar connected event."""
        try:
            user_id = payload.get("user_id")
            if not user_id:
                logger.warning("Missing user_id in calendar_connected event")
                return

            # Find telegram_id by user_id
            telegram_id = await user_cache.find_telegram_id_by_user_id(user_id)
            if not telegram_id:
                logger.warning("Could not find telegram_id for user_id=%s", user_id)
                return

            if not self.bot:
                logger.warning("Bot not initialized, cannot send message")
                return

            # Send calendar menu update
            from telegram_bot.keyboards.calendar_kb import get_calendar_connected_keyboard

            # Get user data to determine locale
            user_data = await user_cache.get_user(telegram_id)
            locale = user_data.get("locale", "en") if user_data else "en"

            keyboard = get_calendar_connected_keyboard(locale=locale)
            status_text = f"✅ *{t('calendar.connected', locale=locale)}*"

            text = (
                f"📅 *{t('calendar.title', locale=locale)}*\n\n"
                f"Status: {status_text}\n\n"
                f"{t('calendar.benefits', locale=locale)}"
            )

            await self.bot.send_message(
                chat_id=telegram_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
            logger.info("Calendar connected notification sent (user_id=%s, telegram_id=%s)", user_id, telegram_id)
        except Exception:
            logger.exception("Failed to handle calendar_connected event")


# Global subscriber instance
subscriber = RedisNotificationSubscriber()
