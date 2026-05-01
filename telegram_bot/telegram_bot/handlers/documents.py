"""Document access handlers."""

import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.utils.formatters import escape_markdown
from telegram_bot.keyboards.documents_kb import (
    get_article_detail_keyboard,
    get_article_list_keyboard,
    get_documents_menu_keyboard,
)
from telegram_bot.services.document_client import document_client
from telegram_bot.services.knowledge_client import knowledge_client

logger = logging.getLogger(__name__)

router = Router()


def _format_file_size(size_bytes: int | None) -> str:
    """Format file size for display."""
    if not size_bytes:
        return ""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def _get_file_emoji(mime_type: str | None) -> str:
    """Get emoji for file type."""
    if not mime_type:
        return "\U0001f4ce"
    if mime_type.startswith("image/"):
        return "\U0001f5bc\ufe0f"
    if "pdf" in mime_type:
        return "\U0001f4d5"
    if "word" in mime_type or "docx" in mime_type:
        return "\U0001f4d8"
    if "sheet" in mime_type or "excel" in mime_type or "xlsx" in mime_type:
        return "\U0001f4ca"
    return "\U0001f4c4"


@router.message(Command("documents"))
@router.message(F.text == "\U0001f4c1 Documents")
@router.message(F.text == "\U0001f4c1 \u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b")
@router.message(F.text == "\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b")
@router.callback_query(F.data == "documents_menu")
async def documents_menu(
    update: Message | CallbackQuery,
    state: FSMContext,
    user: dict,
    *,
    locale: str = "en",
) -> None:
    """Show documents menu."""
    # Clear any active FSM state (e.g., from task file upload)
    await state.clear()

    msg = None
    if isinstance(update, CallbackQuery):
        await update.answer()
        msg = update.message
    else:
        msg = update

    if msg is None:
        return

    if not user:
        await msg.answer(t("common.auth_required", locale=locale))
        return

    text = (
        f"*\U0001f4c1 {t('documents.title', locale=locale)}*\n\n"
        f"{t('documents.description', locale=locale)}\n\n"
        f"  \U0001f4c4 {t('documents.btn_dept', locale=locale)}\n"
        f"  \U0001f4cb {t('documents.btn_policies', locale=locale)}\n"
        f"  \U0001f4da {t('documents.btn_training', locale=locale)}"
    )

    keyboard = get_documents_menu_keyboard(locale=locale)
    if isinstance(update, CallbackQuery) and isinstance(msg, Message):
        await msg.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await msg.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "dept_docs")
async def department_docs(callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en") -> None:
    """Show department documents."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    msg = callback.message

    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    department = user.get("department", "")
    if not department:
        await callback.answer(t("documents.no_dept", locale=locale), show_alert=True)
        return

    docs = await document_client.get_department_documents(department, auth_token)

    text = f"\U0001f4c4 *{t('documents.dept_title', locale=locale)}*\n\n"
    if docs:
        text += t("documents.tap_to_view", locale=locale)
    else:
        text += t("documents.dept_empty", locale=locale)

    await msg.edit_text(
        text,
        reply_markup=get_article_list_keyboard(docs, "documents_menu", locale=locale),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "department_docs_list")
async def department_docs_list(callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en") -> None:
    """Show department documents list from new API."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    msg = callback.message

    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    department_id = user.get("department_id")
    docs = await document_client.get_department_documents_list(department_id, auth_token)

    text = f"\U0001f4c4 *{t('documents.title', locale=locale)}*\n\n"
    if docs:
        text += t("documents.tap_to_view", locale=locale)
    else:
        text += t("documents.dept_empty", locale=locale)

    await msg.edit_text(
        text,
        reply_markup=get_article_list_keyboard(docs, "documents_menu", locale=locale, is_department_docs=True),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("download_dept_doc_"))
async def download_department_document(
    callback: CallbackQuery,
    bot: Bot,
    user: dict,
    auth_token: str,
    *,
    locale: str = "en",
) -> None:
    """Download and send a department document file."""
    if callback.message is None:
        await callback.answer(t("common.error_generic", locale=locale))
        return

    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    parts = callback.data.split("_")
    try:
        document_id = int(parts[-1])
    except (ValueError, IndexError):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    await callback.answer(t("common.loading", locale=locale))

    download_url = await document_client.get_department_document_download_url(document_id, auth_token)

    if not download_url:
        await callback.answer(t("common.failed", locale=locale), show_alert=True)
        return

    # Send the download URL as a link since we can't directly send the file
    try:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"\U0001f4ce {t('documents.download_link', locale=locale)}\n\n{download_url}",
            disable_web_page_preview=True,
        )
    except Exception:
        logger.exception("Failed to send download link to user")
        await callback.answer(t("common.failed", locale=locale), show_alert=True)


@router.callback_query(F.data == "company_policies")
async def company_policies(callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en") -> None:
    """Show company policies."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    msg = callback.message

    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    policies = await document_client.get_company_policies(auth_token)

    text = f"\U0001f4cb *{t('documents.policies_title', locale=locale)}*\n\n"
    if policies:
        text += t("documents.tap_to_view", locale=locale)
    else:
        text += t("documents.policies_empty", locale=locale)

    await msg.edit_text(
        text,
        reply_markup=get_article_list_keyboard(policies, "documents_menu", locale=locale),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "training_materials")
async def training_materials(callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en") -> None:
    """Show training materials."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    msg = callback.message

    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    materials = await document_client.get_training_materials(auth_token)

    text = f"\U0001f4da *{t('documents.training_title', locale=locale)}*\n\n"
    if materials:
        text += t("documents.tap_to_view", locale=locale)
    else:
        text += t("documents.training_empty", locale=locale)

    await msg.edit_text(
        text,
        reply_markup=get_article_list_keyboard(materials, "documents_menu", locale=locale),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view_article_"))
async def view_article_detail(callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en") -> None:
    """Show article details with attachments."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    msg = callback.message

    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    try:
        article_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    article = await knowledge_client.get_article_details(article_id, auth_token)
    if not article:
        await callback.answer(t("knowledge.article_not_found", locale=locale), show_alert=True)
        return

    title = article.get("title", "Untitled")
    content = article.get("content", "")
    excerpt = article.get("excerpt", "")
    attachments = article.get("attachments", [])

    text = f"\U0001f4c4 *{title}*\n\n"
    if excerpt:
        text += f"{excerpt}\n\n"
    elif content:
        preview = content[:300]
        if len(content) > 300:
            preview += "..."
        text += f"{preview}\n\n"

    if attachments:
        text += f"\U0001f4ce *{t('knowledge.attachments', locale=locale)}*\n"
        for att in attachments:
            emoji = _get_file_emoji(att.get("mime_type"))
            name = att.get("name", "file")
            size = _format_file_size(att.get("file_size"))
            size_str = f" ({size})" if size else ""
            text += f"{emoji} {name}{size_str}\n"

    await msg.edit_text(
        text,
        reply_markup=get_article_detail_keyboard(attachments, article_id, locale=locale),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("download_att_"))
async def download_attachment(
    callback: CallbackQuery,
    bot: Bot,
    user: dict,
    auth_token: str,
    *,
    locale: str = "en",
) -> None:
    """Download and send an attachment file."""
    if callback.message is None:
        await callback.answer(t("common.error_generic", locale=locale))
        return

    if not user or not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    parts = callback.data.split("_")
    try:
        attachment_id = int(parts[2])
        article_id = int(parts[3])
    except (ValueError, IndexError):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    await callback.answer(t("common.loading", locale=locale))

    attachments = await knowledge_client.get_article_attachments(article_id, auth_token)
    attachment = next((a for a in attachments if a.get("id") == attachment_id), None)

    if not attachment:
        await callback.answer(t("common.failed", locale=locale), show_alert=True)
        return

    filename = attachment.get("name", "file")

    file_content = await knowledge_client.download_attachment(article_id, filename, auth_token)
    if not file_content:
        await callback.answer(t("common.failed", locale=locale), show_alert=True)
        return

    try:
        input_file = BufferedInputFile(file=file_content, filename=filename)
        await bot.send_document(
            chat_id=callback.message.chat.id,
            document=input_file,
            caption=f"\U0001f4c4 {escape_markdown(filename)}",
        )
    except Exception:
        logger.exception("Failed to send file to user")
        await callback.answer(t("common.failed", locale=locale), show_alert=True)
