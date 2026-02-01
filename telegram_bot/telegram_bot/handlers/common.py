"""Common handlers (help, about, contact, etc.)."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.config import settings

router = Router()


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Help")
@router.callback_query(F.data == "help")
async def cmd_help(update: Message | CallbackQuery) -> None:
    """Show help information."""
    if isinstance(update, CallbackQuery):
        message = update.message
        await update.answer()
    else:
        message = update

    help_text = (
        "🤖 *Mentor Bot Help*\n\n"
        "*Available Commands:*\n"
        "• /start - Start or restart the bot\n"
        "• /menu - Show main menu\n"
        "• /tasks - Show your tasks\n"
        "• /checklist - Show checklist progress\n"
        "• /knowledge - Search knowledge base\n"
        "• /help - Show this help\n\n"
        "*Main Features:*\n"
        "• 📋 *My Tasks* - View and manage onboarding checklist\n"
        "• 🔍 *Knowledge Base* - Search for information and FAQ\n"
        "• 👨‍🏫 *My Mentor* - Contact your assigned mentor\n"
        "• 📞 *Contact HR* - Get help from HR department\n"
        "• 📊 *Progress* - Track your onboarding progress\n\n"
        "*Need Help?*\n"
        "If you encounter any issues, please contact:\n"
        "• Your assigned mentor\n"
        "• HR department\n"
        "• IT support\n\n"
        f"*Bot Version:* {settings.APP_VERSION}"
    )

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📋 Open Menu", callback_data="menu"),
        InlineKeyboardButton(text="📞 Contact HR", callback_data="contact_hr"),
    )
    builder.adjust(1)

    await message.answer(help_text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    """Show information about the bot."""
    about_text = (
        f"*{settings.APP_NAME}*\n\n"
        "🤖 An intelligent onboarding assistant for new employees.\n\n"
        "*Features:*\n"
        "• Personalized onboarding checklists\n"
        "• Knowledge base with search\n"
        "• Mentor assignment and communication\n"
        "• HR support and escalation\n"
        "• Progress tracking and reminders\n\n"
        "*Technology:*\n"
        "• Built with Python and aiogram\n"
        "• Microservices architecture\n"
        "• PostgreSQL database\n"
        "• Redis caching\n\n"
        f"*Version:* {settings.APP_VERSION}\n"
        "*Status:* ✅ Operational"
    )

    await message.answer(about_text, parse_mode="Markdown")


@router.message(F.text == "📞 Contact HR")
@router.message(F.text == "Contact HR")
@router.callback_query(F.data == "contact_hr")
async def contact_hr(update: Message | CallbackQuery, user: dict) -> None:
    """Contact HR department."""
    if isinstance(update, CallbackQuery):
        message = update.message
        await update.answer()
    else:
        message = update

    contact_text = (
        "📞 *Contact HR Department*\n\n"
        "*HR Office Hours:*\n"
        "Monday-Friday: 9:00-18:00\n\n"
        "*Contact Information:*\n"
        "• 📧 Email: hr@company.com\n"
        "• 📱 Phone: +1 (555) 123-4567\n"
        "• 🏢 Office: Building A, Floor 3\n\n"
        "*Emergency Contact:*\n"
        "• 📱 After Hours: +1 (555) 987-6543\n\n"
        "*How to reach us:*\n"
        "1. Use this bot's escalation feature\n"
        "2. Send an email with your question\n"
        "3. Visit the HR office during office hours\n"
        "4. Call for urgent matters"
    )

    if user:
        contact_text += f"\n\n*Your Information:*\n• Name: {user.get('first_name', 'N/A')} {user.get('last_name', '')}\n• Employee ID: {user.get('employee_id', 'N/A')}"

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📨 Send Message", callback_data="send_to_hr"),
        InlineKeyboardButton(text="📅 Schedule Meeting", callback_data="schedule_hr"),
        InlineKeyboardButton(text="← Menu", callback_data="menu"),
    )
    builder.adjust(1)

    await message.answer(contact_text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.message(F.text == "👨‍🏫 My Mentor")
@router.message(F.text == "My Mentor")
@router.callback_query(F.data == "my_mentor")
async def my_mentor(update: Message | CallbackQuery, user: dict) -> None:
    """Show mentor information."""
    if isinstance(update, CallbackQuery):
        message = update.message
        await update.answer()
    else:
        message = update

    if not user:
        await message.answer("You need to be registered to see mentor information.\nUse /start to register.")
        return

    mentor_info = {
        "name": "Alex Johnson",
        "role": "Senior Developer",
        "department": "Engineering",
        "email": "alex.johnson@company.com",
        "phone": "+1 (555) 234-5678",
        "availability": "Mon-Fri, 10:00-16:00",
    }

    mentor_text = (
        "👨‍🏫 *Your Mentor*\n\n"
        f"*Name:* {mentor_info['name']}\n"
        f"*Role:* {mentor_info['role']}\n"
        f"*Department:* {mentor_info['department']}\n"
        f"*Availability:* {mentor_info['availability']}\n\n"
        "*Contact Information:*\n"
        f"• 📧 {mentor_info['email']}\n"
        f"• 📱 {mentor_info['phone']}\n\n"
        "*Your mentor is here to help you with:*\n"
        "• Technical questions\n"
        "• Team integration\n"
        "• Code reviews\n"
        "• Career guidance\n"
        "• Daily work challenges"
    )

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="💬 Message Mentor", callback_data="message_mentor"),
        InlineKeyboardButton(text="📅 Schedule Meeting", callback_data="schedule_mentor"),
        InlineKeyboardButton(text="📋 Shared Tasks", callback_data="mentor_tasks"),
        InlineKeyboardButton(text="← Menu", callback_data="menu"),
    )
    builder.adjust(2)

    await message.answer(mentor_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
