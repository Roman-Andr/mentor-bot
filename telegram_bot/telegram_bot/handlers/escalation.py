"""Escalation handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.escalation_kb import (
    get_escalation_details_keyboard,
    get_escalation_menu_keyboard,
    get_my_escalations_keyboard,
    get_new_escalation_keyboard,
)
from telegram_bot.services.escalation_client import escalation_client
from telegram_bot.states.escalation_states import EscalationStates
from telegram_bot.utils.formatters import format_escalation_list

router = Router()

MIN_DESCRIPTION_LENGTH = 10
MIN_TITLE_LENGTH = 3


@router.message(Command("escalate"))
@router.message(F.text == "🚨 Escalate")
@router.message(F.text == "🚨 Эскалация")
@router.callback_query(F.data == "escalate_menu")
async def escalation_menu(update: Message | CallbackQuery, user: dict, auth_token: str, *, locale: str = "en") -> None:
    """Show escalation menu."""
    if isinstance(update, CallbackQuery):
        msg = update.message
        await update.answer()
    else:
        msg = update

    if not user or not auth_token:
        await msg.answer(t("common.auth_required", locale=locale))
        return

    escalations = await escalation_client.get_user_escalations(user["id"], auth_token, limit=5)

    text = f"*\U0001f4de {t('escalation.title', locale=locale)}*\n\n"
    if escalations:
        text += format_escalation_list(escalations, locale=locale)
        text += "\n"
    else:
        text += f"{t('escalation.no_escalations', locale=locale)}\n\n"

    text += t("escalation.use_options", locale=locale)

    keyboard = get_escalation_menu_keyboard(locale=locale)
    if isinstance(update, CallbackQuery):
        await msg.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await msg.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "new_escalation")
async def new_escalation(callback: CallbackQuery, state: FSMContext, *, locale: str = "en") -> None:
    """Start new escalation."""
    if callback.message:
        await callback.message.edit_text(
            f"*\U0001f4de {t('escalation.new_title', locale=locale)}*\n\n{t('escalation.select_type', locale=locale)}",
            reply_markup=get_new_escalation_keyboard(locale=locale),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("escalate_") & ~F.data.startswith("escalate_menu"))
async def process_escalation_type(callback: CallbackQuery, state: FSMContext, *, locale: str = "en") -> None:
    """Process escalation type selection."""
    escalation_type = callback.data.split("_")[1]

    type_map = {
        "question": t("escalation.type_question", locale=locale),
        "mentor": t("escalation.type_mentor", locale=locale),
        "hr": t("escalation.type_hr", locale=locale),
        "technical": t("escalation.type_technical", locale=locale),
    }

    category = type_map.get(escalation_type, "General")

    await state.update_data(category=category)
    if callback.message:
        await callback.message.edit_text(
            t("escalation.describe_issue", locale=locale, category=category),
            parse_mode="Markdown",
        )
    await state.set_state(EscalationStates.waiting_for_description)
    await callback.answer()


@router.message(EscalationStates.waiting_for_description)
async def process_escalation_description(message: Message, state: FSMContext, *, locale: str = "en") -> None:
    """Process escalation description."""
    description = (message.text or "").strip()

    if len(description) < MIN_DESCRIPTION_LENGTH:
        await message.answer(
            t(
                "escalation.description_too_short",
                locale=locale,
                min=MIN_DESCRIPTION_LENGTH,
            )
        )
        return

    await state.update_data(description=description)
    await message.answer(t("escalation.enter_title", locale=locale))
    await state.set_state(EscalationStates.waiting_for_title)


@router.message(EscalationStates.waiting_for_title)
async def process_escalation_title(
    message: Message,
    state: FSMContext,
    user: dict,
    auth_token: str,
    *,
    locale: str = "en",
) -> None:
    """Process escalation title."""
    title = (message.text or "").strip()

    if len(title) < MIN_TITLE_LENGTH:
        await message.answer(t("escalation.title_too_short", locale=locale, min=MIN_TITLE_LENGTH))
        return

    data = await state.get_data()
    category = data.get("category", "General")
    description = data.get("description", "")

    escalation = await escalation_client.create_escalation(
        user_id=user["id"],
        title=title,
        description=description,
        category=category,
        auth_token=auth_token,
        priority="normal",
    )

    if escalation:
        escalation_id = escalation.get("id", "N/A")
        # Use reason from response (maps to title) or fallback to title
        display_reason = escalation.get("reason", title)
        await message.answer(
            t(
                "escalation.created",
                locale=locale,
                title=display_reason,
                category=category,
                id=escalation_id,
            ),
            parse_mode="Markdown",
        )
    else:
        await message.answer(t("escalation.create_failed", locale=locale))

    await state.clear()


@router.callback_query(F.data == "my_escalations")
async def my_escalations(callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en") -> None:
    """Show user's escalations."""
    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    escalations = await escalation_client.get_user_escalations(user["id"], auth_token, limit=20)

    text = (
        format_escalation_list(escalations, locale=locale)
        if escalations
        else t("escalation.no_escalations", locale=locale)
    )

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_my_escalations_keyboard(locale=locale),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("escalation_") & ~F.data.startswith("escalation_menu"))
async def escalation_details(callback: CallbackQuery, auth_token: str, *, locale: str = "en") -> None:
    """Show escalation details."""
    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    escalation_id = int(callback.data.split("_")[1])

    escalation = await escalation_client.get_escalation_status(escalation_id, auth_token)

    if not escalation:
        await callback.answer(t("common.error_generic", locale=locale), show_alert=True)
        return

    status = escalation.get("status", "unknown")
    # escalation_service uses 'reason' instead of 'title' and 'type' instead of 'category'
    title = escalation.get("reason", "N/A")
    category = escalation.get("type", "General")
    created_at = escalation.get("created_at", "N/A")
    # description is stored in context
    context = escalation.get("context", {})
    description = context.get("description", "No description")

    status_map = {
        "open": t("escalation.status_open", locale=locale),
        "in_progress": t("escalation.status_in_progress", locale=locale),
        "resolved": t("escalation.status_resolved", locale=locale),
        "closed": t("escalation.status_closed", locale=locale),
    }

    status_emoji = {
        "open": "\u23f3",
        "in_progress": "\U0001f504",
        "resolved": "\u2705",
        "closed": "\U0001f512",
    }.get(status, "\u2753")

    text = (
        f"*\U0001f4de {t('escalation.details_title', locale=locale)}*\n\n"
        f"*Title:* {title}\n"
        f"*Category:* {category}\n"
        f"*Status:* {status_emoji} {status_map.get(status, status)}\n"
        f"*Created:* {created_at}\n\n"
        f"*Description:*\n{description}"
    )

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_escalation_details_keyboard(locale=locale),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("escalation:view:"))
async def view_escalation_from_notification(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Show escalation details when user clicks notification link."""
    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    escalation_id = int(callback.data.split(":")[-1])

    escalation = await escalation_client.get_escalation_status(escalation_id, auth_token)

    if not escalation:
        await callback.answer(t("common.error_generic", locale=locale), show_alert=True)
        return

    # Check if user is authorized (requester, assignee, or HR)
    is_authorized = (
        escalation.get("user_id") == user["id"]
        or escalation.get("assigned_to") == user["id"]
        or user.get("role") in ["HR", "ADMIN"]
    )

    if not is_authorized:
        await callback.answer(
            t("escalation.access_denied", locale=locale, default="You don't have access to this escalation"),
            show_alert=True,
        )
        return

    status = escalation.get("status", "unknown")
    title = escalation.get("reason", "N/A")
    category = escalation.get("type", "General")
    priority = escalation.get("priority", "MEDIUM")
    created_at = escalation.get("created_at", "N/A")
    context = escalation.get("context", {})
    description = context.get("description", "No description")

    status_map = {
        "PENDING": t("escalation.status_pending", locale=locale, default="Pending"),
        "ASSIGNED": t("escalation.status_assigned", locale=locale, default="Assigned"),
        "IN_PROGRESS": t("escalation.status_in_progress", locale=locale, default="In Progress"),
        "RESOLVED": t("escalation.status_resolved", locale=locale),
        "CLOSED": t("escalation.status_closed", locale=locale),
    }

    status_emoji = {
        "PENDING": "\u23f3",
        "ASSIGNED": "\ud83d\udccc",
        "IN_PROGRESS": "\U0001f504",
        "RESOLVED": "\u2705",
        "CLOSED": "\U0001f512",
    }.get(status, "\u2753")

    text = (
        f"*\U0001f4de Escalation #{escalation_id}*\n\n"
        f"*Status:* {status_emoji} {status_map.get(status, status)}\n"
        f"*Type:* {category}\n"
        f"*Priority:* {priority}\n"
        f"*Created:* {created_at}\n\n"
        f"*Title:* {title}\n\n"
        f"*Description:*\n{description}"
    )

    if escalation.get("assigned_to_name"):
        text += f"\n\n*Assigned to:* {escalation['assigned_to_name']}"

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("escalation.add_comment", locale=locale, default="📝 Add Comment"),
                    callback_data=f"escalation:comment:{escalation_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("common.back", locale=locale, default="🔙 Back"), callback_data="escalations:list"
                )
            ],
        ]
    )

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "escalations:list")
async def list_my_escalations(callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en") -> None:
    """Show list of user's escalations (used as back button from details)."""
    await my_escalations(callback, user, auth_token, locale=locale)
