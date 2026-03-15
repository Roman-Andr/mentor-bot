"""Bot setup and configuration."""

from aiogram import Bot, Dispatcher

from telegram_bot.handlers import (
    admin,
    auth,
    calendar,
    checklists,
    common,
    documents,
    escalation,
    feedback,
    knowledge_base,
    meetings,
    start,
)
from telegram_bot.middlewares import AuthMiddleware, ThrottlingMiddleware


def setup_bot(dp: Dispatcher, bot: Bot) -> Dispatcher:
    """Set up bot with all handlers and middleware."""
    # Register middleware
    dp.update.outer_middleware(ThrottlingMiddleware())
    dp.update.outer_middleware(AuthMiddleware(bot))

    # Include routers
    dp.include_router(start.router)
    dp.include_router(auth.router)
    dp.include_router(calendar.router)
    dp.include_router(checklists.router)
    dp.include_router(knowledge_base.router)
    dp.include_router(documents.router)
    dp.include_router(meetings.router)
    dp.include_router(escalation.router)
    dp.include_router(feedback.router)
    dp.include_router(admin.router)
    dp.include_router(common.router)

    return dp
