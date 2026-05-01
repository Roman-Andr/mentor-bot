"""Google Calendar integration keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_calendar_connected_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
    """Build calendar menu keyboard when calendar is connected."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f504 {t('calendar.btn_reconnect', locale=locale)}",
            callback_data="calendar_connect",
            style=ButtonStyle.PRIMARY,
        )
    )
    builder.add(
        create_inline_button(
            f"\u274c {t('calendar.btn_disconnect', locale=locale)}",
            callback_data="calendar_disconnect",
            style=ButtonStyle.DANGER,
        )
    )
    builder.add(create_inline_button(f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"))
    builder.adjust(1)
    return builder.as_markup()


def get_calendar_not_connected_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
    """Build calendar menu keyboard when calendar is not connected."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f517 {t('calendar.btn_connect', locale=locale)}",
            callback_data="calendar_connect",
            style=ButtonStyle.PRIMARY,
        )
    )
    builder.add(create_inline_button(f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"))
    builder.adjust(1)
    return builder.as_markup()


def get_calendar_connect_keyboard(connect_url: str, *, locale: str = "en") -> InlineKeyboardMarkup:
    """Build calendar connect keyboard with authorization URL."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("calendar.btn_authorize", locale=locale),
            url=connect_url,
            style=ButtonStyle.PRIMARY,
        )
    )
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="calendar_menu",
        )
    )
    return builder.as_markup()
