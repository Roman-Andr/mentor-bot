"""Throttling middleware to limit user requests."""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject
from aiogram.types import User as TgUser


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware to throttle user requests."""

    def __init__(self) -> None:
        """Initialize throttling middleware."""
        super().__init__()
        self.user_limiters = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Process update with throttling."""
        rate_limit = get_flag(data, "rate_limit")
        if rate_limit is None:
            rate_limit = {"calls": 5, "period": 60}

        tg_user: TgUser = None
        if event.message:
            tg_user = event.message.from_user
        elif event.callback_query:
            tg_user = event.callback_query.from_user

        if tg_user:
            user_id = tg_user.id

            if user_id in self.user_limiters:
                last_call, calls = self.user_limiters[user_id]
                if (
                    datetime.now(UTC) - last_call < timedelta(seconds=rate_limit["period"])
                    and calls >= rate_limit["calls"]
                ):
                    if hasattr(event, "answer"):
                        await event.answer("Too many requests. Please wait a moment.", show_alert=True)
                    return None

            if user_id not in self.user_limiters:
                self.user_limiters[user_id] = [datetime.now(UTC), 1]
            else:
                last_call, calls = self.user_limiters[user_id]
                if datetime.now(UTC) - last_call < timedelta(seconds=rate_limit["period"]):
                    self.user_limiters[user_id] = [last_call, calls + 1]
                else:
                    self.user_limiters[user_id] = [datetime.now(UTC), 1]

        return await handler(event, data)

    def cleanup_old_limiters(self) -> None:
        """Clean up old user limiters."""
        now = datetime.now(UTC)
        to_remove = []

        for user_id, (last_call, _) in self.user_limiters.items():
            if now - last_call > timedelta(minutes=5):
                to_remove.append(user_id)

        for user_id in to_remove:
            del self.user_limiters[user_id]
