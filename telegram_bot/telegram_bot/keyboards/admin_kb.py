"""Admin panel keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Create admin panel keyboard."""
    builder = InlineKeyboardBuilder()

    builder.add(
        create_inline_button("📊 Statistics", callback_data="admin_stats", style=ButtonStyle.PRIMARY),
        create_inline_button("👥 Users", callback_data="admin_users", style=ButtonStyle.PRIMARY),
        create_inline_button("📋 Checklists", callback_data="admin_checklists", style=ButtonStyle.PRIMARY),
        create_inline_button("📚 Knowledge Base", callback_data="admin_knowledge", style=ButtonStyle.PRIMARY),
        create_inline_button("⚙️ Settings", callback_data="admin_settings", style=ButtonStyle.PRIMARY),
        create_inline_button("📈 Reports", callback_data="admin_reports", style=ButtonStyle.PRIMARY),
        create_inline_button("🚨 Alerts", callback_data="admin_alerts", style=ButtonStyle.DANGER),
        create_inline_button("← Main Menu", callback_data="menu", style=ButtonStyle.SUCCESS),
    )

    builder.adjust(2)
    return builder.as_markup()
