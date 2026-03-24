"""Language selection keyboards."""

from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button


def get_language_keyboard() -> InlineKeyboardBuilder:
    """Build language selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            "English", callback_data="set_lang_en", style=ButtonStyle.PRIMARY
        ),
        create_inline_button(
            "Русский", callback_data="set_lang_ru", style=ButtonStyle.PRIMARY
        ),
    )
    builder.adjust(2)
    return builder
