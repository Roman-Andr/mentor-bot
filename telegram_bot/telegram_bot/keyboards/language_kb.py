"""Language selection keyboards."""

from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_language_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
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
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_to_settings', locale=locale)}",
            callback_data="settings_menu",
            style=ButtonStyle.PRIMARY,
        )
    )
    builder.adjust(2, 1)
    return builder
