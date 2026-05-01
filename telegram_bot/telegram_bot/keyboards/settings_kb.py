"""Settings keyboard factory."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_settings_keyboard(locale: str = "en", telegram_enabled: bool = True, email_enabled: bool = True) -> InlineKeyboardMarkup:
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

    # Notifications button
    builder.add(
        create_inline_button(
            f"\U0001f514 {t('settings.btn_notifications', locale=locale)}",
            callback_data="notifications_menu",
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


def get_notifications_keyboard(locale: str = "en", telegram_enabled: bool = True, email_enabled: bool = True) -> InlineKeyboardMarkup:
    """Create notifications settings keyboard."""
    builder = InlineKeyboardBuilder()

    # Telegram toggle
    telegram_status = t("settings.on", locale=locale) if telegram_enabled else t("settings.off", locale=locale)
    builder.add(
        create_inline_button(
            f"\U0001f4f2 {t('settings.btn_telegram', locale=locale)}: {telegram_status}",
            callback_data="toggle_telegram",
            style=ButtonStyle.PRIMARY,
        )
    )

    # Email toggle
    email_status = t("settings.on", locale=locale) if email_enabled else t("settings.off", locale=locale)
    builder.add(
        create_inline_button(
            f"\U0001f4e7 {t('settings.btn_email', locale=locale)}: {email_status}",
            callback_data="toggle_email",
            style=ButtonStyle.PRIMARY,
        )
    )

    # Back to settings button
    builder.add(
        create_inline_button(
            f"\u2190 {t('settings.btn_back_to_settings', locale=locale)}",
            callback_data="settings_menu",
            style=ButtonStyle.PRIMARY,
        )
    )

    builder.adjust(1)
    return builder.as_markup()

