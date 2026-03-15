"""Google Calendar integration handlers."""

import logging
import secrets

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button
from telegram_bot.services.calendar_client import CalendarClient

logger = logging.getLogger(__name__)
router = Router()
calendar_client = CalendarClient()


@router.callback_query(F.data == "calendar_menu")
async def calendar_menu(callback: CallbackQuery, user: dict, auth_token: str) -> None:
    """Show Google Calendar integration menu."""
    if not user or not auth_token:
        await callback.answer("Authentication required", show_alert=True)
        return

    try:
        status = await calendar_client.check_connection_status(user["id"])
        is_connected = status.get("connected", False)
    except Exception as e:
        logger.exception(f"Failed to check calendar status: {e}")
        is_connected = False

    builder = InlineKeyboardBuilder()

    if is_connected:
        builder.add(
            create_inline_button("🔄 Reconnect Calendar", callback_data="calendar_connect", style=ButtonStyle.PRIMARY)
        )
        builder.add(
            create_inline_button(
                "❌ Disconnect Calendar", callback_data="calendar_disconnect", style=ButtonStyle.DANGER
            )
        )
        status_text = "✅ *Connected*"
    else:
        builder.add(
            create_inline_button(
                "🔗 Connect Google Calendar", callback_data="calendar_connect", style=ButtonStyle.PRIMARY
            )
        )
        status_text = "❌ *Not Connected*"

    builder.add(create_inline_button("← Back", callback_data="menu"))
    builder.adjust(2)

    text = (
        "📅 *Google Calendar Integration*\n\n"
        f"Status: {status_text}\n\n"
        "Connect your Google Calendar to automatically sync meetings "
        "and receive reminders directly in your calendar.\n\n"
        "Benefits:\n"
        "• Automatic event creation\n"
        "• Calendar reminders\n"
        "• Sync across devices"
    )

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "calendar_connect")
async def connect_calendar(callback: CallbackQuery, user: dict) -> None:
    """Initiate Google Calendar connection."""
    if not user:
        await callback.answer("Authentication required", show_alert=True)
        return

    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)

        # Get connection URL
        connect_url = await calendar_client.get_connect_url(user["id"], state)

        text = (
            "🔗 *Connect Google Calendar*\n\n"
            "Click the button below to authorize access to your Google Calendar:\n\n"
            f"[Open Authorization Page]({connect_url})\n\n"
            "After authorizing, you will be redirected back to the bot."
        )

        builder = InlineKeyboardBuilder()
        builder.add(create_inline_button("🔐 Authorize Google Calendar", url=connect_url, style=ButtonStyle.PRIMARY))
        builder.add(create_inline_button("← Back", callback_data="calendar_menu"))

        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await callback.answer()

    except Exception as e:
        logger.exception(f"Failed to initiate calendar connection: {e}")
        await callback.answer("Failed to initiate connection. Please try again.", show_alert=True)


@router.callback_query(F.data == "calendar_disconnect")
async def disconnect_calendar(callback: CallbackQuery, user: dict) -> None:
    """Disconnect Google Calendar account."""
    if not user:
        await callback.answer("Authentication required", show_alert=True)
        return

    try:
        result = await calendar_client.disconnect_calendar(user["id"])

        if result.get("status") == "success":
            await callback.answer("✅ Google Calendar disconnected")
            await callback.message.edit_text(
                "✅ Google Calendar has been disconnected.\n\nYou can reconnect at any time from the calendar menu.",
                reply_markup=None,
            )
        else:
            await callback.answer("Failed to disconnect calendar", show_alert=True)

    except Exception as e:
        logger.exception(f"Failed to disconnect calendar: {e}")
        await callback.answer("Failed to disconnect calendar. Please try again.", show_alert=True)


@router.message(F.text == "📅 Calendar")
async def calendar_command(message: Message, user: dict, auth_token: str) -> None:
    """Handle /calendar command or button press."""
    if not user or not auth_token:
        await message.answer("You need to be registered to manage calendar.\nUse /start to register.")
        return

    # Show calendar menu
    status = await calendar_client.check_connection_status(user["id"])
    is_connected = status.get("connected", False)

    builder = InlineKeyboardBuilder()

    if is_connected:
        builder.add(
            create_inline_button("🔄 Reconnect Calendar", callback_data="calendar_connect", style=ButtonStyle.PRIMARY)
        )
        builder.add(
            create_inline_button(
                "❌ Disconnect Calendar", callback_data="calendar_disconnect", style=ButtonStyle.DANGER
            )
        )
        status_text = "✅ *Connected*"
    else:
        builder.add(
            create_inline_button(
                "🔗 Connect Google Calendar", callback_data="calendar_connect", style=ButtonStyle.PRIMARY
            )
        )
        status_text = "❌ *Not Connected*"

    builder.add(create_inline_button("← Menu", callback_data="menu"))
    builder.adjust(2)

    text = (
        "📅 *Google Calendar Integration*\n\n"
        f"Status: {status_text}\n\n"
        "Connect your Google Calendar to automatically sync meetings "
        "and receive reminders directly in your calendar."
    )

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
