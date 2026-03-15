"""Checklist-related keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button


def get_checklists_keyboard(checklists: list[dict]) -> InlineKeyboardMarkup:
    """Create keyboard for checklist selection."""
    builder = InlineKeyboardBuilder()

    for checklist in checklists[:5]:
        title = checklist.get("name", f"Checklist #{checklist['id']}")
        status = checklist.get("status", "unknown")

        emoji = "✅" if status == "completed" else "📋" if status == "in_progress" else "⏳"

        builder.add(
            create_inline_button(
                text=f"{emoji} {title}", callback_data=f"checklist_{checklist['id']}", style=ButtonStyle.PRIMARY
            )
        )

    builder.add(
        create_inline_button("📊 Progress", callback_data="progress", style=ButtonStyle.PRIMARY),
        create_inline_button("← Menu", callback_data="menu"),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_tasks_keyboard(tasks: list[dict], checklist_id: int | None = None) -> InlineKeyboardMarkup:
    """Create keyboard for task selection."""
    builder = InlineKeyboardBuilder()

    for task in tasks[:10]:
        title = task.get("title", f"Task #{task['id']}")
        status = task.get("status", "pending")

        if status == "completed":
            emoji = "✅"
        elif status == "in_progress":
            emoji = "🔄"
        elif status == "blocked":
            emoji = "⛔"
        else:
            emoji = "📝"

        callback_data = f"task_{task['id']}"
        if checklist_id:
            callback_data += f"_{checklist_id}"

        builder.add(
            create_inline_button(text=f"{emoji} {title}", callback_data=callback_data, style=ButtonStyle.PRIMARY)
        )

    builder.add(
        create_inline_button("← Back to Checklists", callback_data="my_tasks"),
        create_inline_button("📊 Overall Progress", callback_data="progress", style=ButtonStyle.PRIMARY),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_task_detail_keyboard(task_id: int, checklist_id: int | None = None) -> InlineKeyboardMarkup:
    """Create keyboard for task detail actions."""
    builder = InlineKeyboardBuilder()

    builder.add(
        create_inline_button("✅ Mark Complete", callback_data=f"complete_task_{task_id}", style=ButtonStyle.SUCCESS),
        create_inline_button("🔄 Start Progress", callback_data=f"start_task_{task_id}", style=ButtonStyle.PRIMARY),
        create_inline_button("📎 Add Attachment", callback_data=f"attach_task_{task_id}", style=ButtonStyle.PRIMARY),
    )

    back_callback = f"checklist_{checklist_id}" if checklist_id else "my_tasks"
    builder.add(
        create_inline_button("ℹ️ More Info", callback_data=f"task_info_{task_id}", style=ButtonStyle.PRIMARY),
        create_inline_button("← Back", callback_data=back_callback),
    )

    builder.adjust(1)
    return builder.as_markup()
