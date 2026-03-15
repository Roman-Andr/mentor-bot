"""Feedback and pulse survey handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button
from telegram_bot.services.feedback_client import feedback_client
from telegram_bot.states.feedback_states import FeedbackStates
from telegram_bot.utils.formatters import format_feedback_menu

router = Router()


@router.message(Command("feedback"))
@router.message(F.text == "📊 Feedback")
@router.callback_query(F.data == "feedback_menu")
async def feedback_menu(update: Message | CallbackQuery, state: FSMContext) -> None:
    """Show feedback menu."""
    if isinstance(update, CallbackQuery):
        message = update.message
        await update.answer()
    else:
        message = update

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("😊 Daily Pulse Survey", callback_data="pulse_survey", style=ButtonStyle.PRIMARY),
        create_inline_button("⭐ Rate Experience", callback_data="rate_experience", style=ButtonStyle.PRIMARY),
        create_inline_button(
            "💬 Comments & Suggestions", callback_data="comments_suggestions", style=ButtonStyle.PRIMARY
        ),
        create_inline_button("← Menu", callback_data="menu"),
    )
    builder.adjust(1)

    if isinstance(update, CallbackQuery):
        await message.edit_text(
            format_feedback_menu(),
            reply_markup=builder.as_markup(),
            parse_mode="Markdown",
        )
    else:
        await message.answer(
            format_feedback_menu(),
            reply_markup=builder.as_markup(),
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "pulse_survey")
async def start_pulse_survey(callback: CallbackQuery, state: FSMContext) -> None:
    """Start daily pulse survey."""
    await callback.message.edit_text(
        "📊 *Daily Pulse Survey*\n\n"
        "How are you feeling today?\n"
        "Please rate your well-being on a scale of 1-10:\n\n"
        "1 = Very bad\n"
        "5 = Average\n"
        "10 = Excellent",
        parse_mode="Markdown",
    )
    await state.set_state(FeedbackStates.waiting_for_pulse_rating)
    await callback.answer()


@router.message(FeedbackStates.waiting_for_pulse_rating)
async def process_pulse_rating(message: Message, state: FSMContext, user: dict, auth_token: str) -> None:
    """Process pulse survey rating."""
    try:
        rating = int(message.text.strip())
        if 1 <= rating <= 10:
            if user and auth_token:
                success = await feedback_client.submit_pulse_survey(user["id"], rating, auth_token)
                if not success:
                    await message.answer("❌ Failed to submit feedback. Please try again.")
                    return

            await message.answer(
                f"✅ Thank you for your feedback!\n\n"
                f"Your rating: {rating}/10\n\n"
                f"Your input helps us improve your onboarding experience.",
            )
            await state.clear()
        else:
            await message.answer("❌ Please enter a number between 1 and 10.")
    except ValueError:
        await message.answer("❌ Please enter a valid number between 1 and 10.")


@router.callback_query(F.data == "rate_experience")
async def start_experience_rating(callback: CallbackQuery, state: FSMContext) -> None:
    """Start experience rating."""
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.add(create_inline_button(f"⭐ {i}", callback_data=f"rate_{i}", style=ButtonStyle.PRIMARY))
    builder.adjust(5)
    builder.add(create_inline_button("← Back", callback_data="feedback_menu"))

    await callback.message.edit_text(
        "⭐ *Rate Your Experience*\n\nHow would you rate your onboarding experience so far?",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rate_"))
async def process_experience_rating(callback: CallbackQuery, user: dict, auth_token: str) -> None:
    """Process experience rating."""
    rating = int(callback.data.split("_")[1])

    if user and auth_token:
        success = await feedback_client.submit_experience_rating(user["id"], rating, auth_token)
        if not success:
            await callback.answer("❌ Failed to submit rating. Please try again.", show_alert=True)
            return

    await callback.message.edit_text(
        f"✅ Thank you for your rating!\n\nYou rated your experience: {rating}/5 stars\n\nWe appreciate your feedback!",
    )
    await callback.answer()


@router.callback_query(F.data == "comments_suggestions")
async def start_comments(callback: CallbackQuery, state: FSMContext) -> None:
    """Start comments and suggestions."""
    await callback.message.edit_text(
        "💬 *Comments & Suggestions*\n\n"
        "Please share your thoughts, suggestions, or any issues you've encountered.\n"
        "Your feedback is valuable to us!",
        parse_mode="Markdown",
    )
    await state.set_state(FeedbackStates.waiting_for_comments)
    await callback.answer()


@router.message(FeedbackStates.waiting_for_comments)
async def process_comments(message: Message, state: FSMContext, user: dict, auth_token: str) -> None:
    """Process comments and suggestions."""
    comment = message.text.strip()

    if len(comment) < 10:
        await message.answer("❌ Please provide more detailed feedback (at least 10 characters).")
        return

    if user and auth_token:
        success = await feedback_client.submit_comment(user["id"], comment, auth_token)
        if not success:
            await message.answer("❌ Failed to submit comment. Please try again.")
            return

    await message.answer(
        "✅ Thank you for your feedback!\n\nYour comments have been received and will be reviewed by our team.",
    )
    await state.clear()


@router.callback_query(F.data == "contact_hr")
async def contact_hr_from_feedback(callback: CallbackQuery, user: dict) -> None:
    """Contact HR from feedback menu."""
    contact_text = (
        "📞 *Contact HR Department*\n\n"
        "*HR Office Hours:*\n"
        "Monday-Friday: 9:00-18:00\n\n"
        "*Contact Information:*\n"
        "• 📧 Email: hr@company.com\n"
        "• 📱 Phone: +1 (555) 123-4567\n"
        "• 🏢 Office: Building A, Floor 3\n\n"
        "*How to reach us:*\n"
        "1. Use this bot's escalation feature\n"
        "2. Send an email with your question\n"
        "3. Visit the HR office during office hours"
    )

    if user:
        contact_text += f"\n\n*Your Information:*\n• Name: {user.get('first_name', 'N/A')} {user.get('last_name', '')}"

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("📨 Send Message", callback_data="send_to_hr", style=ButtonStyle.PRIMARY),
        create_inline_button("← Back", callback_data="feedback_menu"),
    )
    builder.adjust(1)

    await callback.message.edit_text(contact_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()
