"""Common handlers (help, about, contact, mentor, progress)."""

from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.config import settings
from telegram_bot.i18n import t
from telegram_bot.keyboards.common_kb import (
    get_contact_hr_keyboard,
    get_help_keyboard,
    get_mentor_tasks_keyboard,
    get_my_mentor_keyboard,
    get_my_mentor_no_mentor_keyboard,
    get_progress_keyboard,
    get_schedule_hr_keyboard,
    get_schedule_mentor_keyboard,
)
from telegram_bot.services.auth_client import auth_client
from telegram_bot.services.checklists_client import checklists_client
from telegram_bot.states.escalation_states import EscalationStates

router = Router()


@router.message(Command("help"))
@router.message(F.text == "\u2139\ufe0f Help")
@router.callback_query(F.data == "help")
async def cmd_help(update: Message | CallbackQuery, *, locale: str = "en") -> None:
    """Show help information."""
    msg = None
    if isinstance(update, CallbackQuery):
        await update.answer()
        msg = update.message
    else:
        msg = update

    if msg is None:
        return

    help_text = (
        f"*\U0001f916 {t('help.title', locale=locale)}*\n\n"
        f"*{t('help.commands', locale=locale)}*\n"
        f"  {t('help.cmd_start', locale=locale)}\n"
        f"  {t('help.cmd_menu', locale=locale)}\n"
        f"  {t('help.cmd_tasks', locale=locale)}\n"
        f"  {t('help.cmd_knowledge', locale=locale)}\n"
        f"  {t('help.cmd_meetings', locale=locale)}\n"
        f"  {t('help.cmd_documents', locale=locale)}\n"
        f"  {t('help.cmd_feedback', locale=locale)}\n"
        f"  {t('help.cmd_progress', locale=locale)}\n"
        f"  {t('help.cmd_language', locale=locale)}\n"
        f"  {t('help.cmd_help', locale=locale)}\n\n"
        f"*{t('help.features', locale=locale)}*\n"
        f"  \U0001f4cb {t('help.feat_tasks', locale=locale)}\n"
        f"  \U0001f50d {t('help.feat_kb', locale=locale)}\n"
        f"  \U0001f4c5 {t('help.feat_meetings', locale=locale)}\n"
        f"  \U0001f4c1 {t('help.feat_documents', locale=locale)}\n"
        f"  \U0001f468\u200d\U0001f3eb {t('help.feat_mentor', locale=locale)}\n"
        f"  \U0001f4de {t('help.feat_hr', locale=locale)}\n"
        f"  \U0001f4ca {t('help.feat_feedback', locale=locale)}\n"
        f"  \U0001f4ca {t('help.feat_progress', locale=locale)}\n"
        f"  \U0001f4de {t('help.feat_escalate', locale=locale)}\n\n"
        f"*{t('help.version', locale=locale, version=settings.APP_VERSION)}*"
    )

    if isinstance(update, CallbackQuery) and isinstance(msg, Message):
        await msg.edit_text(
            help_text,
            reply_markup=get_help_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    else:
        await msg.answer(
            help_text,
            reply_markup=get_help_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )


@router.message(Command("about"))
async def cmd_about(message: Message, *, locale: str = "en") -> None:
    """Show information about the bot."""
    about_text = (
        f"*{t('about.title', locale=locale, app_name=settings.APP_NAME)}*\n\n"
        f"{t('about.description', locale=locale)}\n\n"
        f"*{t('about.features', locale=locale)}*\n"
        f"  \U0001f4cb Personalized onboarding checklists\n"
        f"  \U0001f50d Knowledge base with intelligent search\n"
        f"  \U0001f468\u200d\U0001f3eb Mentor assignment and communication\n"
        f"  \U0001f4c5 Meeting scheduling and management\n"
        f"  \U0001f4c1 Document access and resources\n"
        f"  \U0001f4de HR support and escalation system\n"
        f"  \U0001f4ca Progress tracking and analytics\n"
        f"  \U0001f4ca Feedback collection and surveys\n"
        f"  \U0001f514 Smart notifications and reminders\n\n"
        f"*{t('about.technology', locale=locale)}*\n"
        f"  Python 3.14+ with async/await\n"
        f"  aiogram 3.x for Telegram API\n"
        f"  FastAPI for REST APIs\n"
        f"  Microservices architecture\n\n"
        f"*{t('about.version', locale=locale, version=settings.APP_VERSION)}*\n"
        f"*{t('about.status', locale=locale)}*"
    )

    await message.answer(about_text, parse_mode="Markdown")


@router.message(F.text == "\U0001f4de Contact HR")
@router.message(F.text == "Contact HR")
@router.callback_query(F.data == "contact_hr")
async def contact_hr(
    update: Message | CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Contact HR department."""
    msg = None
    if isinstance(update, CallbackQuery):
        await update.answer()
        msg = update.message
    else:
        msg = update

    if msg is None:
        return

    contact_text = (
        f"*\U0001f4de {t('hr.title', locale=locale)}*\n\n"
        f"*{t('hr.office_hours', locale=locale)}*\n\n"
        f"*{t('hr.contact_info', locale=locale)}*\n"
        f"  \U0001f4e7 {t('hr.email', locale=locale)}\n"
        f"  \U0001f4f1 {t('hr.phone', locale=locale)}\n"
        f"  \U0001f3e2 {t('hr.office', locale=locale)}\n\n"
        f"*Emergency Contact:*\n"
        f"  \U0001f4f1 {t('hr.emergency', locale=locale)}\n\n"
        f"*{t('hr.how_to', locale=locale)}*\n"
        f"  1. \U0001f4de {t('hr.how_escalate', locale=locale)}\n"
        f"  2. \U0001f4e7 {t('hr.how_email', locale=locale)}\n"
        f"  3. \U0001f3e2 {t('hr.how_visit', locale=locale)}\n"
        f"  4. \U0001f4f1 {t('hr.how_call', locale=locale)}"
    )

    if user:
        first = user.get("first_name", "N/A")
        last = user.get("last_name", "")
        emp_id = user.get("employee_id", "N/A")
        contact_text += (
            f"\n\n*{t('hr.your_info', locale=locale)}*\n"
            f"  {t('hr.your_name', locale=locale, first_name=first, last_name=last)}\n"
            f"  {t('hr.your_id', locale=locale, employee_id=emp_id)}"
        )

    if isinstance(update, CallbackQuery) and isinstance(msg, Message):
        await msg.edit_text(
            contact_text,
            reply_markup=get_contact_hr_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    else:
        await msg.answer(
            contact_text,
            reply_markup=get_contact_hr_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "send_to_hr")
async def send_to_hr(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "en"
) -> None:
    """Start sending a message to HR."""
    if callback.message is None:
        return

    await state.set_state(EscalationStates.waiting_for_description)
    await state.update_data(category="Contact HR")
    await callback.message.edit_text(
        f"\U0001f4e8 *{t('hr.btn_send_message', locale=locale)}*\n\n"
        f"Please type your message and it will be forwarded to HR.",
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "schedule_hr")
async def schedule_hr(callback: CallbackQuery, *, locale: str = "en") -> None:
    """Schedule a meeting with HR."""
    if callback.message is None:
        return

    await callback.message.edit_text(
        f"\U0001f4c5 *{t('hr.btn_schedule_meeting', locale=locale)}*\n\n"
        f"Use the Meetings menu to schedule a meeting with HR.\n\n"
        f"Select the meeting type as 'HR' when scheduling.",
        reply_markup=get_schedule_hr_keyboard(locale=locale).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(F.text == "\U0001f468\u200d\U0001f3eb My Mentor")
@router.message(F.text == "My Mentor")
@router.callback_query(F.data == "my_mentor")
async def my_mentor(
    update: Message | CallbackQuery,
    user: dict,
    auth_token: str,
    *,
    locale: str = "en",
) -> None:
    """Show mentor information."""
    msg = None
    if isinstance(update, CallbackQuery):
        await update.answer()
        msg = update.message
    else:
        msg = update

    if msg is None:
        return

    if not user:
        await msg.answer(t("common.auth_required", locale=locale))
        return

    mentor_id = user.get("mentor_id")
    if not mentor_id:
        mentor_text = (
            f"*\U0001f468\u200d\U0001f3eb {t('mentor.title', locale=locale)}*\n\n"
            f"{t('mentor.not_assigned', locale=locale)}"
        )
    else:
        mentor_info = await auth_client.get_mentor_info(mentor_id, auth_token)

        if mentor_info:
            mentor_name = f"{mentor_info.get('first_name', '')} {mentor_info.get('last_name', '')}"
            mentor_text = (
                f"*\U0001f468\u200d\U0001f3eb {t('mentor.title', locale=locale)}*\n\n"
                f"{t('mentor.name', locale=locale, name=mentor_name)}\n"
                f"{t('mentor.role', locale=locale, role=mentor_info.get('position', 'N/A'))}\n"
                f"{t('mentor.department', locale=locale, department=mentor_info.get('department', 'N/A'))}\n\n"
                f"*{t('mentor.contact_info', locale=locale)}*\n"
                f"  \U0001f4e7 {mentor_info.get('email', 'N/A')}\n"
                f"  \U0001f4f1 {mentor_info.get('phone', 'N/A')}\n\n"
                f"*{t('mentor.help_with', locale=locale)}*\n"
                f"  \U0001f5a5\ufe0f {t('mentor.help_technical', locale=locale)}\n"
                f"  \U0001f465 {t('mentor.help_team', locale=locale)}\n"
                f"  \U0001f4dd {t('mentor.help_reviews', locale=locale)}\n"
                f"  \U0001f680 {t('mentor.help_career', locale=locale)}\n"
                f"  \U0001f4c5 {t('mentor.help_daily', locale=locale)}"
            )
        else:
            mentor_text = (
                f"*\U0001f468\u200d\U0001f3eb {t('mentor.title', locale=locale)}*\n\n"
                f"Could not load mentor information. Please try again later."
            )

    if not mentor_id:
        keyboard = get_my_mentor_no_mentor_keyboard(locale=locale)
    else:
        keyboard = get_my_mentor_keyboard(locale=locale)

    if isinstance(update, CallbackQuery) and isinstance(msg, Message):
        await msg.edit_text(
            mentor_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown"
        )
    else:
        await msg.answer(
            mentor_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown"
        )


@router.callback_query(F.data == "message_mentor")
async def message_mentor(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "en"
) -> None:
    """Start sending a message to mentor."""
    if callback.message is None:
        return

    await callback.message.edit_text(
        f"\U0001f4ac *{t('mentor.btn_message', locale=locale)}*\n\n"
        f"Type your message below and it will be sent to your mentor.",
        parse_mode="Markdown",
    )
    await state.set_state(EscalationStates.waiting_for_description)
    await state.update_data(category="Contact Mentor")


@router.callback_query(F.data == "schedule_mentor")
async def schedule_mentor(callback: CallbackQuery, *, locale: str = "en") -> None:
    """Schedule a meeting with mentor."""
    if callback.message is None:
        return

    await callback.message.edit_text(
        f"\U0001f4c5 *{t('mentor.btn_schedule', locale=locale)}*\n\n"
        f"Use the Meetings menu to schedule a meeting with your mentor.\n\n"
        f"Select the meeting type as 'Mentor' when scheduling.",
        reply_markup=get_schedule_mentor_keyboard(locale=locale).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "mentor_tasks")
async def mentor_tasks(
    callback: CallbackQuery, auth_token: str, *, locale: str = "en"
) -> None:
    """Show tasks shared with mentor."""
    if callback.message is None:
        return

    tasks = await checklists_client.get_assigned_tasks(auth_token)
    pending = [t for t in tasks if t.get("status") in ("pending", "in_progress")]

    text = f"\U0001f4cb *{t('mentor.btn_tasks', locale=locale)}*\n\n"
    if pending:
        text += f"You have {len(pending)} active task(s):\n\n"
        for task in pending[:5]:
            title = task.get("title", "Untitled")
            status = task.get("status", "pending")
            emoji = "\U0001f4dd" if status == "pending" else "\U0001f504"
            text += f"  {emoji} {title}\n"
    else:
        text += "No active tasks found."

    await callback.message.edit_text(
        text,
        reply_markup=get_mentor_tasks_keyboard(locale=locale).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(Command("progress"))
@router.message(F.text == "\U0001f4ca Progress")
@router.callback_query(F.data == "progress")
async def progress(
    update: Message | CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Show progress dashboard."""
    msg = None
    if isinstance(update, CallbackQuery):
        await update.answer()
        msg = update.message
    else:
        msg = update

    if msg is None:
        return

    if not user:
        await msg.answer(t("common.auth_required", locale=locale))
        return

    checklists = await checklists_client.get_user_checklists(user["id"], auth_token)

    if not checklists:
        await msg.answer(t("progress.no_checklists", locale=locale))
        return

    active_checklist = checklists[0]
    checklist_id = active_checklist["id"]

    progress_info = await checklists_client.get_checklist_progress(
        checklist_id, auth_token
    )

    tasks = await checklists_client.get_checklist_tasks(checklist_id, auth_token)
    next_task = "View tasks for details"
    if tasks:
        for task in tasks:
            if task.get("status") in ("pending", "in_progress"):
                next_task = task.get("title", "View tasks for details")
                break

    if not progress_info:
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
        start_date = (
            datetime.fromisoformat(progress_info["start_date"])
            if progress_info.get("start_date")
            else None
        )
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

    bars = 20
    filled = int(progress_data["overall_progress"] / 100 * bars)
    bar = "\u2588" * filled + "\u2591" * (bars - filled)

    text = (
        f"*\U0001f4ca {t('progress.title', locale=locale)}*\n\n"
        f"{t('progress.overall', locale=locale, progress=progress_data['overall_progress'])}\n"
        f"`{bar}`\n\n"
        f"{t('progress.tasks', locale=locale, completed=progress_data['tasks_completed'], total=progress_data['tasks_total'])}\n"
    )
    day_passed = progress_data["days_passed"]
    day_total = progress_data["days_total"]
    text += (
        f"{t('progress.onboarding_day', locale=locale, passed=day_passed, total=day_total)}\n\n"
        f"{t('progress.next_task', locale=locale, task=progress_data['next_task'])}\n"
        f"{t('progress.deadline', locale=locale, deadline=progress_data['upcoming_deadline'])}\n\n"
        f"{t('progress.keep_going', locale=locale)}"
    )

    if isinstance(update, CallbackQuery) and isinstance(msg, Message):
        await msg.edit_text(
            text,
            reply_markup=get_progress_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    else:
        await msg.answer(
            text,
            reply_markup=get_progress_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
