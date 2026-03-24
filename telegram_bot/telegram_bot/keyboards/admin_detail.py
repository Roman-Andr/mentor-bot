"""Admin sub-menu keyboards."""

from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_admin_stats_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build admin stats keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("admin.btn_detailed_report", locale=locale),
            callback_data="detailed_report",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            t("admin.btn_export", locale=locale),
            callback_data="export_data",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="admin_panel",
        ),
    )
    builder.adjust(1)
    return builder


def get_admin_users_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build admin users management keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("admin.btn_list_users", locale=locale),
            callback_data="list_users",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            t("admin.btn_add_user", locale=locale),
            callback_data="add_user",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            t("admin.btn_send_invite", locale=locale),
            callback_data="send_invite",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="admin_panel",
        ),
    )
    builder.adjust(1)
    return builder


def get_admin_checklists_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build admin checklists management keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("admin.btn_templates", locale=locale),
            callback_data="list_templates",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            t("admin.btn_checklist_progress", locale=locale),
            callback_data="checklist_progress",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            t("admin.btn_overdue", locale=locale),
            callback_data="overdue_tasks",
            style=ButtonStyle.DANGER,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="admin_panel",
        ),
    )
    builder.adjust(1)
    return builder


def get_back_to_admin_users_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build back button keyboard to admin users."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="admin_users",
        )
    )
    builder.adjust(1)
    return builder


def get_back_to_admin_checklists_keyboard(
    *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build back button keyboard to admin checklists."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="admin_checklists",
        )
    )
    builder.adjust(1)
    return builder


def get_back_to_admin_panel_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build back button keyboard to admin panel."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="admin_panel",
        )
    )
    builder.adjust(1)
    return builder


def get_back_to_admin_stats_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build back button keyboard to admin stats."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="admin_stats",
        )
    )
    builder.adjust(1)
    return builder
