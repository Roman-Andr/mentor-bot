"""Admin panel handlers."""

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.admin import get_admin_keyboard

logger = logging.getLogger(__name__)
from telegram_bot.keyboards.admin_detail import (
    get_admin_checklists_keyboard,
    get_admin_stats_keyboard,
    get_admin_users_keyboard,
    get_back_to_admin_checklists_keyboard,
    get_back_to_admin_panel_keyboard,
    get_back_to_admin_stats_keyboard,
    get_back_to_admin_users_keyboard,
)
from telegram_bot.services.auth_client import auth_client
from telegram_bot.services.checklists_client import checklists_client

router = Router()


@router.message(Command("admin"))
@router.message(F.text == "\U0001f451 Admin")
@router.message(F.text == "Admin")
@router.message(F.text == "\U0001f451 \u0410\u0434\u043c\u0438\u043d")
@router.message(F.text == "\u0410\u0434\u043c\u0438\u043d")
async def cmd_admin(message: Message, user: dict, *, locale: str = "en") -> None:
    """Admin panel command."""
    logger.info(
        "Admin command called by user: %s, role: %s",
        user.get("id") if user else None,
        user.get("role") if user else None,
    )
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await message.answer(f"\u26d4 {t('common.access_denied', locale=locale)}")
        return

    await message.answer(
        f"\U0001f451 *{t('admin.title', locale=locale)}*\n\n{t('admin.select_option', locale=locale)}",
        reply_markup=get_admin_keyboard(locale=locale),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "admin_panel")
async def admin_panel(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Admin panel callback."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            f"\U0001f451 *{t('admin.title', locale=locale)}*\n\n{t('admin.select_option', locale=locale)}",
            reply_markup=get_admin_keyboard(locale=locale),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Show admin statistics with real data from services."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    # Fetch real stats from services
    total_users = await auth_client.get_total_users(auth_token)
    checklist_stats = await checklists_client.get_admin_stats(auth_token)

    active = checklist_stats.get("active_checklists", 0)
    completed = checklist_stats.get("completed_tasks", 0)
    pending = checklist_stats.get("pending_tasks", 0)
    avg_days = checklist_stats.get("avg_onboarding_days", 0)

    stats_text = (
        f"*\U0001f4ca {t('admin.stats_title', locale=locale)}*\n\n"
        f"\u2022 {t('admin.stats_total_users', locale=locale, count=total_users)}\n"
        f"\u2022 {t('admin.stats_active_checklists', locale=locale, count=active)}\n"
        f"\u2022 {t('admin.stats_completed_tasks', locale=locale, count=completed)}\n"
        f"\u2022 {t('admin.stats_pending_tasks', locale=locale, count=pending)}\n"
        f"\u2022 {t('admin.stats_avg_time', locale=locale, days=avg_days)}\n"
        f"\u2022 {t('admin.stats_uptime', locale=locale, uptime='99.8')}"
    )

    if callback.message:
        await callback.message.edit_text(
            stats_text,
            reply_markup=get_admin_stats_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def admin_users(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Manage users."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            f"\U0001f465 *{t('admin.users_title', locale=locale)}*\n\n{t('admin.users_description', locale=locale)}",
            reply_markup=get_admin_users_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "admin_checklists")
async def admin_checklists(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Manage checklists."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        desc = t("admin.checklists_description", locale=locale)
        title = f"\U0001f4cb *{t('admin.checklists_title', locale=locale)}*"
        await callback.message.edit_text(
            f"{title}\n\n{desc}",
            reply_markup=get_admin_checklists_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "list_users")
async def list_users(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """List system users."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    users_data = await auth_client.list_users(auth_token, page=1, size=10)

    text = f"\U0001f465 *{t('admin.btn_list_users', locale=locale)}*\n\n"
    if users_data and users_data.get("users"):
        for u in users_data["users"][:10]:
            name = f"{u.get('first_name', '')} {u.get('last_name', '')}"
            role = u.get("role", "NEWBIE")
            text += f"\u2022 {name} ({role})\n"
        text += f"\nTotal: {users_data.get('total', 0)} users"
    else:
        text += t("common.no_data", locale=locale)

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_admin_users_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "add_user")
async def add_user(callback: CallbackQuery, user: dict, *, locale: str = "en") -> None:
    """Add user placeholder."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            f"\u2795 *{t('admin.btn_add_user', locale=locale)}*\n\n{t('admin.coming_soon', locale=locale)}",
            reply_markup=get_back_to_admin_users_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "send_invite")
async def send_invite(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Send invite placeholder."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            f"\U0001f4e7 *{t('admin.btn_send_invite', locale=locale)}*\n\n{t('admin.coming_soon', locale=locale)}",
            reply_markup=get_back_to_admin_users_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "list_templates")
async def list_templates(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """List checklist templates."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    templates = await checklists_client.get_templates(auth_token)

    text = f"\U0001f4cb *{t('admin.btn_templates', locale=locale)}*\n\n"
    if templates:
        for tmpl in templates[:10]:
            name = tmpl.get("name", "Unnamed")
            tasks_count = tmpl.get("total_tasks", 0)
            text += f"\u2022 {name} ({tasks_count} tasks)\n"
    else:
        text += t("common.no_data", locale=locale)

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_admin_checklists_keyboard(
                locale=locale
            ).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "checklist_progress")
async def checklist_progress(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Show overall checklist progress."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    stats = await checklists_client.get_admin_stats(auth_token)

    text = (
        f"\U0001f4ca *{t('admin.btn_checklist_progress', locale=locale)}*\n\n"
        f"{t('admin.stats_active_checklists', locale=locale, count=stats.get('active_checklists', 0))}\n"
        f"{t('admin.stats_completed_tasks', locale=locale, count=stats.get('completed_tasks', 0))}\n"
        f"{t('admin.stats_pending_tasks', locale=locale, count=stats.get('pending_tasks', 0))}"
    )

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_admin_checklists_keyboard(
                locale=locale
            ).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "overdue_tasks")
async def overdue_tasks(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Show overdue tasks."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    tasks = await checklists_client.get_overdue_tasks(auth_token)

    text = f"\u26a0\ufe0f *{t('admin.btn_overdue', locale=locale)}*\n\n"
    if tasks:
        for task in tasks[:10]:
            title = task.get("title", "Untitled")
            due = task.get("due_date", "N/A")
            text += f"\u2022 {title} (due: {due})\n"
    else:
        text += "No overdue tasks found."

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_admin_checklists_keyboard(
                locale=locale
            ).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "admin_settings")
async def admin_settings(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Admin settings placeholder."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            f"\u2699\ufe0f *{t('admin.btn_settings', locale=locale)}*\n\n{t('admin.coming_soon', locale=locale)}",
            reply_markup=get_back_to_admin_panel_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "admin_reports")
async def admin_reports(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Admin reports placeholder."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            f"\U0001f4c8 *{t('admin.btn_reports', locale=locale)}*\n\n{t('admin.coming_soon', locale=locale)}",
            reply_markup=get_back_to_admin_panel_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "admin_alerts")
async def admin_alerts(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Admin alerts placeholder."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            f"\U0001f6a8 *{t('admin.btn_alerts', locale=locale)}*\n\n{t('admin.coming_soon', locale=locale)}",
            reply_markup=get_back_to_admin_panel_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "detailed_report")
async def detailed_report(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Detailed report placeholder."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            f"\U0001f4ca *{t('admin.btn_detailed_report', locale=locale)}*\n\n{t('admin.coming_soon', locale=locale)}",
            reply_markup=get_back_to_admin_stats_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "export_data")
async def export_data(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Export data placeholder."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            f"\U0001f4e4 *{t('admin.btn_export', locale=locale)}*\n\n{t('admin.coming_soon', locale=locale)}",
            reply_markup=get_back_to_admin_stats_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()
