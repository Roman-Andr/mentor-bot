"""Checklist-related keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_checklists_keyboard(checklists: list[dict], *, locale: str = "en") -> InlineKeyboardMarkup:
    """Create keyboard for checklist selection."""
    builder = InlineKeyboardBuilder()

    for checklist in checklists[:5]:
        title = checklist.get("name", f"Checklist #{checklist['id']}")
        status = checklist.get("status", "unknown")

        emoji = "\u2705" if status == "completed" else "\U0001f4cb" if status == "in_progress" else "\u23f3"

        builder.add(
            create_inline_button(
                text=f"{emoji} {title}",
                callback_data=f"checklist_{checklist['id']}",
                style=ButtonStyle.PRIMARY,
            )
        )

    builder.add(
        create_inline_button(f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_tasks_keyboard(
    tasks: list[dict], checklist_id: int | None = None, *, locale: str = "en"
) -> InlineKeyboardMarkup:
    """Create keyboard for task selection with task info in buttons."""
    builder = InlineKeyboardBuilder()

    for task in tasks[:10]:
        title = task.get("title", f"Task #{task['id']}")
        status = task.get("status", "PENDING").upper()
        due_date = task.get("due_date")

        if status == "COMPLETED":
            emoji = "✅"
        elif status == "IN_PROGRESS":
            emoji = "🔄"
        elif status == "BLOCKED":
            emoji = "🚫"
        else:
            emoji = "📝"

        # Build button text with task info
        button_text = f"{emoji} {title}"
        if due_date:
            try:
                from datetime import datetime

                due_dt = datetime.fromisoformat(due_date)
                due_str = due_dt.strftime("%d.%m")
                button_text += f" | 📅 {due_str}"
            except ValueError:
                pass

        callback_data = f"task_{task['id']}"
        if checklist_id is not None:
            callback_data += f"_{checklist_id}"

        builder.add(
            create_inline_button(
                text=button_text,
                callback_data=callback_data,
                style=ButtonStyle.PRIMARY,
            )
        )

    builder.add(
        create_inline_button(
            f"← {t('checklists.btn_back_checklists', locale=locale)}",
            callback_data="my_tasks",
        ),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_task_detail_keyboard(
    task_id: int,
    checklist_id: int | None = None,
    task_status: str | None = None,
    attachment_count: int = 0,
    *,
    locale: str = "en",
) -> InlineKeyboardMarkup:
    """Create keyboard for task detail actions."""
    builder = InlineKeyboardBuilder()

    status = task_status.upper() if task_status else "PENDING"

    if status == "COMPLETED":
        # For completed tasks - show "Completed" status button (no action) and back only
        builder.add(
            create_inline_button(
                f"\u2705 {t('tasks.status_completed', locale=locale)}",
                callback_data="noop",  # No action, just status indicator
                style=ButtonStyle.SUCCESS,
            ),
        )
    elif status == "IN_PROGRESS":
        # For in-progress tasks - show complete, attach, and back
        builder.add(
            create_inline_button(
                f"\u2705 {t('checklists.btn_complete', locale=locale)}",
                callback_data=f"complete_task_{task_id}_{checklist_id or 0}",
                style=ButtonStyle.SUCCESS,
            ),
            create_inline_button(
                f"\U0001f4ce {t('checklists.btn_attach', locale=locale)}",
                callback_data=f"attach_task_{task_id}_{checklist_id or 0}",
                style=ButtonStyle.PRIMARY,
            ),
        )
    else:
        # For pending/blocked tasks - show start, attach, and back
        builder.add(
            create_inline_button(
                f"\U0001f504 {t('checklists.btn_start', locale=locale)}",
                callback_data=f"start_task_{task_id}_{checklist_id or 0}",
                style=ButtonStyle.PRIMARY,
            ),
            create_inline_button(
                f"\U0001f4ce {t('checklists.btn_attach', locale=locale)}",
                callback_data=f"attach_task_{task_id}_{checklist_id or 0}",
                style=ButtonStyle.PRIMARY,
            ),
        )

    # Show "View files" button if there are attachments
    if attachment_count > 0:
        builder.add(
            create_inline_button(
                f"\U0001f4c1 {t('tasks.view_files', locale=locale)} ({attachment_count})",
                callback_data=f"task_files_{task_id}_{checklist_id or 0}",
                style=ButtonStyle.PRIMARY,
            ),
        )

    back_callback = f"checklist_{checklist_id}" if checklist_id is not None else "my_tasks"
    builder.add(
        create_inline_button(
            f"\u2190 {t('checklists.btn_back', locale=locale)}",
            callback_data=back_callback,
        ),
    )

    builder.adjust(1)
    return builder.as_markup()
