"""Main menu keyboard factory."""

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button, create_keyboard_button


def get_main_menu_keyboard(*, is_authenticated: bool = False) -> ReplyKeyboardMarkup:
    """Create main menu keyboard."""
    builder = ReplyKeyboardBuilder()

    if is_authenticated:
        builder.add(create_keyboard_button("📋 My Tasks", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("🔍 Knowledge Base", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("📁 Documents", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("📅 Meetings", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("📅 Calendar", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("👨‍🏫 My Mentor", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("📞 Contact HR", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("📊 Feedback", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("ℹ️ Help"))
    else:
        builder.add(create_keyboard_button("/start", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("/help"))

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_inline_main_menu() -> InlineKeyboardMarkup:
    """Create inline main menu."""
    builder = InlineKeyboardBuilder()

    builder.add(create_inline_button("📋 My Tasks", callback_data="my_tasks", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("🔍 Knowledge Base", callback_data="knowledge_base", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("📁 Documents", callback_data="documents_menu", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("📅 Meetings", callback_data="meetings_menu", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("📅 Calendar", callback_data="calendar_menu", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("👨‍🏫 My Mentor", callback_data="my_mentor", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("📞 Contact HR", callback_data="contact_hr", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("📊 Feedback", callback_data="feedback_menu", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("📊 Progress", callback_data="progress", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("ℹ️ Help", callback_data="help"))

    builder.adjust(2)
    return builder.as_markup()
