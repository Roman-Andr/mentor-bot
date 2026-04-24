"""Request ID middleware for tracing requests across services."""

import uuid
from collections.abc import Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, Update

from telegram_bot.utils.logging import logger, request_id_var


class RequestIDMiddleware(BaseMiddleware):
    """Middleware to inject request ID for tracing Telegram bot updates."""

    def __init__(self) -> None:
        """Initialize the middleware."""
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update], Any],
        event: Message | CallbackQuery,
        data: dict,
    ) -> Any:
        """Process update and inject request ID for tracing."""
        rid = uuid.uuid4().hex

        token = request_id_var.set(rid)

        try:
            update_id = getattr(event, "message_id", None) or getattr(event, "id", None)
            with logger.contextualize(request_id=rid, update_id=update_id):
                return await handler(event, data)
        finally:
            request_id_var.reset(token)
