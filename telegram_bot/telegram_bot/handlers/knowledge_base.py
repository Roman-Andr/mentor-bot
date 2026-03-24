"""Knowledge base and FAQ handlers."""

import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.knowledge_kb import (
    get_admin_knowledge_keyboard,
    get_article_view_keyboard,
    get_faq_keyboard,
    get_kb_article_saved_keyboard,
    get_kb_categories_keyboard,
    get_kb_create_files_keyboard,
    get_kb_upload_complete_keyboard,
    get_kb_upload_files_keyboard,
    get_knowledge_base_menu_keyboard,
    get_search_no_results_keyboard,
    get_search_results_keyboard,
)
from telegram_bot.services.knowledge_client import knowledge_client
from telegram_bot.states.auth_states import (
    ArticleCreateStates,
    FileUploadStates,
    SearchStates,
)
from telegram_bot.utils.cache import cache, cached
from telegram_bot.utils.formatters import format_search_results

logger = logging.getLogger(__name__)

router = Router()

MIN_QUERY_LENGTH = 3
SEARCH_RESULTS_TTL = 600


@cached(ttl=300, key_prefix="kb_menu")
async def _get_knowledge_base_menu() -> dict:
    """Get knowledge base menu (cached)."""
    return {
        "title": "Knowledge Base",
        "description": "Find answers to common questions, documentation, and resources.",
    }


@router.message(Command("knowledge"))
@router.message(F.text == "\U0001f50d Knowledge Base")
@router.message(F.text == "Knowledge Base")
@router.callback_query(F.data == "knowledge_base")
async def knowledge_base_menu(
    update: Message | CallbackQuery, *, locale: str = "en"
) -> None:
    """Show knowledge base menu."""
    if isinstance(update, CallbackQuery):
        msg = update.message
        if msg is None:
            return
        await update.answer()
    else:
        msg = update

    text = f"*\U0001f4da {t('knowledge.title', locale=locale)}*\n\n{t('knowledge.description', locale=locale)}"

    if isinstance(update, CallbackQuery):
        await msg.edit_text(
            text,
            reply_markup=get_knowledge_base_menu_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    else:
        await msg.answer(
            text,
            reply_markup=get_knowledge_base_menu_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "search_kb")
async def start_search(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "en"
) -> None:
    """Start knowledge base search."""
    if callback.message:
        await callback.message.edit_text(
            f"\U0001f50d *{t('knowledge.search_prompt', locale=locale)}*",
            parse_mode="Markdown",
        )
    await state.set_state(SearchStates.waiting_for_query)
    await state.update_data(locale=locale)
    await callback.answer()


@router.message(SearchStates.waiting_for_query)
async def process_search_query(
    message: Message,
    state: FSMContext,
    user: dict | None = None,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """Process search query."""
    query = (message.text or "").strip()

    if len(query) < MIN_QUERY_LENGTH:
        await message.answer(t("knowledge.search_too_short", locale=locale))
        return

    if not auth_token:
        await message.answer(t("common.auth_required", locale=locale))
        return

    search_results = await knowledge_client.search_articles(
        query=query,
        auth_token=auth_token,
        page=1,
        size=5,
    )

    if not search_results.results:
        title = t(
            "knowledge.search_results_title",
            locale=locale,
            query=query,
        )
        no_results = t("knowledge.search_no_results", locale=locale)
        text = f"\U0001f50d *{title}*\n\n{no_results}"
        await message.answer(
            text,
            reply_markup=get_search_no_results_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
        await state.clear()
        return

    user_id = message.from_user.id if message.from_user else 0
    results_list = []
    formatted_results = []
    for result in search_results.results:
        results_list.append({"id": result.id, "title": result.title})
        formatted_results.append(
            {
                "title": result.title or "Untitled",
                "snippet": result.excerpt or result.highlighted_content or "",
                "category": result.category_name or "General",
                "relevance": result.relevance_score or 0,
            }
        )
    await cache.set(f"kb_search:{user_id}", results_list, SEARCH_RESULTS_TTL)

    text = format_search_results(query, formatted_results, locale=locale)

    await message.answer(
        text,
        reply_markup=get_search_results_keyboard(
            search_results.results, locale=locale
        ).as_markup(),
        parse_mode="Markdown",
    )
    await state.clear()


@router.callback_query(F.data.startswith("kb_view_"))
async def view_search_result(
    callback: CallbackQuery,
    user: dict | None = None,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """View details of a search result with attachments."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    try:
        idx = int(callback.data.split("_")[-1])
    except ValueError, IndexError:
        await callback.answer(t("common.error_generic", locale=locale))
        return

    user_id = callback.from_user.id if callback.from_user else 0
    results = await cache.get(f"kb_search:{user_id}") or []
    if idx >= len(results):
        await callback.answer(
            t("knowledge.result_unavailable", locale=locale), show_alert=True
        )
        return

    article_id = results[idx]["id"]
    article = await knowledge_client.get_article_details(article_id, auth_token)
    if not article:
        await callback.answer(
            t("knowledge.article_not_found", locale=locale), show_alert=True
        )
        return

    title = article.get("title", "Untitled")
    content = article.get("content", "")
    excerpt = article.get("excerpt", "")
    attachments = article.get("attachments", [])

    text = f"\U0001f4c4 *{title}*\n\n"
    if excerpt:
        text += f"{excerpt}\n\n"
    elif content:
        preview = content[:500]
        if len(content) > 500:
            preview += "..."
        text += f"{preview}\n\n"

    if attachments:
        text += f"\U0001f4ce *{t('knowledge.attachments', locale=locale)}*\n"
        for att in attachments:
            name = att.get("name", "file")
            size = att.get("file_size")
            size_str = f" ({_format_file_size(size)})" if size else ""
            text += f"  \u2022 {name}{size_str}\n"

    await callback.message.edit_text(
        text,
        reply_markup=get_article_view_keyboard(
            attachments, article_id, locale=locale
        ).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("kb_dl_"))
async def download_kb_attachment(
    callback: CallbackQuery, auth_token: str | None = None, *, locale: str = "en"
) -> None:
    """Download an attachment from a knowledge base article."""
    if callback.message is None:
        await callback.answer(t("common.error_generic", locale=locale))
        return

    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    parts = callback.data.split("_")
    try:
        attachment_id = int(parts[2])
        article_id = int(parts[3])
    except ValueError, IndexError:
        await callback.answer(t("common.error_generic", locale=locale))
        return

    await callback.answer(t("common.loading", locale=locale))

    attachments = await knowledge_client.get_article_attachments(article_id, auth_token)
    attachment = next((a for a in attachments if a.get("id") == attachment_id), None)

    if not attachment:
        await callback.answer(t("common.error_generic", locale=locale), show_alert=True)
        return

    filename = attachment.get("name", "file")
    file_content = await knowledge_client.download_attachment(
        article_id, filename, auth_token
    )

    if not file_content:
        await callback.answer(t("common.failed", locale=locale), show_alert=True)
        return

    try:
        input_file = BufferedInputFile(file=file_content, filename=filename)
        bot = Bot.get_current()
        if bot and callback.message:
            await bot.send_document(
                chat_id=callback.message.chat.id,
                document=input_file,
                caption=f"\U0001f4c4 {filename}",
            )
    except Exception:
        logger.exception("Failed to send file")
        await callback.answer(t("common.failed", locale=locale), show_alert=True)


@router.callback_query(F.data == "kb_categories")
async def kb_categories(
    callback: CallbackQuery, auth_token: str | None = None, *, locale: str = "en"
) -> None:
    """Show knowledge base categories."""
    if callback.message is None:
        return

    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    await callback.message.edit_text(
        f"\U0001f4d6 *{t('knowledge.btn_categories', locale=locale)}*\n\n"
        f"Browse the knowledge base by category.\n\n"
        f"Use the search feature to find specific topics, or check the FAQ for common questions.",
        reply_markup=get_kb_categories_keyboard(locale=locale).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


def _format_file_size(size_bytes: int | None) -> str:
    """Format file size for display."""
    if not size_bytes:
        return ""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


@cached(ttl=3600, key_prefix="kb_faq")
async def _get_faq_data(locale: str = "en") -> list[tuple[str, str]]:
    """Get FAQ data (cached)."""
    return [
        (
            "\u2753 How do I request time off?",
            "Use the HR portal or contact your manager.",
        ),
        (
            "\U0001f4bb IT support contact",
            "Email: it-support@company.com or call ext. 555",
        ),
        ("\U0001f3e2 Office access", "Your badge will be activated on your first day."),
        (
            "\U0001f37d\ufe0f Lunch options",
            "Cafeteria is open 11:30-14:00, delivery services available.",
        ),
        (
            "\U0001f697 Parking information",
            "Register your vehicle with security for a parking pass.",
        ),
    ]


@router.callback_query(F.data == "show_faq")
async def show_faq(callback: CallbackQuery, *, locale: str = "en") -> None:
    """Show frequently asked questions."""
    faq_items = await _get_faq_data(locale=locale)

    text = f"\u2753 *{t('knowledge.faq_title', locale=locale)}*\n\n"
    for question, answer in faq_items:
        text += f"*{question}*\n{answer}\n\n"

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_faq_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


# ---------------------------------------------------------------------------
# Admin Knowledge Base Management
# ---------------------------------------------------------------------------

ALLOWED_FILE_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "docx", "xlsx", "txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _is_allowed_file(filename: str) -> bool:
    """Check if a file extension is allowed."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_FILE_EXTENSIONS


@router.callback_query(F.data == "admin_knowledge")
async def admin_knowledge_menu(
    callback: CallbackQuery, user: dict, *, locale: str = "en"
) -> None:
    """Show admin knowledge base management menu."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    if callback.message:
        msg = (
            "\U0001f4da *Knowledge Base Management*\n\n"
            "Create articles and upload file attachments directly from the bot."
        )
        await callback.message.edit_text(
            msg,
            reply_markup=get_admin_knowledge_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "kb_create_article")
async def start_article_create(
    callback: CallbackQuery, state: FSMContext, user: dict, *, locale: str = "en"
) -> None:
    """Start creating a new article."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    await state.set_state(ArticleCreateStates.waiting_for_title)
    await state.update_data(files=[])
    if callback.message:
        await callback.message.edit_text(
            "\U0001f4dd *Create New Article*\n\nSend the *title* for the new article:",
            parse_mode="Markdown",
        )
    await callback.answer()


@router.message(ArticleCreateStates.waiting_for_title)
async def process_article_title(message: Message, state: FSMContext) -> None:
    """Receive article title."""
    title = (message.text or "").strip()
    if not title:
        await message.answer("Please send a text title.")
        return

    await state.update_data(title=title)
    await state.set_state(ArticleCreateStates.waiting_for_content)
    await message.answer(
        f"Title: *{title}*\n\nNow send the *content* of the article (Markdown supported):",
        parse_mode="Markdown",
    )


@router.message(ArticleCreateStates.waiting_for_content)
async def process_article_content(message: Message, state: FSMContext) -> None:
    """Receive article content."""
    content = (message.text or "").strip()
    if not content:
        await message.answer("Please send the article content as text.")
        return

    await state.update_data(content=content)
    await state.set_state(ArticleCreateStates.waiting_for_files)

    await message.answer(
        "Content saved.\n\n"
        "You can now send *files* (PDF, images, DOCX, XLSX, TXT) as attachments, "
        "or tap *Done* to save the article without files.",
        reply_markup=get_kb_create_files_keyboard().as_markup(),
        parse_mode="Markdown",
    )


@router.message(ArticleCreateStates.waiting_for_files, F.document)
async def process_article_file(message: Message, state: FSMContext) -> None:
    """Receive a file for the new article being created."""
    document = message.document
    if not document:
        await message.answer("No file detected.")
        return

    if not document.file_name or not _is_allowed_file(document.file_name):
        await message.answer(
            f"File type not allowed. Accepted: {', '.join(sorted(ALLOWED_FILE_EXTENSIONS))}"
        )
        return

    if document.file_size and document.file_size > MAX_FILE_SIZE:
        await message.answer("File is too large. Maximum size is 10 MB.")
        return

    bot = Bot.get_current()
    if not bot:
        return
    file = await bot.get_file(document.file_id)
    file_bytes = await bot.download_file(file.file_path) if file.file_path else None

    if not file_bytes:
        await message.answer("Failed to download file.")
        return

    data = await state.get_data()
    files: list[dict] = data.get("files", [])
    files.append(
        {
            "filename": document.file_name,
            "content": file_bytes.read(),
            "content_type": document.mime_type or "application/octet-stream",
        }
    )
    await state.update_data(files=files)

    await message.answer(
        f"\U0001f4ce *{document.file_name}* added ({len(files)} file(s) total).\nSend more files or tap *Done*.",
        parse_mode="Markdown",
    )


@router.callback_query(
    ArticleCreateStates.waiting_for_files, F.data == "kb_create_save"
)
async def save_article(
    callback: CallbackQuery,
    state: FSMContext,
    user: dict,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """Create the article and upload attached files."""
    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    data = await state.get_data()
    title: str = data.get("title", "")
    content: str = data.get("content", "")
    files: list[dict] = data.get("files", [])
    department: str | None = user.get("department") if user else None

    await callback.answer(t("common.loading", locale=locale))

    article = await knowledge_client.create_article(
        title=title,
        content=content,
        auth_token=auth_token,
        department=department,
    )

    if not article:
        if callback.message:
            await callback.message.edit_text(t("common.failed", locale=locale))
        await state.clear()
        return

    article_id = article.get("id")
    if not article_id:
        if callback.message:
            await callback.message.edit_text(t("common.failed", locale=locale))
        await state.clear()
        return

    uploaded = 0
    for f in files:
        result = await knowledge_client.upload_attachment(
            article_id=int(article_id),
            file_bytes=f["content"],
            filename=f["filename"],
            auth_token=auth_token,
            content_type=f["content_type"],
        )
        if result:
            uploaded += 1

    await state.clear()

    text = f"\u2705 Article created: *{title}*\nID: `{article_id}`"
    if files:
        text += f"\n\U0001f4ce Uploaded {uploaded}/{len(files)} file(s)"

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_kb_article_saved_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )


@router.callback_query(
    ArticleCreateStates.waiting_for_files, F.data == "kb_create_cancel"
)
async def cancel_article_create(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel article creation."""
    await state.clear()
    if callback.message:
        await callback.message.edit_text("Article creation cancelled.")
    await callback.answer()


@router.callback_query(F.data == "kb_upload_file")
async def start_file_upload(
    callback: CallbackQuery, state: FSMContext, user: dict, *, locale: str = "en"
) -> None:
    """Start uploading files to an existing article."""
    if not user or user.get("role") not in ("HR", "ADMIN"):
        await callback.answer(t("common.access_denied", locale=locale), show_alert=True)
        return

    await state.set_state(FileUploadStates.waiting_for_article_id)
    if callback.message:
        await callback.message.edit_text(
            "\U0001f4e4 *Upload File to Article*\n\nSend the *article ID* you want to attach files to:",
            parse_mode="Markdown",
        )
    await callback.answer()


@router.message(FileUploadStates.waiting_for_article_id)
async def process_upload_article_id(
    message: Message,
    state: FSMContext,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """Receive article ID for file upload."""
    text = (message.text or "").strip()
    try:
        article_id = int(text)
    except ValueError:
        await message.answer("Please send a valid numeric article ID.")
        return

    if not auth_token:
        await message.answer(t("common.auth_required", locale=locale))
        await state.clear()
        return

    article = await knowledge_client.get_article_details(article_id, auth_token)
    if not article:
        await message.answer("Article not found. Please check the ID and try again.")
        return

    await state.update_data(article_id=article_id, files=[])
    await state.set_state(FileUploadStates.waiting_for_files)

    title = article.get("title", "Untitled")

    await message.answer(
        f"Article: *{title}*\nID: `{article_id}`\n\n"
        "Send *files* (PDF, images, DOCX, XLSX, TXT) to upload, "
        "or tap *Done* when finished.",
        reply_markup=get_kb_upload_files_keyboard().as_markup(),
        parse_mode="Markdown",
    )


@router.message(FileUploadStates.waiting_for_files, F.document)
async def process_upload_file(message: Message, state: FSMContext) -> None:
    """Receive a file for uploading to an article."""
    document = message.document
    if not document:
        await message.answer("No file detected.")
        return

    if not document.file_name or not _is_allowed_file(document.file_name):
        await message.answer(
            f"File type not allowed. Accepted: {', '.join(sorted(ALLOWED_FILE_EXTENSIONS))}"
        )
        return

    if document.file_size and document.file_size > MAX_FILE_SIZE:
        await message.answer("File is too large. Maximum size is 10 MB.")
        return

    bot = Bot.get_current()
    if not bot:
        return
    file = await bot.get_file(document.file_id)
    file_bytes = await bot.download_file(file.file_path) if file.file_path else None

    if not file_bytes:
        await message.answer("Failed to download file.")
        return

    data = await state.get_data()
    files: list[dict] = data.get("files", [])
    files.append(
        {
            "filename": document.file_name,
            "content": file_bytes.read(),
            "content_type": document.mime_type or "application/octet-stream",
        }
    )
    await state.update_data(files=files)

    await message.answer(
        f"\U0001f4ce *{document.file_name}* added ({len(files)} file(s) total).\nSend more files or tap *Done*.",
        parse_mode="Markdown",
    )


@router.callback_query(FileUploadStates.waiting_for_files, F.data == "kb_upload_save")
async def save_uploaded_files(
    callback: CallbackQuery,
    state: FSMContext,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """Upload all collected files to the article."""
    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    data = await state.get_data()
    article_id: int = data.get("article_id", 0)
    files: list[dict] = data.get("files", [])

    if not files:
        await callback.answer("No files to upload", show_alert=True)
        return

    await callback.answer(t("common.loading", locale=locale))

    uploaded = 0
    for f in files:
        result = await knowledge_client.upload_attachment(
            article_id=article_id,
            file_bytes=f["content"],
            filename=f["filename"],
            auth_token=auth_token,
            content_type=f["content_type"],
        )
        if result:
            uploaded += 1

    await state.clear()

    text = f"\u2705 Uploaded {uploaded}/{len(files)} file(s) to article `{article_id}`"

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_kb_upload_complete_keyboard().as_markup(),
            parse_mode="Markdown",
        )


@router.callback_query(FileUploadStates.waiting_for_files, F.data == "kb_upload_cancel")
async def cancel_file_upload(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel file upload."""
    await state.clear()
    if callback.message:
        await callback.message.edit_text("File upload cancelled.")
    await callback.answer()
