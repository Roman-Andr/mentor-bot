"""Meeting management handlers."""

from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button
from telegram_bot.services.meeting_client import meeting_client
from telegram_bot.states.meeting_states import MeetingStates
from telegram_bot.utils.formatters import format_meeting_list

router = Router()


@router.message(Command("meetings"))
@router.message(F.text == "📅 Meetings")
@router.callback_query(F.data == "meetings_menu")
async def meetings_menu(update: Message | CallbackQuery, user: dict, auth_token: str) -> None:
    """Show meetings menu."""
    if isinstance(update, CallbackQuery):
        message = update.message
        await update.answer()
    else:
        message = update

    if not user or not auth_token:
        await message.answer("You need to be registered to view meetings.\nUse /start to register.")
        return

    # Get upcoming meetings
    meetings = await meeting_client.get_upcoming_meetings(user["id"], limit=5)

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("📋 My Meetings", callback_data="my_meetings", style=ButtonStyle.PRIMARY),
        create_inline_button("➕ Schedule Meeting", callback_data="schedule_meeting", style=ButtonStyle.PRIMARY),
        create_inline_button("← Menu", callback_data="menu"),
    )
    builder.adjust(1)

    text = "📅 *Meetings*\n\n"
    if meetings:
        text += format_meeting_list(meetings)
        text += "\n"
    else:
        text += "You have no upcoming meetings.\n\n"

    text += "Use the options below to manage your meetings."

    if isinstance(update, CallbackQuery):
        await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data == "my_meetings")
async def my_meetings(callback: CallbackQuery, user: dict, auth_token: str) -> None:
    """Show user's meetings."""
    if not user or not auth_token:
        await callback.answer("Authentication required", show_alert=True)
        return

    meetings = await meeting_client.get_user_meetings(user["id"], limit=20)

    builder = InlineKeyboardBuilder()
    builder.add(create_inline_button("← Back", callback_data="meetings_menu"))

    text = format_meeting_list(meetings) if meetings else "📭 You have no meetings scheduled."

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "schedule_meeting")
async def start_schedule_meeting(callback: CallbackQuery, state: FSMContext) -> None:
    """Start scheduling a meeting."""
    if callback.message is None:
        return

    await callback.message.edit_text(
        "📅 *Schedule Meeting*\n\n"
        "Please provide the meeting details:\n\n"
        "1. Meeting title\n"
        "2. Description (optional)\n"
        "3. Date and time (e.g., 2024-12-31 14:00)\n"
        "4. Duration in minutes (default: 60)\n\n"
        "Please enter the meeting title:",
        parse_mode="Markdown",
    )
    await state.set_state(MeetingStates.waiting_for_title)
    await callback.answer()


@router.message(MeetingStates.waiting_for_title)
async def process_meeting_title(message: Message, state: FSMContext) -> None:
    """Process meeting title."""
    title = message.text.strip()

    if len(title) < 3:
        await message.answer("❌ Title must be at least 3 characters long.")
        return

    await state.update_data(title=title)
    await message.answer(
        "✅ Great! Now please provide a brief description of the meeting (or type 'skip'):",
    )
    await state.set_state(MeetingStates.waiting_for_description)


@router.message(MeetingStates.waiting_for_description)
async def process_meeting_description(message: Message, state: FSMContext) -> None:
    """Process meeting description."""
    description = message.text.strip()

    if description.lower() == "skip":
        description = ""

    await state.update_data(description=description)
    await message.answer(
        "✅ Now please provide the date and time in format YYYY-MM-DD HH:MM (e.g., 2024-12-31 14:00):",
    )
    await state.set_state(MeetingStates.waiting_for_datetime)


@router.message(MeetingStates.waiting_for_datetime)
async def process_meeting_datetime(message: Message, state: FSMContext) -> None:
    """Process meeting date and time."""
    datetime_str = message.text.strip()

    try:
        # Parse datetime
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        await state.update_data(scheduled_at=dt.isoformat(), datetime_str=datetime_str)
        await message.answer(
            "✅ Finally, please provide the duration in minutes (or type '60' for default):",
        )
        await state.set_state(MeetingStates.waiting_for_duration)
    except ValueError:
        await message.answer(
            "❌ Invalid format. Please use YYYY-MM-DD HH:MM (e.g., 2024-12-31 14:00):",
        )


@router.message(MeetingStates.waiting_for_duration)
async def process_meeting_duration(message: Message, state: FSMContext, user: dict, auth_token: str) -> None:
    """Process meeting duration."""
    duration_str = message.text.strip()

    try:
        duration = int(duration_str)
        if duration < 15 or duration > 480:
            await message.answer("❌ Duration must be between 15 and 480 minutes.")
            return
    except ValueError:
        duration = 60  # Default

    # Get data from state
    data = await state.get_data()
    title = data.get("title")
    description = data.get("description", "")
    scheduled_at = data.get("scheduled_at")
    datetime_str = data.get("datetime_str", "N/A")
    participant_ids = [user["id"]]  # Just the user for now

    # Create meeting
    meeting = await meeting_client.create_meeting(
        user_id=user["id"],
        title=title,
        description=description,
        participant_ids=participant_ids,
        scheduled_at=scheduled_at,
        duration_minutes=duration,
        meeting_type="onboarding",
    )

    if meeting:
        await message.answer(
            f"✅ Meeting scheduled successfully!\n\n"
            f"*Title:* {title}\n"
            f"*Date:* {datetime_str}\n"
            f"*Duration:* {duration} minutes\n\n"
            f"You will receive reminders before the meeting.",
            parse_mode="Markdown",
        )
    else:
        await message.answer("❌ Failed to schedule meeting. Please try again.")

    await state.clear()


@router.callback_query(F.data.startswith("meeting_"))
async def meeting_details(callback: CallbackQuery, user: dict, auth_token: str) -> None:
    """Show meeting details."""
    if not auth_token or not user:
        await callback.answer("Authentication required", show_alert=True)
        return

    meeting_id = int(callback.data.split("_")[1])

    # Fetch meeting details from service
    meetings = await meeting_client.get_user_meetings(user["id"], limit=100)
    meeting_detail = None
    for meeting in meetings:
        if meeting.get("id") == meeting_id:
            meeting_detail = meeting
            break

    if not meeting_detail:
        await callback.answer("Meeting not found", show_alert=True)
        return

    text = (
        f"📅 *{meeting_detail.get('title', 'Untitled Meeting')}*\n\n"
        f"*Date:* {meeting_detail.get('scheduled_at', 'N/A')}\n"
        f"*Status:* {meeting_detail.get('status', 'N/A')}\n\n"
        f"*Description:*\n{meeting_detail.get('description', 'No description')}"
    )

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("✅ Confirm", callback_data=f"confirm_meeting_{meeting_id}", style=ButtonStyle.SUCCESS),
        create_inline_button("❌ Cancel", callback_data=f"cancel_meeting_{meeting_id}", style=ButtonStyle.DANGER),
        create_inline_button("← Back", callback_data="my_meetings"),
    )
    builder.adjust(2, 1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_meeting_"))
async def confirm_meeting(callback: CallbackQuery, user: dict, auth_token: str) -> None:
    """Confirm meeting attendance."""
    if not user or not auth_token:
        await callback.answer("Authentication required", show_alert=True)
        return

    meeting_id = int(callback.data.split("_")[2])

    result = await meeting_client.confirm_meeting(meeting_id, user["id"])

    if result:
        await callback.answer("✅ Meeting confirmed!")
        await callback.message.edit_text(
            "✅ Meeting confirmed!\n\nYou will receive a reminder before the meeting.",
        )
    else:
        await callback.answer("❌ Failed to confirm meeting")


@router.callback_query(F.data.startswith("cancel_meeting_"))
async def cancel_meeting(callback: CallbackQuery, user: dict, auth_token: str) -> None:
    """Cancel meeting."""
    if not user or not auth_token:
        await callback.answer("Authentication required", show_alert=True)
        return

    meeting_id = int(callback.data.split("_")[2])

    result = await meeting_client.cancel_meeting(meeting_id, user["id"], "Cancelled via Telegram")

    if result:
        await callback.answer("✅ Meeting cancelled")
        await callback.message.edit_text(
            "✅ Meeting cancelled.\n\nIf you need to reschedule, please use the schedule meeting option.",
        )
    else:
        await callback.answer("❌ Failed to cancel meeting")
