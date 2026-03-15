"""Common handlers (help, about, contact, etc.)."""

from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.config import settings
from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button
from telegram_bot.services.checklists_client import checklists_client

router = Router()


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Help")
@router.callback_query(F.data == "help")
async def cmd_help(update: Message | CallbackQuery) -> None:
    """Show help information."""
    message = None
    if isinstance(update, CallbackQuery):
        await update.answer()
        message = update.message
    else:
        message = update

    if message is None:
        return

    help_text = (
        "🤖 *Mentor Bot Help*\n\n"
        "*Available Commands:*\n"
        "• /start - Start or restart the bot\n"
        "• /menu - Show main menu\n"
        "• /tasks - Show your tasks\n"
        "• /checklist - Show checklist progress\n"
        "• /knowledge - Search knowledge base\n"
        "• /meetings - View and manage meetings\n"
        "• /documents - Access department documents\n"
        "• /feedback - Provide feedback\n"
        "• /progress - View onboarding progress\n"
        "• /help - Show this help\n\n"
        "*Main Features:*\n"
        "• 📋 *My Tasks* - View and manage onboarding checklist\n"
        "• 🔍 *Knowledge Base* - Search for information and FAQ\n"
        "• 📅 *Meetings* - Schedule and manage meetings with mentor/HR\n"
        "• 📁 *Documents* - Access department-specific documents and resources\n"
        "• 👨‍🏫 *My Mentor* - Contact your assigned mentor\n"
        "• 📞 *Contact HR* - Get help from HR department\n"
        "• 📊 *Feedback* - Share your thoughts and rate your experience\n"
        "• 📊 *Progress* - Track your onboarding progress\n"
        "• 📞 *Escalate* - Escalate issues to HR or mentor\n\n"
        "*Need Help?*\n"
        "If you encounter any issues, please contact:\n"
        "• Your assigned mentor\n"
        "• HR department\n"
        "• IT support\n\n"
        f"*Bot Version:* {settings.APP_VERSION}"
    )

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("📋 Open Menu", callback_data="menu", style=ButtonStyle.PRIMARY),
        create_inline_button("📞 Contact HR", callback_data="contact_hr", style=ButtonStyle.PRIMARY),
        create_inline_button("👨‍🏫 My Mentor", callback_data="my_mentor", style=ButtonStyle.PRIMARY),
    )
    builder.adjust(1)

    if isinstance(update, CallbackQuery) and isinstance(message, Message):
        await message.edit_text(help_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await message.answer(help_text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    """Show information about the bot."""
    about_text = (
        f"*{settings.APP_NAME}*\n\n"
        "🤖 An intelligent onboarding assistant for new employees.\n\n"
        "*Features:*\n"
        "• 📋 Personalized onboarding checklists\n"
        "• 🔍 Knowledge base with intelligent search\n"
        "• 👨‍ Mentor assignment and communication\n"
        "• 📅 Meeting scheduling and management\n"
        "• 📁 Document access and resources\n"
        "• 📞 HR support and escalation system\n"
        "• 📊 Progress tracking and analytics\n"
        "• 📊 Feedback collection and surveys\n"
        "• 🔔 Smart notifications and reminders\n\n"
        "*Technology:*\n"
        "• Python 3.11+ with async/await\n"
        "• aiogram 3.x for Telegram API\n"
        "• FastAPI for REST APIs\n"
        "• Microservices architecture\n"
        "• PostgreSQL database\n"
        "• Redis caching\n"
        "• Docker containerization\n\n"
        f"*Version:* {settings.APP_VERSION}\n"
        "*Status:* ✅ Operational\n\n"
        "This bot is part of the Mentor-Bot onboarding system, helping new employees transition smoothly into their roles."
    )

    await message.answer(about_text, parse_mode="Markdown")


@router.message(F.text == "📞 Contact HR")
@router.message(F.text == "Contact HR")
@router.callback_query(F.data == "contact_hr")
async def contact_hr(update: Message | CallbackQuery, user: dict) -> None:
    """Contact HR department."""
    message = None
    if isinstance(update, CallbackQuery):
        await update.answer()
        message = update.message
    else:
        message = update

    if message is None:
        return

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
        "1. 📞 Use the Escalate feature in the menu\n"
        "2. 📧 Send an email with your question\n"
        "3. 🏢 Visit the HR office during office hours\n"
        "4. 📱 Call for urgent matters\n\n"
        "*Tip:* You can also schedule a meeting with HR directly from the Meetings menu!"
    )

    if user:
        contact_text += f"\n\n*Your Information:*\n• Name: {user.get('first_name', 'N/A')} {user.get('last_name', '')}\n• Employee ID: {user.get('employee_id', 'N/A')}"

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("📨 Send Message", callback_data="send_to_hr", style=ButtonStyle.PRIMARY),
        create_inline_button("📅 Schedule Meeting", callback_data="schedule_hr", style=ButtonStyle.PRIMARY),
        create_inline_button("← Menu", callback_data="menu"),
    )
    builder.adjust(1)

    if isinstance(update, CallbackQuery) and isinstance(message, Message):
        await message.edit_text(contact_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await message.answer(contact_text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.message(F.text == "👨‍🏫 My Mentor")
@router.message(F.text == "My Mentor")
@router.callback_query(F.data == "my_mentor")
async def my_mentor(update: Message | CallbackQuery, user: dict) -> None:
    """Show mentor information."""
    message = None
    if isinstance(update, CallbackQuery):
        await update.answer()
        message = update.message
    else:
        message = update

    if message is None:
        return

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
        "• 🖥️ Technical questions and coding\n"
        "• 👥 Team integration and culture\n"
        "• 📝 Code reviews and best practices\n"
        "• 🚀 Career guidance and growth\n"
        "• 📅 Daily work challenges and blockers\n"
        "• 🎯 Goal setting and achievement\n\n"
        "Your mentor is your go-to person for anything related to your role and team!"
    )

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("💬 Message Mentor", callback_data="message_mentor", style=ButtonStyle.PRIMARY),
        create_inline_button("📅 Schedule Meeting", callback_data="schedule_mentor", style=ButtonStyle.PRIMARY),
        create_inline_button("📋 Shared Tasks", callback_data="mentor_tasks", style=ButtonStyle.PRIMARY),
        create_inline_button("← Menu", callback_data="menu"),
    )
    builder.adjust(1)

    if isinstance(update, CallbackQuery) and isinstance(message, Message):
        await message.edit_text(mentor_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await message.answer(mentor_text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.message(Command("progress"))
@router.message(F.text == "📊 Progress")
@router.callback_query(F.data == "progress")
async def progress(update: Message | CallbackQuery, user: dict) -> None:
    """Show progress dashboard."""
    message = None
    if isinstance(update, CallbackQuery):
        await update.answer()
        message = update.message
    else:
        message = update

    if message is None:
        return

    if not user:
        await message.answer("You need to be registered to view progress.\nUse /start to register.")
        return

    # Fetch checklists for user
    checklists = await checklists_client.get_user_checklists(user["id"], user["access_token"])

    if not checklists:
        await message.answer(
            "📭 You don't have any active checklists.\n\n"
            "Checklists are created automatically when you start onboarding."
        )
        return

    # Get the first (active) checklist
    active_checklist = checklists[0]
    checklist_id = active_checklist["id"]

    # Fetch detailed progress for the active checklist
    progress_info = await checklists_client.get_checklist_progress(checklist_id, user["access_token"])

    # Fetch tasks to find the next pending task
    tasks = await checklists_client.get_checklist_tasks(checklist_id, user["access_token"])
    next_task = "View tasks for details"
    if tasks:
        # Find first pending task
        for task in tasks:
            if task.get("status") in ["pending", "in_progress"]:
                next_task = task.get("title", "View tasks for details")
                break

    if not progress_info:
        # Fallback to basic checklist data
        progress_data = {
            "overall_progress": active_checklist.get("progress_percentage", 0),
            "tasks_completed": active_checklist.get("completed_tasks", 0),
            "tasks_total": active_checklist.get("total_tasks", 0),
            "days_passed": 0,
            "days_total": 30,
            "next_task": next_task,
            "upcoming_deadline": active_checklist.get("due_date", ""),
        }
    else:
        # Calculate days passed from start date
        start_date = datetime.fromisoformat(progress_info["start_date"]) if progress_info.get("start_date") else None
        days_passed = (datetime.now(UTC) - start_date).days if start_date else 0

        progress_data = {
            "overall_progress": progress_info.get("progress_percentage", 0),
            "tasks_completed": progress_info.get("completed_tasks", 0),
            "tasks_total": progress_info.get("total_tasks", 0),
            "days_passed": days_passed,
            "days_total": progress_info.get("days_remaining", 30) + days_passed,
            "next_task": next_task,
            "upcoming_deadline": progress_info.get("due_date", ""),
        }

    # Progress bar
    bars = 20
    filled = int(progress_data["overall_progress"] / 100 * bars)
    bar = "█" * filled + "░" * (bars - filled)

    text = (
        "📊 *Your Progress*\n\n"
        f"*Overall Progress:* {progress_data['overall_progress']}%\n"
        f"`{bar}`\n\n"
        f"*Tasks:* {progress_data['tasks_completed']}/{progress_data['tasks_total']} completed\n"
        f"*Onboarding:* Day {progress_data['days_passed']}/{progress_data['days_total']}\n\n"
        f"*Next Task:* {progress_data['next_task']}\n"
        f"*Deadline:* {progress_data['upcoming_deadline']}\n\n"
        "Keep up the great work! 🎉"
    )

    builder = InlineKeyboardBuilder()
    builder.add(create_inline_button("📋 My Tasks", callback_data="my_tasks", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("📅 Meetings", callback_data="meetings_menu", style=ButtonStyle.PRIMARY))
    builder.add(create_inline_button("← Menu", callback_data="menu"))
    builder.adjust(1)

    if isinstance(update, CallbackQuery) and isinstance(message, Message):
        await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
