"""Checklist and task management handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.checklist_kb import (
    get_checklists_keyboard,
    get_task_detail_keyboard,
    get_tasks_keyboard,
)
from telegram_bot.keyboards.utils import create_inline_button
from telegram_bot.services.checklists_client import checklists_client
from telegram_bot.utils.formatters import (
    format_checklist_progress,
    format_task_detail,
    format_task_list,
)

router = Router()


@router.message(Command("tasks"))
@router.message(F.text == "📋 My Tasks")
@router.message(F.text == "My Tasks")
@router.callback_query(F.data == "my_tasks")
async def show_checklists(callback: Message | CallbackQuery, auth_token: str, user: dict) -> None:
    """Show user's checklists."""
    if not auth_token or not user:
        await _respond_with_auth_error(callback)
        return

    checklists = await checklists_client.get_user_checklists(user["id"], auth_token)

    if isinstance(callback, CallbackQuery):
        message = callback.message
        await callback.answer()
    else:
        message = callback

    if not checklists:
        await message.answer(
            "📭 You don't have any active checklists.\n\n"
            "Checklists are created automatically when you start onboarding."
        )
        return

    text = "📋 *Your Checklists*\n\n"
    for checklist in checklists[:5]:  # Show first 5
        text += format_checklist_progress(checklist)

    if len(checklists) > 5:
        text += f"\n... and {len(checklists) - 5} more"

    if isinstance(callback, CallbackQuery) and isinstance(message, Message):
        await message.edit_text(text, reply_markup=get_checklists_keyboard(checklists), parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=get_checklists_keyboard(checklists), parse_mode="Markdown")


@router.callback_query(F.data.startswith("checklist_"))
async def show_checklist_tasks(callback: CallbackQuery, auth_token: str) -> None:
    """Show tasks for a specific checklist."""
    if not auth_token:
        await callback.answer("Authentication required")
        return

    checklist_id = int(callback.data.split("_")[1])

    tasks = await checklists_client.get_checklist_tasks(checklist_id, auth_token)

    if not tasks:
        await callback.message.edit_text(
            "📭 No tasks found for this checklist.",
            reply_markup=InlineKeyboardBuilder()
            .add(create_inline_button("← Back", callback_data="my_tasks"))
            .as_markup(),
        )
        await callback.answer()
        return

    text = format_task_list(tasks)

    await callback.message.edit_text(text, reply_markup=get_tasks_keyboard(tasks, checklist_id), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("task_"))
async def show_task_detail(callback: CallbackQuery, auth_token: str) -> None:
    """Show task details."""
    if not auth_token:
        await callback.answer("Authentication required")
        return

    task_id = int(callback.data.split("_")[1])
    checklist_id = int(callback.data.split("_")[2]) if len(callback.data.split("_")) > 2 else None

    # Fetch task details from service
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
        await callback.answer("Task not found", show_alert=True)
        return

    text = format_task_detail(task_detail)

    await callback.message.edit_text(
        text, reply_markup=get_task_detail_keyboard(task_id, checklist_id), parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("complete_task_"))
async def complete_task(callback: CallbackQuery, auth_token: str, user: dict) -> None:
    """Mark task as completed."""
    if not auth_token or not user:
        await callback.answer("Authentication required")
        return

    task_id = int(callback.data.split("_")[2])

    result = await checklists_client.complete_task(task_id, auth_token, "Completed via Telegram Bot")

    if result:
        await callback.answer("✅ Task marked as completed!")

        # Update message
        builder = InlineKeyboardBuilder()
        builder.add(create_inline_button("✅ Completed", callback_data=f"task_{task_id}", style=ButtonStyle.SUCCESS))
        builder.add(create_inline_button("← Back to Tasks", callback_data="my_tasks"))

        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    else:
        await callback.answer("❌ Failed to complete task")


async def _respond_with_auth_error(update: Message | CallbackQuery) -> None:
    """Send authentication error response."""
    text = "🔒 Authentication required\n\nUse /start to register first."

    if isinstance(update, CallbackQuery):
        await update.answer(text, show_alert=True)
    else:
        await update.answer(text)
