"""Bot setup and configuration."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from telegram_bot.handlers import (
    admin,
    auth,
    calendar,
    checklists,
    common,
    documents,
    escalation,
    faq,
    feedback,
    knowledge_base,
    language,
    meetings,
    start,
)
from telegram_bot.middlewares import AuthMiddleware, LanguageMiddleware

logger = logging.getLogger(__name__)


async def global_error_handler(event: ErrorEvent) -> bool:
    """Handle all uncaught errors gracefully."""
    logger.error(
        "Unhandled error in update %s: %s",
        event.update.update_id,
        event.exception,
        exc_info=event.exception,
    )

    callback = event.update.callback_query
    message = event.update.message or (callback.message if callback else None)

    if message:
        try:
            await message.answer(
                "\u26a0\ufe0f An unexpected error occurred. Please try again later.",
            )
        except Exception:
            logger.warning("Failed to send error message to user")
    elif callback:
        try:
            await callback.answer(
                "An error occurred. Please try again.",
                show_alert=True,
            )
        except Exception:
            logger.warning("Failed to send error callback answer")

    return True


def setup_bot(dp: Dispatcher, bot: Bot) -> Dispatcher:
    """Set up bot with all handlers and middleware."""
    # Register middleware
    dp.update.outer_middleware(AuthMiddleware(bot))
    dp.update.outer_middleware(LanguageMiddleware())

    # Register global error handler
    dp.errors.register(global_error_handler)

    # Include routers (order matters: start/auth first, common last)
    dp.include_router(start.router)
    dp.include_router(auth.router)
    dp.include_router(language.router)
    dp.include_router(calendar.router)
    dp.include_router(checklists.router)
    dp.include_router(knowledge_base.router)
    dp.include_router(faq.router)
    dp.include_router(documents.router)
    dp.include_router(meetings.router)
    dp.include_router(escalation.router)
    dp.include_router(feedback.router)
    dp.include_router(admin.router)
    dp.include_router(common.router)

    return dp
