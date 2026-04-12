"""Checklist and task management handlers."""

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

logger = logging.getLogger(__name__)

from telegram_bot.i18n import t
from telegram_bot.keyboards.checklist import (
    get_checklists_keyboard,
    get_task_detail_keyboard,
    get_tasks_keyboard,
)
from telegram_bot.keyboards.checklist_detail import (
    get_attach_task_keyboard,
    get_back_to_task_keyboard,
    get_no_checklists_keyboard,
    get_no_tasks_keyboard,
    get_skip_description_keyboard,
    get_task_attachments_keyboard,
    get_task_completed_keyboard,
    get_task_info_keyboard,
)
from telegram_bot.services.checklists_client import checklists_client
from telegram_bot.states.checklist_states import TaskAttachmentStates
from telegram_bot.utils.formatters import (
    format_checklist_progress,
    format_task_detail,
)

router = Router()

MAX_DISPLAYED_CHECKLISTS = 5
CALLBACK_DATA_MIN_PARTS = 2
MAX_FILE_SIZE_MB = 10


@router.message(Command("tasks"))
@router.message(F.text == "\U0001f4cb My Tasks")
@router.message(F.text == "My Tasks")
@router.message(
    F.text == "\U0001f4cb \u041c\u043e\u0438 \u0437\u0430\u0434\u0430\u0447\u0438"
)
@router.message(F.text == "\u041c\u043e\u0438 \u0437\u0430\u0434\u0430\u0447\u0438")
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
            reply_markup=get_checklists_keyboard(checklists, locale=locale),
            parse_mode="Markdown",
        )
    else:
        await msg.answer(
            text,
            reply_markup=get_checklists_keyboard(checklists, locale=locale),
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

    # Get checklist details for the title
    checklists = await checklists_client.get_user_checklists(
        callback.from_user.id, auth_token
    )
    current_checklist = None
    for cl in checklists:
        if cl.get("id") == checklist_id:
            current_checklist = cl
            break

    tasks = await checklists_client.get_checklist_tasks(checklist_id, auth_token)

    if not tasks:
        if callback.message:
            await callback.message.edit_text(
                t("checklists.no_tasks", locale=locale),
                reply_markup=get_no_tasks_keyboard(locale=locale).as_markup(),
            )
        await callback.answer()
        return

    # Simple text with checklist name and progress only
    if current_checklist:
        checklist_name = current_checklist.get("name", "Checklist")
        progress = current_checklist.get("progress_percentage", 0)
        completed = current_checklist.get("completed_tasks", 0)
        total = current_checklist.get("total_tasks", 0)
        text = f"*📋 {checklist_name}*\n📊 {progress}% • {t('checklists.tasks_completed', locale=locale, completed=completed, total=total)}"
    else:
        text = f"*📋 {t('checklists.tasks_title', locale=locale)}*"

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_tasks_keyboard(tasks, checklist_id, locale=locale),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(
    F.data.startswith("task_"),
    ~F.data.startswith("task_info_")
    & ~F.data.startswith("start_task_")
    & ~F.data.startswith("attach_task_")
    & ~F.data.startswith("task_files_")
    & ~F.data.startswith("download_task_file_"),
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

    # Invalidate cache to get fresh task status
    await checklists_client.invalidate_task_cache(auth_token, checklist_id)

    tasks = await checklists_client.get_assigned_tasks(auth_token)
    task_detail = None
    for task in tasks:
        if task.get("id") == task_id:
            task_detail = task
            break

    if not task_detail and checklist_id is not None:
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
    task_status = task_detail.get("status")

    # Get attachments count
    attachments = await checklists_client.get_task_attachments(task_id, auth_token)
    attachment_count = len(attachments)

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_task_detail_keyboard(
                task_id, checklist_id, task_status, attachment_count, locale=locale
            ),
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

    parts = callback.data.split("_")
    task_id = int(parts[2])
    checklist_id = int(parts[3]) if len(parts) > 3 and parts[3] != "0" else None

    # Check current task status
    tasks = await checklists_client.get_assigned_tasks(auth_token)
    task_status = None
    for task in tasks:
        if task.get("id") == task_id:
            task_status = task.get("status")
            break

    if task_status == "COMPLETED":
        await callback.answer(
            t("tasks.already_completed", locale=locale), show_alert=True
        )
        return

    if task_status == "IN_PROGRESS":
        # Task already started, just update keyboard
        await callback.answer(t("tasks.already_started", locale=locale))
        if callback.message:
            await callback.message.edit_reply_markup(
                reply_markup=get_task_detail_keyboard(
                    task_id, checklist_id, "in_progress", locale=locale
                )
            )
        return

    result = await checklists_client.start_task(task_id, auth_token)

    if result:
        # Invalidate task cache so fresh data is shown on next view
        await checklists_client.invalidate_task_cache(auth_token, checklist_id)
        await callback.answer(t("common.success", locale=locale))
        if callback.message:
            await callback.message.edit_reply_markup(
                reply_markup=get_task_detail_keyboard(
                    task_id, checklist_id, "in_progress", locale=locale
                )
            )
    else:
        await callback.answer(
            t("checklists.task_start_failed", locale=locale), show_alert=True
        )


@router.callback_query(F.data.startswith("attach_task_"))
async def attach_task(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "en"
) -> None:
    """Start file attachment process to task."""
    if callback.message is None:
        return

    parts = callback.data.split("_")
    task_id = int(parts[2])
    checklist_id = int(parts[3]) if len(parts) > 3 and parts[3] != "0" else None

    # Save task info to state
    await state.update_data(
        attach_task_id=task_id,
        attach_checklist_id=checklist_id,
    )
    await state.set_state(TaskAttachmentStates.waiting_for_file)

    await callback.message.edit_text(
        f"\U0001f4ce *{t('tasks.attach_file_title', locale=locale)}*\n\n"
        f"{t('tasks.attach_file_prompt', locale=locale)}\n\n"
        f"_{t('tasks.attach_file_limits', locale=locale, max_size=MAX_FILE_SIZE_MB)}_",
        reply_markup=get_attach_task_keyboard(
            task_id, checklist_id, locale=locale
        ).as_markup(),
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

    parts = callback.data.split("_")
    task_id = int(parts[2])
    checklist_id = int(parts[3]) if len(parts) > 3 and parts[3] != "0" else None

    task_detail = await checklists_client.get_task_details(
        task_id, auth_token, checklist_id
    )

    if not task_detail:
        await callback.answer(
            t("checklists.task_not_found", locale=locale), show_alert=True
        )
        return

    text = format_task_detail(task_detail, locale=locale)
    task_status = task_detail.get("status")
    checklist_id = task_detail.get("checklist_id")

    # Add additional info
    dependencies = task_detail.get("depends_on", [])
    if dependencies:
        text += f"\n*{t('tasks.depends_on', locale=locale, count=len(dependencies))}*\n"

    assignee = task_detail.get("assignee")
    if assignee:
        assign_label = t("tasks.assigned_to", locale=locale)
        text += f"\n*{assign_label}:* {assignee}\n"

    # Get attachments count for showing files button
    attachments = await checklists_client.get_task_attachments(task_id, auth_token)
    attachment_count = len(attachments)

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_task_info_keyboard(
                task_id, checklist_id, task_status, attachment_count, locale=locale
            ).as_markup(),
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

    parts = callback.data.split("_")
    task_id = int(parts[2])
    checklist_id = int(parts[3]) if len(parts) > 3 and parts[3] != "0" else None

    result = await checklists_client.complete_task(
        task_id, auth_token, "Completed via Telegram Bot"
    )

    if result:
        # Invalidate task cache so checklist progress is updated
        await checklists_client.invalidate_task_cache(auth_token, checklist_id)
        await callback.answer(t("checklists.task_completed", locale=locale))

        if callback.message:
            # Update the task detail text to show completed status
            task_detail = result
            text = format_task_detail(task_detail, locale=locale)

            # Get attachments count for completed task
            attachments = await checklists_client.get_task_attachments(
                task_id, auth_token
            )
            attachment_count = len(attachments)

            await callback.message.edit_text(
                text,
                reply_markup=get_task_completed_keyboard(
                    task_id, checklist_id, attachment_count, locale=locale
                ).as_markup(),
                parse_mode="Markdown",
            )
    else:
        await callback.answer(t("checklists.task_complete_failed", locale=locale))


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery, *, locale: str = "en") -> None:
    """No-op callback handler for disabled buttons."""
    await callback.answer()


@router.message(TaskAttachmentStates.waiting_for_file, F.document)
async def receive_task_file(
    message: Message, state: FSMContext, auth_token: str, *, locale: str = "en"
) -> None:
    """Receive file attachment for task."""
    if not auth_token:
        await message.answer(t("common.auth_required", locale=locale))
        await state.clear()
        return

    if not message.document:
        await message.answer(t("tasks.no_file_received", locale=locale))
        return

    # Check file size
    file_size = message.document.file_size or 0
    max_size = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        await message.answer(
            t("tasks.file_too_large", locale=locale, max_size=MAX_FILE_SIZE_MB)
        )
        return

    # Save file info to state
    await state.update_data(
        attach_file_id=message.document.file_id,
        attach_filename=message.document.file_name,
    )
    await state.set_state(TaskAttachmentStates.waiting_for_description)

    # Ask for optional description
    await message.answer(
        f"\U0001f4ce *{t('tasks.file_received', locale=locale)}:* `{message.document.file_name}`\n\n"
        f"{t('tasks.ask_description', locale=locale)}",
        parse_mode="Markdown",
        reply_markup=get_skip_description_keyboard(locale=locale).as_markup(),
    )


@router.message(TaskAttachmentStates.waiting_for_file, F.photo)
async def receive_task_photo(
    message: Message, state: FSMContext, auth_token: str, *, locale: str = "en"
) -> None:
    """Receive photo attachment for task."""
    if not auth_token:
        await message.answer(t("common.auth_required", locale=locale))
        await state.clear()
        return

    if not message.photo:
        await message.answer(t("tasks.no_file_received", locale=locale))
        return

    # Get largest photo (best quality)
    photo = message.photo[-1]

    # Check file size
    file_size = photo.file_size or 0
    max_size = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        await message.answer(
            t("tasks.file_too_large", locale=locale, max_size=MAX_FILE_SIZE_MB)
        )
        return

    # Save file info to state - generate filename for photo
    await state.update_data(
        attach_file_id=photo.file_id,
        attach_filename="photo.jpg",
    )
    await state.set_state(TaskAttachmentStates.waiting_for_description)

    # Ask for optional description
    await message.answer(
        f"\U0001f4ce *{t('tasks.photo_received', locale=locale)}*\n\n"
        f"{t('tasks.ask_description', locale=locale)}",
        parse_mode="Markdown",
        reply_markup=get_skip_description_keyboard(locale=locale).as_markup(),
    )


@router.message(TaskAttachmentStates.waiting_for_file)
async def receive_task_file_invalid(
    message: Message, state: FSMContext, *, locale: str = "en"
) -> None:
    """Handle invalid input when waiting for file."""
    await message.answer(t("tasks.send_file_only", locale=locale))


@router.message(TaskAttachmentStates.waiting_for_description)
async def receive_task_description(
    message: Message, state: FSMContext, auth_token: str, *, locale: str = "en"
) -> None:
    """Receive description and upload file to task."""
    if not auth_token:
        await message.answer(t("common.auth_required", locale=locale))
        await state.clear()
        return

    data = await state.get_data()
    task_id = data.get("attach_task_id")
    checklist_id = data.get("attach_checklist_id")
    file_id = data.get("attach_file_id")
    filename = data.get("attach_filename")

    if not task_id or not file_id:
        await message.answer(t("tasks.attachment_error", locale=locale))
        await state.clear()
        return

    # Get file from Telegram
    try:
        file_info = await message.bot.get_file(file_id)
        file_content = await message.bot.download_file(file_info.file_path)
    except Exception:
        await message.answer(t("tasks.download_failed", locale=locale))
        await state.clear()
        return

    # Upload to service
    description = message.text if message.text else None
    result = await checklists_client.upload_task_attachment(
        task_id=task_id,
        file_content=file_content,  # download_file returns bytes directly
        filename=filename or "attachment",
        auth_token=auth_token,
        description=description,
    )

    if result:
        await message.answer(
            f"\U0001f4ce {t('tasks.attachment_success', locale=locale)}\n\n"
            f"{t('tasks.back_to_task', locale=locale)}",
            reply_markup=get_back_to_task_keyboard(
                task_id, checklist_id, locale=locale
            ).as_markup(),
        )
    else:
        await message.answer(t("tasks.attachment_failed", locale=locale))

    await state.clear()


@router.callback_query(F.data == "skip_description")
async def skip_description(
    callback: CallbackQuery, state: FSMContext, auth_token: str, *, locale: str = "en"
) -> None:
    """Skip description and upload file directly."""
    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        await state.clear()
        return

    data = await state.get_data()
    task_id = data.get("attach_task_id")
    checklist_id = data.get("attach_checklist_id")
    file_id = data.get("attach_file_id")
    filename = data.get("attach_filename")

    if not task_id or not file_id:
        await callback.answer(t("tasks.attachment_error", locale=locale))
        await state.clear()
        return

    # Get file from Telegram
    try:
        file_info = await callback.bot.get_file(file_id)
        file_content = await callback.bot.download_file(file_info.file_path)
    except Exception:
        await callback.answer(
            t("tasks.download_failed", locale=locale), show_alert=True
        )
        await state.clear()
        return

    # Upload to service
    result = await checklists_client.upload_task_attachment(
        task_id=task_id,
        file_content=file_content,  # download_file returns bytes directly
        filename=filename or "attachment",
        auth_token=auth_token,
        description=None,
    )

    if result:
        if callback.message:
            await callback.message.edit_text(
                f"\U0001f4ce {t('tasks.attachment_success', locale=locale)}\n\n"
                f"{t('tasks.back_to_task', locale=locale)}",
                reply_markup=get_back_to_task_keyboard(
                    task_id, checklist_id, locale=locale
                ).as_markup(),
            )
    else:
        await callback.answer(
            t("tasks.attachment_failed", locale=locale), show_alert=True
        )

    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("task_files_"))
async def show_task_attachments(
    callback: CallbackQuery, auth_token: str, *, locale: str = "en"
) -> None:
    """Show list of task attachments."""
    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    parts = callback.data.split("_")
    task_id = int(parts[2])
    checklist_id = int(parts[3]) if len(parts) > 3 and parts[3] != "0" else None

    attachments = await checklists_client.get_task_attachments(task_id, auth_token)

    if not attachments:
        await callback.answer(t("tasks.no_attachments", locale=locale), show_alert=True)
        return

    text = f"\U0001f4c1 *{t('tasks.view_files', locale=locale)}*\n\n"
    text += f"{t('tasks.select_file', locale=locale)}"

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_task_attachments_keyboard(
                attachments, task_id, checklist_id, locale=locale
            ).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("download_task_file_"))
async def download_task_file(
    callback: CallbackQuery, auth_token: str, *, locale: str = "en"
) -> None:
    """Download and send task attachment."""
    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    parts = callback.data.split("_")
    task_id = int(parts[3])
    attachment_id = int(parts[4])
    checklist_id = int(parts[5]) if len(parts) > 5 and parts[5] != "0" else None

    # Get attachments list to find filename
    attachments = await checklists_client.get_task_attachments(task_id, auth_token)
    attachment = next((a for a in attachments if a.get("id") == attachment_id), None)

    if not attachment:
        await callback.answer(
            t("tasks.attachment_error", locale=locale), show_alert=True
        )
        return

    await callback.answer(t("common.loading", locale=locale))

    # Download file
    try:
        file_data = await checklists_client.download_task_attachment(
            task_id, attachment.get("filename", "file"), auth_token
        )
        if file_data:
            filename = attachment.get("filename", "file")
            # Wrap bytes in BufferedInputFile for aiogram
            input_file = BufferedInputFile(file_data, filename=filename)
            await callback.message.answer_document(
                document=input_file,
                caption=f"\U0001f4ce {filename}",
            )
        else:
            await callback.answer(
                t("tasks.download_failed", locale=locale), show_alert=True
            )
    except Exception as e:
        logger.exception("Failed to send task attachment")
        await callback.answer(
            t("tasks.download_failed", locale=locale), show_alert=True
        )


async def _respond_with_auth_error(
    update: Message | CallbackQuery, *, locale: str = "en"
) -> None:
    """Send authentication error response."""
    text = t("common.auth_required", locale=locale)

    if isinstance(update, CallbackQuery):
        await update.answer(text, show_alert=True)
    else:
        await update.answer(text)
