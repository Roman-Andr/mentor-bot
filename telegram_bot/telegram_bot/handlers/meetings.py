"""Meeting management handlers."""

from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.meetings_kb import (
    get_meeting_details_keyboard,
    get_meetings_menu_keyboard,
    get_my_meetings_keyboard,
)
from telegram_bot.services.meeting_client import meeting_client
from telegram_bot.states.meeting_states import MeetingStates
from telegram_bot.utils.formatters import format_meeting_list

router = Router()

MIN_TITLE_LENGTH = 3
MIN_MEETING_DURATION = 15
MAX_MEETING_DURATION = 480


@router.message(Command("meetings"))
@router.message(F.text == "\U0001f4c5 Meetings")
@router.message(F.text == "\U0001f4c5 \u0412\u0441\u0442\u0440\u0435\u0447\u0438")
@router.message(F.text == "\u0412\u0441\u0442\u0440\u0435\u0447\u0438")
@router.callback_query(F.data == "meetings_menu")
async def meetings_menu(
    update: Message | CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Show meetings menu."""
    if isinstance(update, CallbackQuery):
        msg = update.message
        await update.answer()
    else:
        msg = update

    if not user or not auth_token:
        await msg.answer(t("common.auth_required", locale=locale))
        return

    meetings = await meeting_client.get_upcoming_meetings(
        user["id"], auth_token, limit=5
    )

    text = f"*\U0001f4c5 {t('meetings.title', locale=locale)}*\n\n"
    if meetings:
        text += format_meeting_list(meetings, locale=locale)
        text += "\n"
    else:
        text += f"{t('meetings.no_meetings', locale=locale)}\n\n"

    text += t("meetings.use_options", locale=locale)

    keyboard = get_meetings_menu_keyboard(locale=locale)
    if isinstance(update, CallbackQuery):
        await msg.edit_text(
            text, reply_markup=keyboard.as_markup(), parse_mode="Markdown"
        )
    else:
        await msg.answer(text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data == "my_meetings")
async def my_meetings(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Show user's meetings."""
    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    meetings = await meeting_client.get_user_meetings(user["id"], auth_token, limit=20)

    text = (
        format_meeting_list(meetings, locale=locale)
        if meetings
        else t("meetings.no_meetings_list", locale=locale)
    )

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_my_meetings_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "schedule_meeting")
async def start_schedule_meeting(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "en"
) -> None:
    """Start scheduling a meeting."""
    if callback.message is None:
        return

    schedule_title = f"*\U0001f4c5 {t('meetings.schedule_title', locale=locale)}*"
    schedule_desc = t("meetings.schedule_instructions", locale=locale)
    await callback.message.edit_text(
        f"{schedule_title}\n\n{schedule_desc}",
        parse_mode="Markdown",
    )
    await state.set_state(MeetingStates.waiting_for_title)
    await callback.answer()


@router.message(MeetingStates.waiting_for_title)
async def process_meeting_title(
    message: Message, state: FSMContext, *, locale: str = "en"
) -> None:
    """Process meeting title."""
    title = (message.text or "").strip()

    if len(title) < MIN_TITLE_LENGTH:
        await message.answer(
            t("meetings.title_too_short", locale=locale, min=MIN_TITLE_LENGTH)
        )
        return

    await state.update_data(title=title)
    await message.answer(t("meetings.enter_description", locale=locale))
    await state.set_state(MeetingStates.waiting_for_description)


@router.message(MeetingStates.waiting_for_description)
async def process_meeting_description(
    message: Message, state: FSMContext, *, locale: str = "en"
) -> None:
    """Process meeting description."""
    description = (message.text or "").strip()

    if description.lower() in ("skip", "пропустить"):
        description = ""

    await state.update_data(description=description)
    await message.answer(t("meetings.enter_datetime", locale=locale))
    await state.set_state(MeetingStates.waiting_for_datetime)


@router.message(MeetingStates.waiting_for_datetime)
async def process_meeting_datetime(
    message: Message, state: FSMContext, *, locale: str = "en"
) -> None:
    """Process meeting date and time."""
    datetime_str = (message.text or "").strip()

    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
        if dt <= datetime.now(UTC):
            await message.answer(t("meetings.past_datetime", locale=locale))
            return
        await state.update_data(scheduled_at=dt.isoformat(), datetime_str=datetime_str)
        await message.answer(t("meetings.enter_duration", locale=locale))
        await state.set_state(MeetingStates.waiting_for_duration)
    except ValueError:
        await message.answer(t("meetings.invalid_datetime", locale=locale))


@router.message(MeetingStates.waiting_for_duration)
async def process_meeting_duration(
    message: Message,
    state: FSMContext,
    user: dict,
    auth_token: str,
    *,
    locale: str = "en",
) -> None:
    """Process meeting duration."""
    duration_str = (message.text or "").strip()

    try:
        duration = int(duration_str)
        if duration < MIN_MEETING_DURATION or duration > MAX_MEETING_DURATION:
            await message.answer(
                t(
                    "meetings.invalid_duration",
                    locale=locale,
                    min=MIN_MEETING_DURATION,
                    max=MAX_MEETING_DURATION,
                )
            )
            return
    except ValueError:
        duration = 60

    data = await state.get_data()
    title = data.get("title")
    description = data.get("description", "")
    scheduled_at = data.get("scheduled_at")
    datetime_str = data.get("datetime_str", "N/A")
    participant_ids = [user["id"]]

    meeting = await meeting_client.create_meeting(
        user_id=user["id"],
        title=title,
        description=description,
        participant_ids=participant_ids,
        scheduled_at=scheduled_at,
        auth_token=auth_token,
        duration_minutes=duration,
        meeting_type="onboarding",
    )

    if meeting:
        await message.answer(
            t(
                "meetings.scheduled",
                locale=locale,
                title=title,
                datetime=datetime_str,
                duration=duration,
            ),
            parse_mode="Markdown",
        )
    else:
        await message.answer(t("meetings.schedule_failed", locale=locale))

    await state.clear()


@router.callback_query(
    F.data.startswith("meeting_")
    & ~F.data.startswith("confirm_meeting_")
    & ~F.data.startswith("cancel_meeting_")
)
async def meeting_details(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Show meeting details."""
    if not auth_token or not user:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    meeting_id = int(callback.data.split("_")[1])

    meetings = await meeting_client.get_user_meetings(user["id"], auth_token, limit=100)
    meeting_detail = None
    for meeting in meetings:
        if meeting.get("id") == meeting_id:
            meeting_detail = meeting
            break

    if not meeting_detail:
        await callback.answer(t("common.error_generic", locale=locale), show_alert=True)
        return

    text = (
        f"\U0001f4c5 *{meeting_detail.get('title', 'Untitled Meeting')}*\n\n"
        f"*Date:* {meeting_detail.get('scheduled_at', 'N/A')}\n"
        f"*Status:* {meeting_detail.get('status', 'N/A')}\n\n"
        f"*Description:*\n{meeting_detail.get('description', 'No description')}"
    )

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_meeting_details_keyboard(
                meeting_id, locale=locale
            ).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_meeting_"))
async def confirm_meeting(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Confirm meeting attendance."""
    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    meeting_id = int(callback.data.split("_")[2])

    result = await meeting_client.confirm_meeting(meeting_id, user["id"], auth_token)

    if result:
        await callback.answer(t("meetings.confirmed", locale=locale))
        if callback.message:
            await callback.message.edit_text(t("meetings.confirmed", locale=locale))
    else:
        await callback.answer(t("meetings.confirm_failed", locale=locale))


@router.callback_query(F.data.startswith("cancel_meeting_"))
async def cancel_meeting(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Cancel meeting."""
    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    meeting_id = int(callback.data.split("_")[2])

    result = await meeting_client.cancel_meeting(
        meeting_id, user["id"], auth_token, "Cancelled via Telegram"
    )

    if result:
        await callback.answer(t("meetings.cancelled", locale=locale))
        if callback.message:
            await callback.message.edit_text(t("meetings.cancelled", locale=locale))
    else:
        await callback.answer(t("meetings.cancel_failed", locale=locale))
