"""Language selection handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.language_kb import get_language_keyboard
from telegram_bot.services.cache import user_cache

router = Router()


@router.message(Command("language"))
async def cmd_language(message: Message, *, locale: str = "en") -> None:
    """Show language selection."""
    await message.answer(
        t("start.choose_language", locale=locale),
        reply_markup=get_language_keyboard(locale=locale).as_markup(),
    )


@router.callback_query(F.data == "language_menu")
async def cb_language_menu(callback: CallbackQuery, *, locale: str = "en") -> None:
    """Show language selection via callback."""
    if callback.message is None:
        await callback.answer()
        return

    await callback.message.edit_text(
        t("start.choose_language", locale=locale),
        reply_markup=get_language_keyboard(locale=locale).as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery, tg_user: object) -> None:
    """Set user language preference."""
    lang = callback.data.split("_")[-1]
    if lang not in ("en", "ru"):
        await callback.answer("Unsupported language")
        return

    from aiogram.types import User as TgUser

    user = tg_user
    if isinstance(user, TgUser):
        await user_cache.update_user_field(user.id, "language", lang)

    await callback.answer(t("start.language_set", locale=lang))
    if callback.message:
        await callback.message.edit_text(
            t("start.language_set", locale=lang),
            reply_markup=get_language_keyboard(locale=lang).as_markup(),
        )
