"""Checklist and task management handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.checklist import (
    get_checklists_keyboard,
    get_task_detail_keyboard,
    get_tasks_keyboard,
)
from telegram_bot.keyboards.checklist_detail import (
    get_attach_task_keyboard,
    get_no_checklists_keyboard,
    get_no_tasks_keyboard,
    get_task_completed_keyboard,
    get_task_info_keyboard,
)
from telegram_bot.services.checklists_client import checklists_client
from telegram_bot.states.auth_states import SearchStates
from telegram_bot.utils.formatters import (
    format_checklist_progress,
    format_task_detail,
    format_task_list,
)

router = Router()

MAX_DISPLAYED_CHECKLISTS = 5
CALLBACK_DATA_MIN_PARTS = 2


@router.message(Command("tasks"))
@router.message(F.text == "\U0001f4cb My Tasks")
@router.message(F.text == "My Tasks")
@router.callback_query(F.data == "my_tasks")
async def show_checklists(
    callback: Message | CallbackQuery,
    auth_token: str,
    user: dict,
    *,
    locale: str = "en",
) -> None:
    """Show user's checklists."""
    if not auth_token or not user:
        await _respond_with_auth_error(callback, locale=locale)
        return

    checklists = await checklists_client.get_user_checklists(user["id"], auth_token)

    if isinstance(callback, CallbackQuery):
        msg = callback.message
        await callback.answer()
    else:
        msg = callback

    if not checklists:
        text = t("checklists.no_checklists", locale=locale)
        if isinstance(callback, CallbackQuery) and isinstance(msg, Message):
            await msg.edit_text(
                text, reply_markup=get_no_checklists_keyboard(locale=locale).as_markup()
            )
        else:
            await msg.answer(text)
        return

    text = f"*\U0001f4cb {t('checklists.title', locale=locale)}*\n\n"
    for checklist in checklists[:MAX_DISPLAYED_CHECKLISTS]:
        text += format_checklist_progress(checklist, locale=locale)

    if len(checklists) > MAX_DISPLAYED_CHECKLISTS:
        text += f"\n... and {len(checklists) - MAX_DISPLAYED_CHECKLISTS} more"

    if isinstance(callback, CallbackQuery) and isinstance(msg, Message):
        await msg.edit_text(
            text,
            reply_markup=get_checklists_keyboard(checklists),
            parse_mode="Markdown",
        )
    else:
        await msg.answer(
            text,
            reply_markup=get_checklists_keyboard(checklists),
            parse_mode="Markdown",
        )


@router.callback_query(F.data.startswith("checklist_"))
async def show_checklist_tasks(
    callback: CallbackQuery, auth_token: str, *, locale: str = "en"
) -> None:
    """Show tasks for a specific checklist."""
    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    checklist_id = int(callback.data.split("_")[1])

    tasks = await checklists_client.get_checklist_tasks(checklist_id, auth_token)

    if not tasks:
        if callback.message:
            await callback.message.edit_text(
                t("checklists.no_tasks", locale=locale),
                reply_markup=get_no_tasks_keyboard(locale=locale).as_markup(),
            )
        await callback.answer()
        return

    text = format_task_list(tasks, locale=locale)

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_tasks_keyboard(tasks, checklist_id),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(
    F.data.startswith("task_")
    & ~F.data.startswith("task_info_")
    & ~F.data.startswith("start_task_")
    & ~F.data.startswith("attach_task_")
)
async def show_task_detail(
    callback: CallbackQuery, auth_token: str, *, locale: str = "en"
) -> None:
    """Show task details."""
    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    task_id = int(callback.data.split("_")[1])
    checklist_id = (
        int(callback.data.split("_")[2])
        if len(callback.data.split("_")) > CALLBACK_DATA_MIN_PARTS
        else None
    )

    tasks = await checklists_client.get_assigned_tasks(auth_token)
    task_detail = None
    for task in tasks:
        if task.get("id") == task_id:
            task_detail = task
            break

    if not task_detail and checklist_id:
        tasks = await checklists_client.get_checklist_tasks(checklist_id, auth_token)
        for task in tasks:
            if task.get("id") == task_id:
                task_detail = task
                break

    if not task_detail:
        await callback.answer(
            t("checklists.task_not_found", locale=locale), show_alert=True
        )
        return

    text = format_task_detail(task_detail, locale=locale)

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_task_detail_keyboard(task_id, checklist_id),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("start_task_"))
async def start_task(
    callback: CallbackQuery, auth_token: str, *, locale: str = "en"
) -> None:
    """Start working on a task."""
    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    task_id = int(callback.data.split("_")[2])

    result = await checklists_client.start_task(task_id, auth_token)

    if result:
        await callback.answer(t("common.success", locale=locale))
        if callback.message:
            await callback.message.edit_reply_markup(
                reply_markup=get_task_detail_keyboard(task_id)
            )
    else:
        await callback.answer(
            t("checklists.task_start_failed", locale=locale), show_alert=True
        )


@router.callback_query(F.data.startswith("attach_task_"))
async def attach_task(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "en"
) -> None:
    """Handle attach file to task."""
    if callback.message is None:
        return

    task_id = int(callback.data.split("_")[2])
    await state.update_data(attach_task_id=task_id)
    await state.set_state(SearchStates.waiting_for_query)

    await callback.message.edit_text(
        f"\U0001f4ce *Attach file to task #{task_id}*\n\n"
        f"File attachment is handled through the Documents section. "
        f"Please use the Documents menu to upload files.",
        reply_markup=get_attach_task_keyboard(task_id, locale=locale).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_info_"))
async def task_info(
    callback: CallbackQuery, auth_token: str, *, locale: str = "en"
) -> None:
    """Show detailed task information."""
    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    task_id = int(callback.data.split("_")[2])

    task_detail = await checklists_client.get_task_details(task_id, auth_token)

    if not task_detail:
        await callback.answer(
            t("checklists.task_not_found", locale=locale), show_alert=True
        )
        return

    text = format_task_detail(task_detail, locale=locale)

    # Add additional info
    dependencies = task_detail.get("depends_on", [])
    if dependencies:
        text += f"\n*Dependencies:* {len(dependencies)} task(s)\n"

    assignee = task_detail.get("assignee")
    if assignee:
        text += f"*Assigned to:* {assignee}\n"

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_task_info_keyboard(task_id, locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("complete_task_"))
async def complete_task(
    callback: CallbackQuery, auth_token: str, user: dict, *, locale: str = "en"
) -> None:
    """Mark task as completed."""
    if not auth_token or not user:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    task_id = int(callback.data.split("_")[2])

    result = await checklists_client.complete_task(
        task_id, auth_token, "Completed via Telegram Bot"
    )

    if result:
        await callback.answer(t("checklists.task_completed", locale=locale))

        if callback.message:
            await callback.message.edit_reply_markup(
                reply_markup=get_task_completed_keyboard(
                    task_id, locale=locale
                ).as_markup()
            )
    else:
        await callback.answer(t("checklists.task_complete_failed", locale=locale))


async def _respond_with_auth_error(
    update: Message | CallbackQuery, *, locale: str = "en"
) -> None:
    """Send authentication error response."""
    text = t("common.auth_required", locale=locale)

    if isinstance(update, CallbackQuery):
        await update.answer(text, show_alert=True)
    else:
        await update.answer(text)
