"""Authentication middleware for Telegram updates."""

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject
from loguru import logger

from telegram_bot.config import settings
from telegram_bot.services.auth_client import auth_client
from telegram_bot.services.cache import user_cache

if TYPE_CHECKING:
    from aiogram.types import User as TgUser


class AuthMiddleware(BaseMiddleware):
    """Middleware to authenticate users and attach user data."""

    def __init__(self, bot: Bot) -> None:
        """Initialize auth middleware."""
        super().__init__()
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> object:
        """Process update to authenticate user."""
        tg_user: TgUser = None
        if event.message:
            tg_user = event.message.from_user
        elif event.callback_query:
            tg_user = event.callback_query.from_user
        elif event.inline_query:
            tg_user = event.inline_query.from_user

        if not tg_user:
            return await handler(event, data)

        logger.debug("Auth middleware processing (telegram_id={})", tg_user.id)
        data["tg_user"] = tg_user

        user_data = await user_cache.get_user(tg_user.id)

        if not user_data:
            logger.debug("User not in cache, authenticating (telegram_id={})", tg_user.id)
            telegram_data = {
                "api_key": settings.TELEGRAM_API_KEY,
                "telegram_id": tg_user.id,
            }

            auth_result = await auth_client.authenticate_with_telegram(telegram_data)

            if auth_result and "access_token" in auth_result:
                user_data = await auth_client.get_current_user(
                    auth_result["access_token"]
                )

                if user_data:
                    user_data = {
                        **user_data,
                        "access_token": auth_result["access_token"],
                        "refresh_token": auth_result["refresh_token"],
                    }
                    await user_cache.set_user(tg_user.id, user_data)
                    logger.info("User authenticated and cached (telegram_id={}, user_id={})", tg_user.id, user_data.get("id"))
                else:
                    logger.warning("Authentication successful but user data fetch failed (telegram_id={})", tg_user.id)
            else:
                logger.debug("Authentication failed (telegram_id={})", tg_user.id)

        if user_data:
            data["user"] = user_data
            data["auth_token"] = user_data.get("access_token")
            data["is_authenticated"] = True
        else:
            data["user"] = None
            data["auth_token"] = None
            data["is_authenticated"] = False

        return await handler(event, data)
