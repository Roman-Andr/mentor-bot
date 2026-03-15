"""Admin panel handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.admin_kb import get_admin_keyboard
from telegram_bot.keyboards.utils import create_inline_button

router = Router()


@router.message(Command("admin"))
async def cmd_admin(message: Message, user: dict) -> None:
    """Admin panel command."""
    if not user or user.get("role") not in ["HR", "ADMIN"]:
        await message.answer("⛔ Access denied. Admin privileges required.")
        return

    await message.answer(
        "👑 *Admin Panel*\n\nSelect an option below:", reply_markup=get_admin_keyboard(), parse_mode="Markdown"
    )


@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery, user: dict) -> None:
    """Admin panel callback."""
    if not user or user.get("role") not in ["HR", "ADMIN"]:
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    await callback.message.edit_text(
        "👑 *Admin Panel*\n\nSelect an option below:", reply_markup=get_admin_keyboard(), parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, user: dict) -> None:
    """Show admin statistics."""
    if not user or user.get("role") not in ["HR", "ADMIN"]:
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    stats_text = (
        "📊 *System Statistics*\n\n"
        "• Total users: 127\n"
        "• Active checklists: 42\n"
        "• Completed tasks: 1,254\n"
        "• Pending tasks: 189\n"
        "• Avg. onboarding time: 28 days\n"
        "• Bot uptime: 99.8%\n\n"
        "*Recent Activity*\n"
        "• 5 new users this week\n"
        "• 12 checklists completed\n"
        "• 3 escalations to HR"
    )

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("📈 Detailed Report", callback_data="detailed_report", style=ButtonStyle.PRIMARY),
        create_inline_button("📤 Export Data", callback_data="export_data", style=ButtonStyle.PRIMARY),
        create_inline_button("← Back", callback_data="admin_panel"),
    )
    builder.adjust(1)

    await callback.message.edit_text(stats_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery, user: dict) -> None:
    """Manage users."""
    if not user or user.get("role") not in ["HR", "ADMIN"]:
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("👥 List Users", callback_data="list_users", style=ButtonStyle.PRIMARY),
        create_inline_button("➕ Add User", callback_data="add_user", style=ButtonStyle.PRIMARY),
        create_inline_button("📧 Send Invite", callback_data="send_invite", style=ButtonStyle.PRIMARY),
        create_inline_button("← Back", callback_data="admin_panel"),
    )
    builder.adjust(1)

    await callback.message.edit_text(
        "👥 *User Management*\n\nManage system users and invitations.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_checklists")
async def admin_checklists(callback: CallbackQuery, user: dict) -> None:
    """Manage checklists."""
    if not user or user.get("role") not in ["HR", "ADMIN"]:
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("📋 Templates", callback_data="list_templates", style=ButtonStyle.PRIMARY),
        create_inline_button("📊 Progress", callback_data="checklist_progress", style=ButtonStyle.PRIMARY),
        create_inline_button("⚠️ Overdue", callback_data="overdue_tasks", style=ButtonStyle.DANGER),
        create_inline_button("← Back", callback_data="admin_panel"),
    )
    builder.adjust(1)

    await callback.message.edit_text(
        "📋 *Checklist Management*\n\nManage checklist templates and monitor progress.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()
