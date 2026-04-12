"""Settings keyboard factory."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_settings_keyboard(locale: str = "en") -> InlineKeyboardMarkup:
    """Create settings menu keyboard."""
    builder = InlineKeyboardBuilder()

    # Language button
    builder.add(
        create_inline_button(
            f"\U0001f310 {t('settings.btn_language', locale=locale)}",
            callback_data="language_menu",
            style=ButtonStyle.PRIMARY,
        )
    )

    # Back to menu button
    builder.add(
        create_inline_button(
            f"\u2190 {t('settings.btn_back', locale=locale)}",
            callback_data="main_menu",
            style=ButtonStyle.PRIMARY,
        )
    )

    builder.adjust(1)
    return builder.as_markup()
