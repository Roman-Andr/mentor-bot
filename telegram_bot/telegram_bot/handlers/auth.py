"""Authentication and registration handlers."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import User as TgUser

from telegram_bot.keyboards.main_menu import get_main_menu_keyboard
from telegram_bot.states.auth_states import RegistrationStates
from telegram_bot.utils.formatters import format_welcome_message
from telegram_bot.utils.registration import register_by_token, user_cache

router = Router()


@router.message(RegistrationStates.waiting_for_token)
async def process_invitation_token(message: Message, state: FSMContext, tg_user: TgUser) -> None:
    """Process invitation token from user (fallback for manual token entry)."""
    token = message.text.strip()

    success, result = await register_by_token(token, tg_user, state)

    if success:
        welcome_text = format_welcome_message(tg_user, result)
        await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(is_authenticated=True))
    else:
        await message.answer(result)


@router.callback_query(F.data == "logout")
async def cb_logout(callback: CallbackQuery, state: FSMContext, tg_user: TgUser) -> None:
    """Handle logout."""
    await user_cache.delete_user(tg_user.id)
    await state.clear()

    await callback.message.edit_text("👋 You have been logged out.\n\nUse /start to register again.")
    await callback.answer("Logged out successfully")
