"""Settings menu handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.settings_kb import get_settings_keyboard

router = Router()


@router.message(Command("settings"))
@router.message(F.text == "\u2699\ufe0f Settings")
@router.message(F.text == "Settings")
@router.message(
    F.text == "\u2699\ufe0f \u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438"
)
@router.message(F.text == "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438")
async def cmd_settings(message: Message, *, locale: str = "en") -> None:
    """Show settings menu."""
    text = (
        f"*\u2699\ufe0f {t('settings.title', locale=locale)}*\n\n"
        f"{t('settings.description', locale=locale)}"
    )
    await message.answer(
        text,
        reply_markup=get_settings_keyboard(locale=locale),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "settings_menu")
async def cb_settings_menu(callback: CallbackQuery, *, locale: str = "en") -> None:
    """Show settings menu via callback."""
    if callback.message is None:
        await callback.answer()
        return

    text = (
        f"*\u2699\ufe0f {t('settings.title', locale=locale)}*\n\n"
        f"{t('settings.description', locale=locale)}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_settings_keyboard(locale=locale),
        parse_mode="Markdown",
    )
    await callback.answer()
