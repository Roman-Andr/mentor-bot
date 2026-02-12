"""Knowledge base and FAQ handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.states.auth_states import SearchStates
from telegram_bot.utils.cache import cached
from telegram_bot.utils.formatters import format_search_results

router = Router()


@cached(ttl=300, key_prefix="kb_menu")
async def _get_knowledge_base_menu() -> dict:
    """Get knowledge base menu (cached)."""
    return {
        "title": "📚 *Knowledge Base*",
        "description": "Find answers to common questions, documentation, and resources.",
    }


@router.message(Command("knowledge"))
@router.message(F.text == "🔍 Knowledge Base")
@router.message(F.text == "Knowledge Base")
@router.callback_query(F.data == "knowledge_base")
async def knowledge_base_menu(update: Message | CallbackQuery) -> None:
    """Show knowledge base menu."""
    if isinstance(update, CallbackQuery):
        message = update.message
        await update.answer()
    else:
        message = update

    # Get cached menu data
    menu_data = await _get_knowledge_base_menu()

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🔍 Search", callback_data="search_kb"),
        InlineKeyboardButton(text="📚 FAQ", callback_data="show_faq"),
        InlineKeyboardButton(text="📖 Categories", callback_data="kb_categories"),
        InlineKeyboardButton(text="← Menu", callback_data="menu"),
    )
    builder.adjust(2)

    await message.answer(
        f"{menu_data['title']}\n\n{menu_data['description']}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "search_kb")
async def start_search(callback: CallbackQuery, state: FSMContext) -> None:
    """Start knowledge base search."""
    await callback.message.answer(
        "🔍 *Search Knowledge Base*\n\nWhat would you like to search for?\nPlease enter your search query:",
        parse_mode="Markdown",
    )
    await state.set_state(SearchStates.waiting_for_query)
    await callback.answer()


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext) -> None:
    """Process search query."""
    query = message.text.strip()

    if len(query) < 3:
        await message.answer("❌ Search query must be at least 3 characters long.")
        return

    mock_results = [
        {
            "title": "How to request vacation",
            "snippet": "Learn how to request vacation time through the HR system...",
            "category": "HR",
            "relevance": 0.95,
        },
        {
            "title": "Setting up your workstation",
            "snippet": "Complete guide to setting up your computer and software...",
            "category": "IT",
            "relevance": 0.87,
        },
        {
            "title": "Company policies overview",
            "snippet": "Overview of all company policies and procedures...",
            "category": "General",
            "relevance": 0.76,
        },
    ]

    text = format_search_results(query, mock_results)

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📄 View first result", callback_data="view_result_0"),
        InlineKeyboardButton(text="🔍 Search again", callback_data="search_kb"),
        InlineKeyboardButton(text="📞 Contact HR", callback_data="contact_hr"),
        InlineKeyboardButton(text="← Menu", callback_data="menu"),
    )
    builder.adjust(1)

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await state.clear()


@cached(ttl=3600, key_prefix="kb_faq")
async def _get_faq_data() -> list[tuple[str, str]]:
    """Get FAQ data (cached)."""
    return [
        ("❓ How do I request time off?", "Use the HR portal or contact your manager."),
        ("💻 IT support contact", "Email: it-support@company.com or call ext. 555"),
        ("🏢 Office access", "Your badge will be activated on your first day."),
        ("🍽️ Lunch options", "Cafeteria is open 11:30-14:00, delivery services available."),
        ("🚗 Parking information", "Register your vehicle with security for a parking pass."),
    ]


@router.callback_query(F.data == "show_faq")
async def show_faq(callback: CallbackQuery) -> None:
    """Show frequently asked questions."""
    faq_items = await _get_faq_data()

    text = "❓ *Frequently Asked Questions*\n\n"
    for question, answer in faq_items:
        text += f"*{question}*\n{answer}\n\n"

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🔍 Search", callback_data="search_kb"),
        InlineKeyboardButton(text="📞 Contact HR", callback_data="contact_hr"),
        InlineKeyboardButton(text="← Back", callback_data="knowledge_base"),
    )
    builder.adjust(2)

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()
