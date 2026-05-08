"""Language selection keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_language_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
    """Build language selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("\U0001f1ec\U0001f1e7 English", callback_data="set_lang_en", style=ButtonStyle.PRIMARY),
        create_inline_button("\U0001f1f7\U0001f1fa Русский", callback_data="set_lang_ru", style=ButtonStyle.PRIMARY),
    )
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="settings_menu",
        )
    )
    builder.adjust(1)
    return builder.as_markup()
