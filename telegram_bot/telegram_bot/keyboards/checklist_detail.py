"""Checklist detail-specific keyboards (no checklists, no tasks, attach, info, completed)."""

from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_no_checklists_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build keyboard for when user has no checklists."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}",
            callback_data="menu",
        )
    )
    return builder


def get_no_tasks_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build keyboard for when a checklist has no tasks."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="my_tasks",
        )
    )
    return builder


def get_attach_task_keyboard(
    task_id: int, checklist_id: int | None = None, *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build keyboard for attach file to task."""
    builder = InlineKeyboardBuilder()
    back_callback = f"task_{task_id}_{checklist_id or 0}"
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data=back_callback,
        ),
    )
    return builder


def get_task_info_keyboard(
    task_id: int,
    checklist_id: int | None = None,
    task_status: str | None = None,
    attachment_count: int = 0,
    *,
    locale: str = "en",
) -> InlineKeyboardBuilder:
    """Build keyboard for task info view."""
    builder = InlineKeyboardBuilder()

    status = task_status.upper() if task_status else "PENDING"

    if status == "COMPLETED":
        # For completed tasks - show completed status (no action)
        builder.add(
            create_inline_button(
                f"\u2705 {t('tasks.status_completed', locale=locale)}",
                callback_data="noop",  # No action, just status indicator
                style=ButtonStyle.SUCCESS,
            ),
        )
        # Show files button if there are attachments
        if attachment_count > 0:
            builder.add(
                create_inline_button(
                    f"\U0001f4c1 {t('tasks.view_files', locale=locale)} ({attachment_count})",
                    callback_data=f"task_files_{task_id}_{checklist_id or 0}",
                )
            )
    elif status == "IN_PROGRESS":
        # For in-progress tasks - show complete button
        builder.add(
            create_inline_button(
                t("checklists.btn_complete", locale=locale),
                callback_data=f"complete_task_{task_id}_{checklist_id or 0}",
                style=ButtonStyle.SUCCESS,
            ),
        )
    # For pending/blocked tasks - no complete button, only back

    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data=f"checklist_{checklist_id}"
            if checklist_id is not None
            else "my_tasks",
        ),
    )
    builder.adjust(1)
    return builder


def get_task_completed_keyboard(
    task_id: int,
    checklist_id: int | None = None,
    attachment_count: int = 0,
    *,
    locale: str = "en",
) -> InlineKeyboardBuilder:
    """Build keyboard shown after task is completed."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2705 {t('tasks.status_completed', locale=locale)}",
            callback_data="noop",  # No action, just status indicator
            style=ButtonStyle.SUCCESS,
        )
    )

    # Show files button if there are attachments
    if attachment_count > 0:
        builder.add(
            create_inline_button(
                f"\U0001f4c1 {t('tasks.view_files', locale=locale)} ({attachment_count})",
                callback_data=f"task_files_{task_id}_{checklist_id or 0}",
            )
        )

    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data=f"checklist_{checklist_id}"
            if checklist_id is not None
            else "my_tasks",
        )
    )
    builder.adjust(1)
    return builder


def get_skip_description_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build keyboard to skip description step."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("tasks.skip_description", locale=locale),
            callback_data="skip_description",
            style=ButtonStyle.PRIMARY,
        )
    )
    return builder


def get_back_to_task_keyboard(
    task_id: int, checklist_id: int | None = None, *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build keyboard to return to task after attachment."""
    builder = InlineKeyboardBuilder()
    back_callback = f"task_{task_id}_{checklist_id or 0}"
    builder.add(
        create_inline_button(
            f"\u2190 {t('tasks.back_to_task', locale=locale)}",
            callback_data=back_callback,
        )
    )
    return builder


def get_task_attachments_keyboard(
    attachments: list[dict],
    task_id: int,
    checklist_id: int | None = None,
    *,
    locale: str = "en",
) -> InlineKeyboardBuilder:
    """Build keyboard for task attachments list."""
    builder = InlineKeyboardBuilder()

    for att in attachments[:10]:
        filename = att.get("filename", "file")
        emoji = (
            "\U0001f4f7"
            if any(
                ext in filename.lower()
                for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]
            )
            else "\U0001f4c4"
        )
        builder.add(
            create_inline_button(
                f"{emoji} {filename[:30]}{'...' if len(filename) > 30 else ''}",
                callback_data=f"download_task_file_{task_id}_{att.get('id')}_{checklist_id or 0}",
            )
        )

    # Back to task button
    builder.add(
        create_inline_button(
            f"\u2190 {t('tasks.back_to_task', locale=locale)}",
            callback_data=f"task_{task_id}_{checklist_id or 0}",
        )
    )

    builder.adjust(1)
    return builder
