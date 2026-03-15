"""Start command and welcome handlers."""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.keyboards.main_menu import get_inline_main_menu, get_main_menu_keyboard
from telegram_bot.states.auth_states import RegistrationStates
from telegram_bot.utils.formatters import format_welcome_message
from telegram_bot.utils.registration import register_by_token

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, *, is_authenticated: bool, user: dict | None = None) -> None:
    """Handle /start command with optional invitation token."""
    await state.clear()

    # Format: /start token or via link: https://t.me/bot?start=token
    token = None
    if message.text and len(message.text.split()) > 1:
        token = message.text.split()[1].strip()

    if is_authenticated:
        welcome_text = format_welcome_message(message.from_user, user)
        await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(is_authenticated=True))
        return

    if token:
        success, result = await register_by_token(token, message.from_user, state)

        if success:
            welcome_text = format_welcome_message(message.from_user, result)
            await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(is_authenticated=True))
        else:
            await message.answer(
                f"{result}\n\nPlease check the token or contact HR.",
            )
            await state.set_state(RegistrationStates.waiting_for_token)
    else:
        await message.answer(
            "👋 Welcome to Mentor Bot!\n\n"
            "🤖 Your personal onboarding assistant for a smooth transition into your new role.\n\n"
            "*What I can help you with:*\n"
            "• 📋 Complete your onboarding checklist\n"
            "• 🔍 Search the knowledge base for answers\n"
            "• 📅 Schedule meetings with your mentor\n"
            "• 📁 Access important documents\n"
            "• 📊 Track your progress\n"
            "• 📞 Get help from HR\n\n"
            "To get started, you need to register using your invitation link.\n"
            "Please send me your invitation token or use the link from your email."
        )
        await state.set_state(RegistrationStates.waiting_for_token)


@router.message(Command("menu"))
async def cmd_menu(message: Message, *, is_authenticated: bool) -> None:
    """Show main menu."""
    if not is_authenticated:
        await message.answer("You need to register first. Use /start to begin registration.")
        return

    await message.answer(
        "📋 *Main Menu*\n\nChoose an option below:",
        reply_markup=get_inline_main_menu(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery, *, is_authenticated: bool) -> None:
    """Menu callback button."""
    if not is_authenticated:
        await callback.answer("You need to register first.")
        return

    if callback.message is None:
        await callback.answer("Unable to show menu. Please try again.")
        return

    await callback.message.edit_text(
        "📋 *Main Menu*\n\nChoose an option below:",
        reply_markup=get_inline_main_menu(),
        parse_mode="Markdown",
    )
    await callback.answer()
