"""Language selection handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.language_kb import get_language_keyboard
from telegram_bot.services.auth_client import auth_client

router = Router()


@router.message(Command("language"))
async def cmd_language(message: Message, *, locale: str = "en") -> None:
    """Show language selection (deprecated, redirects to settings)."""
    await message.answer(
        t("settings.language_deprecated", locale=locale),
        reply_markup=get_language_keyboard(locale=locale).as_markup(),
    )


@router.callback_query(F.data == "language_menu")
async def cb_language_menu(callback: CallbackQuery, *, locale: str = "en") -> None:
    """Show language selection via callback."""
    if callback.message is None:
        await callback.answer()
        return

    await callback.message.edit_text(
        t("settings.choose_language", locale=locale),
        reply_markup=get_language_keyboard(locale=locale).as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery, auth_token: str, user: dict) -> None:
    """Set user language preference via auth_service API."""
    lang = callback.data.split("_")[-1]
    if lang not in ("en", "ru"):
        await callback.answer("Unsupported language")
        return

    # Update preferences via auth_service API
    if user and auth_token:
        user_id = user.get("id")
        if user_id:
            await auth_client.update_user_preferences(
                user_id,
                {"language": lang},
                auth_token,
            )

    await callback.answer(t("settings.language_set", locale=lang))
    if callback.message:
        await callback.message.edit_text(
            t("settings.language_set", locale=lang),
            reply_markup=get_language_keyboard(locale=lang),
        )
