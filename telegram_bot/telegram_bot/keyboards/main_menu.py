"""Main menu keyboard factory."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_main_menu_keyboard(*, is_authenticated: bool = False) -> ReplyKeyboardMarkup:
    """Create main menu keyboard."""
    builder = ReplyKeyboardBuilder()

    if is_authenticated:
        builder.add(KeyboardButton(text="📋 My Tasks"))
        builder.add(KeyboardButton(text="🔍 Knowledge Base"))
        builder.add(KeyboardButton(text="👨‍🏫 My Mentor"))
        builder.add(KeyboardButton(text="📞 Contact HR"))
        builder.add(KeyboardButton(text="ℹ️ Help"))
    else:
        builder.add(KeyboardButton(text="/start"))
        builder.add(KeyboardButton(text="/help"))

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_inline_main_menu() -> InlineKeyboardMarkup:
    """Create inline main menu."""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="📋 My Tasks", callback_data="my_tasks"))
    builder.add(InlineKeyboardButton(text="🔍 Knowledge Base", callback_data="knowledge_base"))
    builder.add(InlineKeyboardButton(text="👨‍🏫 My Mentor", callback_data="my_mentor"))
    builder.add(InlineKeyboardButton(text="📞 Contact HR", callback_data="contact_hr"))
    builder.add(InlineKeyboardButton(text="📊 Progress", callback_data="progress"))
    builder.add(InlineKeyboardButton(text="ℹ️ Help", callback_data="help"))

    builder.adjust(2)
    return builder.as_markup()
