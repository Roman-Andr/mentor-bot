"""Meeting management keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_meetings_menu_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
    """Build meetings menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f4cb {t('meetings.btn_my_meetings', locale=locale)}",
            callback_data="my_meetings",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2795 {t('meetings.btn_schedule', locale=locale)}",
            callback_data="schedule_meeting",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_my_meetings_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
    """Build back button keyboard for my meetings."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="meetings_menu",
        )
    )
    return builder


def get_meeting_details_keyboard(meeting_id: int, *, locale: str = "en") -> InlineKeyboardMarkup:
    """Build meeting details keyboard with confirm/cancel actions."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2705 {t('meetings.btn_confirm', locale=locale)}",
            callback_data=f"confirm_meeting_{meeting_id}",
            style=ButtonStyle.SUCCESS,
        ),
        create_inline_button(
            f"\u274c {t('meetings.btn_cancel', locale=locale)}",
            callback_data=f"cancel_meeting_{meeting_id}",
            style=ButtonStyle.DANGER,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="my_meetings",
        ),
    )
    builder.adjust(2, 1)
    return builder.as_markup()
