"""Escalation handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button
from telegram_bot.services.escalation_client import escalation_client
from telegram_bot.states.escalation_states import EscalationStates
from telegram_bot.utils.formatters import format_escalation_list

router = Router()


@router.message(Command("escalate"))
@router.message(F.text == "📞 Escalate")
@router.callback_query(F.data == "escalate_menu")
async def escalation_menu(update: Message | CallbackQuery, user: dict, auth_token: str) -> None:
    """Show escalation menu."""
    if isinstance(update, CallbackQuery):
        message = update.message
        await update.answer()
    else:
        message = update

    if not user or not auth_token:
        await message.answer("You need to be registered to escalate issues.\nUse /start to register.")
        return

    # Get user escalations
    escalations = await escalation_client.get_user_escalations(user["id"], limit=5)

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("➕ New Escalation", callback_data="new_escalation", style=ButtonStyle.PRIMARY),
        create_inline_button("📋 My Escalations", callback_data="my_escalations", style=ButtonStyle.PRIMARY),
        create_inline_button("← Menu", callback_data="menu"),
    )
    builder.adjust(1)

    text = "📞 *Escalation Center*\n\n"
    if escalations:
        text += format_escalation_list(escalations)
        text += "\n"
    else:
        text += "You have no active escalations.\n\n"

    text += "Use the options below to escalate an issue or view your existing escalations."

    if isinstance(update, CallbackQuery):
        await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data == "new_escalation")
async def new_escalation(callback: CallbackQuery, state: FSMContext) -> None:
    """Start new escalation."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("❓ Question not answered", callback_data="escalate_question", style=ButtonStyle.PRIMARY),
        create_inline_button("👥 Contact Mentor", callback_data="escalate_mentor", style=ButtonStyle.PRIMARY),
        create_inline_button("📞 Contact HR", callback_data="escalate_hr", style=ButtonStyle.PRIMARY),
        create_inline_button("⚠️ Technical Issue", callback_data="escalate_technical", style=ButtonStyle.DANGER),
        create_inline_button("← Back", callback_data="escalate_menu"),
    )
    builder.adjust(1)

    await callback.message.edit_text(
        "📞 *New Escalation*\n\nPlease select the type of escalation:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("escalate_"))
async def process_escalation_type(callback: CallbackQuery, state: FSMContext) -> None:
    """Process escalation type selection."""
    escalation_type = callback.data.split("_")[1]

    type_map = {
        "question": "Question not answered",
        "mentor": "Contact Mentor",
        "hr": "Contact HR",
        "technical": "Technical Issue",
    }

    category = type_map.get(escalation_type, "General")

    await state.update_data(category=category)
    await callback.message.edit_text(
        f"📚 *Escalation: {category}*\n\nPlease describe your issue or question in detail:",
        parse_mode="Markdown",
    )
    await state.set_state(EscalationStates.waiting_for_description)
    await callback.answer()


@router.message(EscalationStates.waiting_for_description)
async def process_escalation_description(message: Message, state: FSMContext) -> None:
    """Process escalation description."""
    description = message.text.strip()

    if len(description) < 10:
        await message.answer("❌ Please provide more details (at least 10 characters).")
        return

    await state.update_data(description=description)
    await message.answer(
        "✅ Thank you! Now please provide a brief title for your escalation:",
    )
    await state.set_state(EscalationStates.waiting_for_title)


@router.message(EscalationStates.waiting_for_title)
async def process_escalation_title(message: Message, state: FSMContext, user: dict, auth_token: str) -> None:
    """Process escalation title."""
    title = message.text.strip()

    if len(title) < 3:
        await message.answer("❌ Title must be at least 3 characters long.")
        return

    # Get data from state
    data = await state.get_data()
    category = data.get("category", "General")
    description = data.get("description", "")

    # Create escalation
    escalation = await escalation_client.create_escalation(
        user_id=user["id"],
        title=title,
        description=description,
        category=category,
        priority="normal",
    )

    if escalation:
        escalation_id = escalation.get("id", "N/A")
        await message.answer(
            f"✅ Escalation created successfully!\n\n"
            f"*Title:* {title}\n"
            f"*Category:* {category}\n"
            f"*Escalation ID:* {escalation_id}\n\n"
            f"You will receive a notification when your escalation is being processed.",
            parse_mode="Markdown",
        )
    else:
        await message.answer("❌ Failed to create escalation. Please try again.")

    await state.clear()


@router.callback_query(F.data == "my_escalations")
async def my_escalations(callback: CallbackQuery, user: dict, auth_token: str) -> None:
    """Show user's escalations."""
    if not user or not auth_token:
        await callback.answer("Authentication required", show_alert=True)
        return

    escalations = await escalation_client.get_user_escalations(user["id"], limit=20)

    builder = InlineKeyboardBuilder()
    builder.add(create_inline_button("← Back", callback_data="escalate_menu"))

    text = format_escalation_list(escalations) if escalations else "📭 You have no active escalations."

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("escalation_"))
async def escalation_details(callback: CallbackQuery, auth_token: str) -> None:
    """Show escalation details."""
    if not auth_token:
        await callback.answer("Authentication required", show_alert=True)
        return

    escalation_id = int(callback.data.split("_")[1])

    # Fetch escalation details
    escalation = await escalation_client.get_escalation_status(escalation_id)

    if not escalation:
        await callback.answer("Escalation not found", show_alert=True)
        return

    status = escalation.get("status", "unknown")
    title = escalation.get("title", "N/A")
    category = escalation.get("category", "General")
    created_at = escalation.get("created_at", "N/A")
    description = escalation.get("description", "No description")

    # Status emoji
    status_emoji = {
        "open": "⏳",
        "in_progress": "🔄",
        "resolved": "✅",
        "closed": "🔒",
    }.get(status, "❓")

    text = (
        f"📞 *Escalation Details*\n\n"
        f"*Title:* {title}\n"
        f"*Category:* {category}\n"
        f"*Status:* {status_emoji} {status}\n"
        f"*Created:* {created_at}\n\n"
        f"*Description:*\n{description}"
    )

    builder = InlineKeyboardBuilder()
    builder.add(create_inline_button("← Back", callback_data="my_escalations"))

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()
