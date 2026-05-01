"""Settings menu handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.settings_kb import get_notifications_keyboard, get_settings_keyboard
from telegram_bot.services.auth_client import auth_client

router = Router()


@router.message(Command("settings"))
@router.message(F.text == "\u2699\ufe0f Settings")
@router.message(F.text == "Settings")
@router.message(
    F.text == "\u2699\ufe0f \u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438"
)
@router.message(F.text == "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438")
async def cmd_settings(message: Message, auth_token: str, user: dict, *, locale: str = "en") -> None:
    """Show settings menu."""
    # Fetch current preferences from auth_service
    telegram_enabled = True
    email_enabled = True
    if user and auth_token:
        user_id = user.get("id")
        if user_id:
            prefs = await auth_client.get_user_preferences(user_id, auth_token)
            if prefs:
                telegram_enabled = prefs.get("notification_telegram_enabled", True)
                email_enabled = prefs.get("notification_email_enabled", True)

    text = (
        f"*\u2699\ufe0f {t('settings.title', locale=locale)}*\n\n"
        f"{t('settings.description', locale=locale)}"
    )
    await message.answer(
        text,
        reply_markup=get_settings_keyboard(locale=locale, telegram_enabled=telegram_enabled, email_enabled=email_enabled),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "settings_menu")
async def cb_settings_menu(callback: CallbackQuery, auth_token: str, user: dict, *, locale: str = "en") -> None:
    """Show settings menu via callback."""
    if callback.message is None:
        await callback.answer()
        return

    # Fetch current preferences from auth_service
    telegram_enabled = True
    email_enabled = True
    if user and auth_token:
        user_id = user.get("id")
        if user_id:
            prefs = await auth_client.get_user_preferences(user_id, auth_token)
            if prefs:
                telegram_enabled = prefs.get("notification_telegram_enabled", True)
                email_enabled = prefs.get("notification_email_enabled", True)

    text = (
        f"*\u2699\ufe0f {t('settings.title', locale=locale)}*\n\n"
        f"{t('settings.description', locale=locale)}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_settings_keyboard(locale=locale, telegram_enabled=telegram_enabled, email_enabled=email_enabled),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "notifications_menu")
async def cb_notifications_menu(callback: CallbackQuery, auth_token: str, user: dict, *, locale: str = "en") -> None:
    """Show notifications settings menu."""
    if callback.message is None:
        await callback.answer()
        return

    # Fetch current preferences from auth_service
    telegram_enabled = True
    email_enabled = True
    if user and auth_token:
        user_id = user.get("id")
        if user_id:
            prefs = await auth_client.get_user_preferences(user_id, auth_token)
            if prefs:
                telegram_enabled = prefs.get("notification_telegram_enabled", True)
                email_enabled = prefs.get("notification_email_enabled", True)

    text = (
        f"*\u2699\ufe0f {t('settings.notifications_title', locale=locale)}*\n\n"
        f"{t('settings.notifications_description', locale=locale)}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_notifications_keyboard(locale=locale, telegram_enabled=telegram_enabled, email_enabled=email_enabled),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_telegram")
async def cb_toggle_telegram(callback: CallbackQuery, auth_token: str, user: dict, *, locale: str = "en") -> None:
    """Toggle Telegram notifications."""
    if callback.message is None:
        await callback.answer()
        return

    # Fetch current preferences
    telegram_enabled = True
    email_enabled = True
    user_id = None
    if user and auth_token:
        user_id = user.get("id")
        if user_id:
            prefs = await auth_client.get_user_preferences(user_id, auth_token)
            if prefs:
                telegram_enabled = prefs.get("notification_telegram_enabled", True)
                email_enabled = prefs.get("notification_email_enabled", True)

    # Toggle the value
    new_telegram_enabled = not telegram_enabled

    # Update preferences via auth_service API
    if user_id and auth_token:
        await auth_client.update_user_preferences(
            user_id,
            {"notification_telegram_enabled": new_telegram_enabled},
            auth_token,
        )

    text = (
        f"*\u2699\ufe0f {t('settings.notifications_title', locale=locale)}*\n\n"
        f"{t('settings.notifications_description', locale=locale)}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_notifications_keyboard(locale=locale, telegram_enabled=new_telegram_enabled, email_enabled=email_enabled),
        parse_mode="Markdown",
    )
    await callback.answer(t("settings.telegram_toggled", locale=locale))


@router.callback_query(F.data == "toggle_email")
async def cb_toggle_email(callback: CallbackQuery, auth_token: str, user: dict, *, locale: str = "en") -> None:
    """Toggle Email notifications."""
    if callback.message is None:
        await callback.answer()
        return

    # Fetch current preferences
    telegram_enabled = True
    email_enabled = True
    user_id = None
    if user and auth_token:
        user_id = user.get("id")
        if user_id:
            prefs = await auth_client.get_user_preferences(user_id, auth_token)
            if prefs:
                telegram_enabled = prefs.get("notification_telegram_enabled", True)
                email_enabled = prefs.get("notification_email_enabled", True)

    # Toggle the value
    new_email_enabled = not email_enabled

    # Update preferences via auth_service API
    if user_id and auth_token:
        await auth_client.update_user_preferences(
            user_id,
            {"notification_email_enabled": new_email_enabled},
            auth_token,
        )

    text = (
        f"*\u2699\ufe0f {t('settings.notifications_title', locale=locale)}*\n\n"
        f"{t('settings.notifications_description', locale=locale)}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_notifications_keyboard(locale=locale, telegram_enabled=telegram_enabled, email_enabled=new_email_enabled),
        parse_mode="Markdown",
    )
    await callback.answer(t("settings.email_toggled", locale=locale))

