"""Handlers package for Telegram Bot."""

from telegram_bot.handlers.admin import router as admin_router
from telegram_bot.handlers.auth import router as auth_router
from telegram_bot.handlers.checklists import router as checklists_router
from telegram_bot.handlers.common import router as common_router
from telegram_bot.handlers.knowledge_base import router as knowledge_base_router
from telegram_bot.handlers.start import router as start_router

__all__ = [
    "admin_router",
    "auth_router",
    "checklists_router",
    "common_router",
    "knowledge_base_router",
    "start_router",
]
