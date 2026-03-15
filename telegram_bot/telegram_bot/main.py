"""Main entry point for Telegram Bot application."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from redis.asyncio import Redis

from telegram_bot.bot import setup_bot
from telegram_bot.config import settings
from telegram_bot.database import init_db
from telegram_bot.services.cache import user_cache
from telegram_bot.utils import cache as redis_cache
from telegram_bot.utils import scheduler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(bot: Bot) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events."""
    logger.info("Starting Telegram Bot...")

    # Initialize database
    await init_db()

    # Initialize cache
    await user_cache.connect()
    await redis_cache.connect()

    # Setup bot commands
    await setup_bot_commands(bot)

    # Start scheduler for notifications
    if settings.ENABLE_NOTIFICATIONS:
        await scheduler.start(bot)

    logger.info("Telegram Bot started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Telegram Bot...")
    await bot.session.close()
    await user_cache.disconnect()
    await redis_cache.disconnect()
    if settings.ENABLE_NOTIFICATIONS:
        await scheduler.shutdown()


async def setup_bot_commands(bot: Bot) -> None:
    """Bot commands for Telegram menu."""
    commands = [
        BotCommand(command="/start", description="Start/restart bot"),
        BotCommand(command="/menu", description="Open main menu"),
        BotCommand(command="/tasks", description="Show my tasks"),
        BotCommand(command="/checklist", description="Show checklist progress"),
        BotCommand(command="/knowledge", description="Search knowledge base"),
        BotCommand(command="/meetings", description="View and manage meetings"),
        BotCommand(command="/documents", description="Access documents"),
        BotCommand(command="/feedback", description="Provide feedback"),
        BotCommand(command="/progress", description="View onboarding progress"),
        BotCommand(command="/help", description="Show help"),
    ]

    if settings.ADMIN_IDS:
        commands.append(BotCommand(command="/admin", description="Admin panel"))

    await bot.set_my_commands(commands)


async def main() -> None:
    """Application entry point."""
    # Initialize Redis storage
    redis = Redis.from_url(str(settings.REDIS_URL))
    storage = RedisStorage(redis=redis)

    # Create bot and dispatcher
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
    dp = Dispatcher(storage=storage)

    # Setup bot handlers and middleware
    setup_bot(dp, bot)

    async with lifespan(bot):
        # Delete webhook if exists
        await bot.delete_webhook(drop_pending_updates=True)

        # Start polling
        await dp.start_polling(bot)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
