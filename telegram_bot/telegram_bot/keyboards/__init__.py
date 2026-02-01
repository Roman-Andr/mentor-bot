"""Keyboards package for Telegram Bot."""

from telegram_bot.keyboards.admin_kb import get_admin_keyboard
from telegram_bot.keyboards.checklist_kb import (
    get_checklists_keyboard,
    get_task_detail_keyboard,
    get_tasks_keyboard,
)
from telegram_bot.keyboards.main_menu import (
    get_inline_main_menu,
    get_main_menu_keyboard,
)

__all__ = [
    "get_admin_keyboard",
    "get_checklists_keyboard",
    "get_inline_main_menu",
    "get_main_menu_keyboard",
    "get_task_detail_keyboard",
    "get_tasks_keyboard",
]
