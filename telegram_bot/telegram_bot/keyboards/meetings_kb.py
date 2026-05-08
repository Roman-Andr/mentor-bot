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
    return builder.as_markup()


def get_title_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
    """Build keyboard with back button for title step."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(f"← {t('common.back_button', locale=locale)}", callback_data="meetings_menu"),
    )
    return builder.as_markup()


def get_skip_description_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
    """Build keyboard with skip button for description step."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"⏩ {t('meetings.btn_skip', locale=locale)}",
            callback_data="meeting_skip_description",
        ),
        create_inline_button(f"← {t('common.back_button', locale=locale)}", callback_data="schedule_meeting"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_datetime_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
    """Build keyboard with back button for datetime step."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(f"← {t('common.back_button', locale=locale)}", callback_data="meeting_back_to_description"),
    )
    return builder.as_markup()


def get_duration_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
    """Build keyboard with duration options (30/60/120 min)."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("30 мин" if locale == "ru" else "30 min", callback_data="meeting_duration_30"),
        create_inline_button("60 мин" if locale == "ru" else "60 min", callback_data="meeting_duration_60"),
        create_inline_button("120 мин" if locale == "ru" else "120 min", callback_data="meeting_duration_120"),
        create_inline_button(f"← {t('common.back_button', locale=locale)}", callback_data="meeting_back_to_datetime"),
    )
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


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
