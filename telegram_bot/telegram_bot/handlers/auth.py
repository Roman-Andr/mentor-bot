"""Authentication and registration handlers."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import User as TgUser
from loguru import logger

from telegram_bot.i18n import t
from telegram_bot.keyboards.main_menu import get_main_menu_keyboard
from telegram_bot.states.auth_states import RegistrationStates
from telegram_bot.utils.formatters import format_welcome_message
from telegram_bot.utils.registration import register_by_token, user_cache

router = Router()


@router.message(RegistrationStates.waiting_for_token)
async def process_invitation_token(
    message: Message, state: FSMContext, tg_user: TgUser, *, locale: str = "en"
) -> None:
    """Process invitation token from user (fallback for manual token entry)."""
    logger.debug("Processing invitation token (telegram_id={})", tg_user.id)
    token = (message.text or "").strip()

    success, result = await register_by_token(token, tg_user, state)

    if success:
        logger.info("User registered via token (telegram_id={}, user_id={})", tg_user.id, result.get("id") if result else None)
        welcome_text = format_welcome_message(tg_user, result, locale=locale)
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard(
                is_authenticated=True, user=result, locale=locale
            ),
        )
    else:
        logger.warning("Registration failed (telegram_id={}, result={})", tg_user.id, result)
        await message.answer(t("start.register_error", locale=locale, result=result))


@router.callback_query(F.data == "logout")
async def cb_logout(
    callback: CallbackQuery, state: FSMContext, tg_user: TgUser, *, locale: str = "en"
) -> None:
    """Handle logout."""
    logger.info("User logout (telegram_id={})", tg_user.id)
    await user_cache.delete_user(tg_user.id)
    await state.clear()

    if callback.message:
        await callback.message.edit_text(t("auth.logged_out", locale=locale))
    await callback.answer(t("auth.logout_success", locale=locale))
