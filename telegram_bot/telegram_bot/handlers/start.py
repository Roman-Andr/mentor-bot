"""Start command and welcome handlers."""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.main_menu import (
    get_inline_main_menu,
    get_main_menu_keyboard,
)
from telegram_bot.states.auth_states import RegistrationStates
from telegram_bot.utils.formatters import format_welcome_message
from telegram_bot.utils.registration import register_by_token

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    *,
    is_authenticated: bool,
    user: dict | None = None,
    locale: str = "en",
) -> None:
    """Handle /start command with optional invitation token."""
    await state.clear()

    token = None
    if message.text and len(message.text.split()) > 1:
        token = message.text.split()[1].strip()

    if is_authenticated:
        welcome_text = format_welcome_message(message.from_user, user, locale=locale)
        await message.answer(
            welcome_text, reply_markup=get_main_menu_keyboard(is_authenticated=True)
        )
        return

    if token:
        success, result = await register_by_token(token, message.from_user, state)

        if success:
            welcome_text = format_welcome_message(
                message.from_user, result, locale=locale
            )
            await message.answer(
                welcome_text, reply_markup=get_main_menu_keyboard(is_authenticated=True)
            )
        else:
            await message.answer(
                t("start.register_error", locale=locale, result=result),
            )
            await state.set_state(RegistrationStates.waiting_for_token)
    else:
        await message.answer(t("start.welcome_new", locale=locale))
        await state.set_state(RegistrationStates.waiting_for_token)


@router.message(Command("menu"))
async def cmd_menu(
    message: Message, *, is_authenticated: bool, locale: str = "en"
) -> None:
    """Show main menu."""
    if not is_authenticated:
        await message.answer(t("start.register_prompt", locale=locale))
        return

    await message.answer(
        t("start.menu_header", locale=locale),
        reply_markup=get_inline_main_menu(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "menu")
async def cb_menu(
    callback: CallbackQuery, *, is_authenticated: bool, locale: str = "en"
) -> None:
    """Menu callback button."""
    if not is_authenticated:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    if callback.message is None:
        await callback.answer(t("common.error_generic", locale=locale))
        return

    await callback.message.edit_text(
        t("start.menu_header", locale=locale),
        reply_markup=get_inline_main_menu(),
        parse_mode="Markdown",
    )
    await callback.answer()
