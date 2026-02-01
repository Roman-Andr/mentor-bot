"""Admin panel keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Create admin panel keyboard."""
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats"),
        InlineKeyboardButton(text="👥 Users", callback_data="admin_users"),
        InlineKeyboardButton(text="📋 Checklists", callback_data="admin_checklists"),
        InlineKeyboardButton(text="📚 Knowledge Base", callback_data="admin_knowledge"),
        InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_settings"),
        InlineKeyboardButton(text="📈 Reports", callback_data="admin_reports"),
        InlineKeyboardButton(text="🚨 Alerts", callback_data="admin_alerts"),
        InlineKeyboardButton(text="← Main Menu", callback_data="menu"),
    )

    builder.adjust(2)
    return builder.as_markup()
