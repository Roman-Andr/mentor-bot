"""Language middleware to inject locale into handler data."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from telegram_bot.i18n import DEFAULT_LOCALE
from telegram_bot.services.cache import user_cache


class LanguageMiddleware(BaseMiddleware):
    """Middleware to detect user language and pass it to handlers."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> object:
        """Inject locale into handler data."""
        locale = DEFAULT_LOCALE

        tg_user = data.get("tg_user")
        if tg_user:
            user_data = await user_cache.get_user(tg_user.id)
            if user_data:
                locale = user_data.get("language", DEFAULT_LOCALE)

        data["locale"] = locale
        return await handler(event, data)
