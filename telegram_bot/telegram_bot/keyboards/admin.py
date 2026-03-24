"""Admin panel keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button


def get_admin_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
    """Create admin panel keyboard."""
    from telegram_bot.i18n import t

    builder = InlineKeyboardBuilder()

    builder.add(
        create_inline_button(
            f"\U0001f4ca {t('admin.btn_stats', locale=locale)}",
            callback_data="admin_stats",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f465 {t('admin.btn_users', locale=locale)}",
            callback_data="admin_users",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4cb {t('admin.btn_checklists', locale=locale)}",
            callback_data="admin_checklists",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4da {t('admin.btn_knowledge', locale=locale)}",
            callback_data="admin_knowledge",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2699\ufe0f {t('admin.btn_settings', locale=locale)}",
            callback_data="admin_settings",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4c8 {t('admin.btn_reports', locale=locale)}",
            callback_data="admin_reports",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f6a8 {t('admin.btn_alerts', locale=locale)}",
            callback_data="admin_alerts",
            style=ButtonStyle.DANGER,
        ),
        create_inline_button(
            "\u2190 Main Menu", callback_data="menu", style=ButtonStyle.SUCCESS
        ),
    )

    builder.adjust(2)
    return builder.as_markup()
