"""Common handlers (help, about, contact, mentor, progress)."""

from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.config import settings
from telegram_bot.i18n import t
from telegram_bot.keyboards.common_kb import (
    get_help_keyboard,
    get_mentor_tasks_keyboard,
    get_my_mentor_keyboard,
    get_my_mentor_no_mentor_keyboard,
    get_progress_keyboard,
    get_schedule_mentor_keyboard,
)
from telegram_bot.services.auth_client import auth_client
from telegram_bot.services.checklists_client import checklists_client
from telegram_bot.states.escalation_states import EscalationStates

router = Router()


@router.message(Command("help"))
@router.message(F.text == "\u2139\ufe0f Help")
@router.message(F.text == "Help")
@router.message(F.text == "\u2139\ufe0f \u041f\u043e\u043c\u043e\u0449\u044c")
@router.message(F.text == "\u041f\u043e\u043c\u043e\u0449\u044c")
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


@router.message(F.text == "\U0001f468\u200d\U0001f3eb My Mentor")
@router.message(F.text == "My Mentor")
@router.message(
    F.text
    == "\U0001f468\u200d\U0001f3eb \u041c\u043e\u0439 \u043d\u0430\u0441\u0442\u0430\u0432\u043d\u0438\u043a"
)
@router.message(
    F.text
    == "\u041c\u043e\u0439 \u043d\u0430\u0441\u0442\u0430\u0432\u043d\u0438\u043a"
)
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

    import logging

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
            dept = mentor_info.get("department")
            dept_name = (
                dept.get("name", "N/A") if isinstance(dept, dict) else (dept or "N/A")
            )
            mentor_text = (
                f"*\U0001f468\u200d\U0001f3eb {t('mentor.title', locale=locale)}*\n\n"
                f"{t('mentor.name', locale=locale, name=mentor_name)}\n"
                f"{t('mentor.role', locale=locale, role=mentor_info.get('position', 'N/A'))}\n"
                f"{t('mentor.department', locale=locale, department=dept_name)}\n\n"
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
@router.message(F.text == "Progress")
@router.message(F.text == "\U0001f4ca \u041f\u0440\u043e\u0433\u0440\u0435\u0441\u0441")
@router.message(F.text == "\u041f\u0440\u043e\u0433\u0440\u0435\u0441\u0441")
@router.callback_query(F.data == "progress")
@router.callback_query(F.data.startswith("progress_"))
async def progress(
    update: Message | CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Show progress dashboard."""
    msg = None
    specific_checklist_id = None

    if isinstance(update, CallbackQuery):
        await update.answer()
        msg = update.message
        # Extract checklist_id from callback data if present
        if update.data and update.data.startswith("progress_"):
            parts = update.data.split("_")
            if len(parts) > 1:
                specific_checklist_id = int(parts[1])
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

    # Use specific checklist_id if provided, otherwise use first checklist
    if specific_checklist_id is not None:
        active_checklist = None
        for cl in checklists:
            if cl.get("id") == specific_checklist_id:
                active_checklist = cl
                break
        if not active_checklist:
            active_checklist = checklists[0]
    else:
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
        # Format the due date nicely
        due_date_raw = active_checklist.get("due_date")
        upcoming_deadline = ""
        if due_date_raw:
            try:
                due_dt = datetime.fromisoformat(due_date_raw)
                upcoming_deadline = due_dt.strftime("%d.%m.%Y")
            except ValueError:
                upcoming_deadline = due_date_raw

        progress_data = {
            "overall_progress": active_checklist.get("progress_percentage", 0),
            "tasks_completed": active_checklist.get("completed_tasks", 0),
            "tasks_total": active_checklist.get("total_tasks", 0),
            "days_passed": 0,
            "days_total": 30,
            "next_task": next_task,
            "upcoming_deadline": upcoming_deadline,
        }
    else:
        start_date = (
            datetime.fromisoformat(progress_info["start_date"])
            if progress_info.get("start_date")
            else None
        )
        days_passed = (datetime.now(UTC) - start_date).days if start_date else 0

        # Format the due date nicely
        due_date_raw = progress_info.get("due_date")
        upcoming_deadline = ""
        if due_date_raw:
            try:
                due_dt = datetime.fromisoformat(due_date_raw)
                upcoming_deadline = due_dt.strftime("%d.%m.%Y")
            except ValueError:
                upcoming_deadline = due_date_raw

        progress_data = {
            "overall_progress": progress_info.get("progress_percentage", 0),
            "tasks_completed": progress_info.get("completed_tasks", 0),
            "tasks_total": progress_info.get("total_tasks", 0),
            "days_passed": days_passed,
            "days_total": progress_info.get("days_remaining", 30) + days_passed,
            "next_task": next_task,
            "upcoming_deadline": upcoming_deadline,
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

    if isinstance(update, CallbackQuery):
        await msg.edit_text(
            text,
            reply_markup=get_progress_keyboard(checklist_id, locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    else:
        await msg.answer(
            text,
            reply_markup=get_progress_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
