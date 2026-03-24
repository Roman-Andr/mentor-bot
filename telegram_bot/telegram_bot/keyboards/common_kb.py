"""Common keyboards (help, contact HR, mentor, progress)."""

from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_help_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build help screen keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("buttons.open_menu", locale=locale),
            callback_data="menu",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            t("buttons.contact_hr", locale=locale),
            callback_data="contact_hr",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            t("buttons.my_mentor", locale=locale),
            callback_data="my_mentor",
            style=ButtonStyle.PRIMARY,
        ),
    )
    builder.adjust(1)
    return builder


def get_contact_hr_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build contact HR keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f4e8 {t('hr.btn_send_message', locale=locale)}",
            callback_data="send_to_hr",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4c5 {t('hr.btn_schedule_meeting', locale=locale)}",
            callback_data="schedule_hr",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}",
            callback_data="menu",
        ),
    )
    builder.adjust(1)
    return builder


def get_schedule_hr_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build schedule meeting with HR keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("buttons.meetings", locale=locale),
            callback_data="meetings_menu",
            style=ButtonStyle.PRIMARY,
        )
    )
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="contact_hr",
        )
    )
    return builder


def get_my_mentor_no_mentor_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build my mentor keyboard when no mentor is assigned."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("buttons.contact_hr", locale=locale),
            callback_data="contact_hr",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_my_mentor_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build my mentor keyboard when mentor is assigned."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f4ac {t('mentor.btn_message', locale=locale)}",
            callback_data="message_mentor",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4c5 {t('mentor.btn_schedule', locale=locale)}",
            callback_data="schedule_mentor",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4cb {t('mentor.btn_tasks', locale=locale)}",
            callback_data="mentor_tasks",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_schedule_mentor_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build schedule meeting with mentor keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("buttons.meetings", locale=locale),
            callback_data="meetings_menu",
            style=ButtonStyle.PRIMARY,
        )
    )
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="my_mentor",
        )
    )
    return builder


def get_mentor_tasks_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build mentor tasks keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("buttons.my_tasks", locale=locale),
            callback_data="my_tasks",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="my_mentor",
        ),
    )
    builder.adjust(1)
    return builder


def get_progress_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build progress dashboard keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("progress.btn_my_tasks", locale=locale),
            callback_data="my_tasks",
            style=ButtonStyle.PRIMARY,
        )
    )
    builder.add(
        create_inline_button(
            t("progress.btn_meetings", locale=locale),
            callback_data="meetings_menu",
            style=ButtonStyle.PRIMARY,
        )
    )
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        )
    )
    builder.adjust(1)
    return builder
