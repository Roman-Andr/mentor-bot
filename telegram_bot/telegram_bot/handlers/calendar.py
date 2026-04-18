"""Google Calendar integration handlers."""

import logging
import secrets

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.calendar_kb import (
    get_calendar_connect_keyboard,
    get_calendar_connected_keyboard,
    get_calendar_not_connected_keyboard,
)
from telegram_bot.services.calendar_client import CalendarClient

logger = logging.getLogger(__name__)
router = Router()
calendar_client = CalendarClient()


@router.message(Command("calendar"))
@router.message(F.text == "\U0001f4c5 Calendar")
@router.message(F.text == "Calendar")
@router.message(
    F.text == "\U0001f4c5 \u041a\u0430\u043b\u0435\u043d\u0434\u0430\u0440\u044c"
)
@router.message(F.text == "\u041a\u0430\u043b\u0435\u043d\u0434\u0430\u0440\u044c")
@router.callback_query(F.data == "calendar_menu")
async def calendar_menu(
    update: Message | CallbackQuery,
    user: dict,
    auth_token: str,
    *,
    locale: str = "en",
) -> None:
    """Show Google Calendar integration menu."""
    msg = None
    is_callback = isinstance(update, CallbackQuery)

    if is_callback:
        msg = update.message
        await update.answer()
    else:
        msg = update

    if not user or not auth_token:
        if is_callback:
            await update.answer(t("common.auth_required_short", locale=locale))
        else:
            await msg.answer(t("common.auth_required", locale=locale))
        return

    try:
        status = await calendar_client.check_connection_status(user["id"], auth_token)
        is_connected = status.get("connected", False)
    except Exception:
        logger.exception("Failed to check calendar status")
        is_connected = False

    if is_connected:
        keyboard = get_calendar_connected_keyboard(locale=locale)
        status_text = f"\u2705 *{t('calendar.connected', locale=locale)}*"
    else:
        keyboard = get_calendar_not_connected_keyboard(locale=locale)
        status_text = f"\u274c *{t('calendar.not_connected', locale=locale)}*"

    text = (
        f"*\U0001f4c5 {t('calendar.title', locale=locale)}*\n\n"
        f"Status: {status_text}\n\n"
        f"{t('calendar.benefits', locale=locale)}"
    )

    if is_callback and msg:
        await msg.edit_text(
            text,
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown",
        )
    else:
        await msg.answer(
            text,
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "calendar_connect")
async def connect_calendar(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Initiate Google Calendar connection."""
    if not user:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    try:
        state = secrets.token_urlsafe(32)
        connect_url = await calendar_client.get_connect_url(user["id"], state)

        text = (
            f"*\U0001f517 {t('calendar.connect_title', locale=locale)}*\n\n"
            f"{t('calendar.connect_instructions', locale=locale)}\n\n"
            f"[{t('calendar.btn_authorize', locale=locale)}]({connect_url})"
        )

        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=get_calendar_connect_keyboard(
                    connect_url, locale=locale
                ).as_markup(),
                parse_mode="Markdown",
            )
        await callback.answer()

    except Exception:
        logger.exception("Failed to initiate calendar connection")
        await callback.answer(t("common.failed", locale=locale), show_alert=True)


@router.callback_query(F.data == "calendar_disconnect")
async def disconnect_calendar(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Disconnect Google Calendar account."""
    if not user:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    try:
        result = await calendar_client.disconnect_calendar(user["id"], auth_token)

        if result.get("status") == "success":
            await callback.answer(t("calendar.disconnected", locale=locale))
            if callback.message:
                await callback.message.edit_text(
                    t("calendar.disconnected", locale=locale)
                )
        else:
            await callback.answer(
                t("calendar.disconnect_failed", locale=locale), show_alert=True
            )

    except Exception:
        logger.exception("Failed to disconnect calendar")
        await callback.answer(
            t("calendar.disconnect_failed", locale=locale), show_alert=True
        )
