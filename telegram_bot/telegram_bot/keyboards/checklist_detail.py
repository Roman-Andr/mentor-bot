"""Checklist detail-specific keyboards (no checklists, no tasks, attach, info, completed)."""

from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_no_checklists_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build keyboard for when user has no checklists."""
    builder = InlineKeyboardBuilder()
    builder.add(create_inline_button("\u2190 Menu", callback_data="menu"))
    return builder


def get_no_tasks_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build keyboard for when a checklist has no tasks."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="my_tasks",
        )
    )
    return builder


def get_attach_task_keyboard(
    task_id: int, *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build keyboard for attach file to task."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("buttons.documents", locale=locale),
            callback_data="documents_menu",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data=f"task_{task_id}",
        ),
    )
    return builder


def get_task_info_keyboard(
    task_id: int, *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build keyboard for task info view."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("checklists.btn_complete", locale=locale),
            callback_data=f"complete_task_{task_id}",
            style=ButtonStyle.SUCCESS,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="my_tasks",
        ),
    )
    builder.adjust(1)
    return builder


def get_task_completed_keyboard(
    task_id: int, *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build keyboard shown after task is completed."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            "\u2705 Completed",
            callback_data=f"task_{task_id}",
            style=ButtonStyle.SUCCESS,
        )
    )
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="my_tasks",
        )
    )
    return builder
