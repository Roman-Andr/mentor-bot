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
    get_faq_scenario_keyboard,
    get_kb_article_saved_keyboard,
    get_kb_categories_keyboard,
    get_kb_category_article_view_keyboard,
    get_kb_category_articles_keyboard,
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
from telegram_bot.utils.file_rate_limiter import file_upload_rate_limit
from telegram_bot.utils.formatters import format_search_results

logger = logging.getLogger(__name__)

router = Router()

MIN_QUERY_LENGTH = 3
SEARCH_RESULTS_TTL = 600


async def _get_user_from_callback(callback: CallbackQuery) -> dict | None:
    """Get user data from callback query."""
    # Try to get user from middleware data if available
    # Otherwise return basic info from callback
    if callback.from_user:
        return {
            "id": callback.from_user.id,
            "first_name": callback.from_user.first_name,
            "last_name": callback.from_user.last_name,
            "username": callback.from_user.username,
        }
    return None


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
@router.message(F.text == "\U0001f50d \u0411\u0430\u0437\u0430 \u0437\u043d\u0430\u043d\u0438\u0439")
@router.message(F.text == "\u0411\u0430\u0437\u0430 \u0437\u043d\u0430\u043d\u0438\u0439")
@router.callback_query(F.data == "knowledge_base")
async def knowledge_base_menu(
    update: Message | CallbackQuery,
    state: FSMContext,
    *,
    locale: str = "en",
) -> None:
    """Show knowledge base menu."""
    # Clear any active FSM state (e.g., from task file upload)
    await state.clear()

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
async def start_search(callback: CallbackQuery, state: FSMContext, *, locale: str = "en") -> None:
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

    # Perform search
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

    # Cache search results with query info for pagination and back navigation
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

    # Store full search context in cache
    search_cache_key = f"kb_search:{user_id}"
    await cache.set(
        search_cache_key,
        {
            "results": results_list,
            "query": query,
            "page": search_results.page,
            "pages": search_results.pages,
        },
        SEARCH_RESULTS_TTL,
    )

    text = format_search_results(query, formatted_results, locale=locale)

    await message.answer(
        text,
        reply_markup=get_search_results_keyboard(
            search_results.results,
            locale=locale,
            page=search_results.page,
            total_pages=search_results.pages,
            query=query,
        ).as_markup(),
        parse_mode="Markdown",
    )
    await state.clear()


@router.callback_query(F.data.startswith("kb_search_page_"))
async def handle_search_pagination(
    callback: CallbackQuery,
    user: dict | None = None,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """Handle search pagination."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    # Parse page number from callback data
    parts = callback.data.split("_")
    try:
        page = int(parts[3])
        query = "_".join(parts[4:]) if len(parts) > 4 else ""
    except (ValueError, IndexError):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    await callback.answer(t("common.loading", locale=locale))

    # Re-run search with new page
    search_results = await knowledge_client.search_articles(
        query=query,
        auth_token=auth_token,
        page=page,
        size=5,
    )

    if not search_results.results:
        await callback.message.edit_text(
            t("knowledge.search_no_results", locale=locale),
            reply_markup=get_search_no_results_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
        return

    # Update cache with new results
    user_id = callback.from_user.id if callback.from_user else 0
    results_list = [{"id": r.id, "title": r.title} for r in search_results.results]
    formatted_results = [
        {
            "title": r.title or "Untitled",
            "snippet": r.excerpt or r.highlighted_content or "",
            "category": r.category_name or "General",
            "relevance": r.relevance_score or 0,
        }
        for r in search_results.results
    ]

    await cache.set(
        f"kb_search:{user_id}",
        {
            "results": results_list,
            "query": query,
            "page": page,
            "pages": search_results.pages,
        },
        SEARCH_RESULTS_TTL,
    )

    text = format_search_results(query, formatted_results, locale=locale)

    await callback.message.edit_text(
        text,
        reply_markup=get_search_results_keyboard(
            search_results.results,
            locale=locale,
            page=page,
            total_pages=search_results.pages,
            query=query,
        ).as_markup(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "kb_search_nop")
async def search_pagination_nop(callback: CallbackQuery) -> None:
    """Handle pagination no-op button (just shows page number)."""
    await callback.answer()


@router.callback_query(F.data.startswith("kb_back_to_search_"))
async def back_to_search_results(
    callback: CallbackQuery,
    user: dict | None = None,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """Go back to search results."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    # Get page from callback data
    parts = callback.data.split("_")
    try:
        page = int(parts[4]) if len(parts) > 4 else 1
    except ValueError:
        page = 1

    await callback.answer(t("common.loading", locale=locale))

    # Get search context from cache
    user_id = callback.from_user.id if callback.from_user else 0
    search_data = await cache.get(f"kb_search:{user_id}")

    if not search_data or not isinstance(search_data, dict):
        await callback.message.edit_text(
            t("knowledge.result_unavailable", locale=locale),
            reply_markup=get_knowledge_base_menu_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
        return

    query = search_data.get("query", "")
    if not query:
        await callback.message.edit_text(
            t("knowledge.result_unavailable", locale=locale),
            reply_markup=get_knowledge_base_menu_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
        return

    # Re-run search
    search_results = await knowledge_client.search_articles(
        query=query,
        auth_token=auth_token,
        page=page,
        size=5,
    )

    if not search_results.results:
        await callback.message.edit_text(
            t("knowledge.search_no_results", locale=locale),
            reply_markup=get_search_no_results_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
        return

    # Update cache
    results_list = [{"id": r.id, "title": r.title} for r in search_results.results]
    formatted_results = [
        {
            "title": r.title or "Untitled",
            "snippet": r.excerpt or r.highlighted_content or "",
            "category": r.category_name or "General",
            "relevance": r.relevance_score or 0,
        }
        for r in search_results.results
    ]

    await cache.set(
        f"kb_search:{user_id}",
        {
            "results": results_list,
            "query": query,
            "page": page,
            "pages": search_results.pages,
        },
        SEARCH_RESULTS_TTL,
    )

    text = format_search_results(query, formatted_results, locale=locale)

    await callback.message.edit_text(
        text,
        reply_markup=get_search_results_keyboard(
            search_results.results,
            locale=locale,
            page=page,
            total_pages=search_results.pages,
            query=query,
        ).as_markup(),
        parse_mode="Markdown",
    )


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
        parts = callback.data.split("_")
        idx = int(parts[2])
        search_page = int(parts[3]) if len(parts) > 3 else 1
    except (ValueError, IndexError):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    user_id = callback.from_user.id if callback.from_user else 0
    search_data = await cache.get(f"kb_search:{user_id}")

    if not search_data or not isinstance(search_data, dict):
        await callback.answer(t("knowledge.result_unavailable", locale=locale), show_alert=True)
        return

    results = search_data.get("results", [])
    if idx >= len(results):
        await callback.answer(t("knowledge.result_unavailable", locale=locale), show_alert=True)
        return

    article_id = results[idx]["id"]
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
            attachments,
            article_id,
            locale=locale,
            from_search=True,
            search_page=search_page,
        ).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("kb_dl_"))
async def download_kb_attachment(
    callback: CallbackQuery,
    bot: Bot,
    auth_token: str | None = None,
    *,
    locale: str = "en",
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
    except (ValueError, IndexError):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    await callback.answer(t("common.loading", locale=locale))

    attachments = await knowledge_client.get_article_attachments(article_id, auth_token)
    attachment = next((a for a in attachments if a.get("id") == attachment_id), None)

    if not attachment:
        await callback.answer(t("common.error_generic", locale=locale), show_alert=True)
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
            caption=f"\U0001f4c4 {filename}",
        )
    except Exception:
        logger.exception("Failed to send file")
        await callback.answer(t("common.failed", locale=locale), show_alert=True)


@router.callback_query(F.data == "kb_categories")
async def kb_categories(
    callback: CallbackQuery,
    state: FSMContext,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """Show knowledge base categories."""
    if callback.message is None:
        return

    # Clear any active FSM state (e.g., from task file upload)
    await state.clear()

    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    await callback.answer(t("common.loading", locale=locale))

    # Fetch categories from API
    categories_data = await knowledge_client.get_categories(auth_token, skip=0, limit=50)
    categories = categories_data.get("categories", [])

    if categories:
        text = f"\U0001f4d6 *{t('knowledge.categories_title', locale=locale)}*\n\n{t('knowledge.categories_description', locale=locale)}"
    else:
        text = f"\U0001f4d6 *{t('knowledge.categories_title', locale=locale)}*\n\n{t('knowledge.no_categories', locale=locale)}"

    await callback.message.edit_text(
        text,
        reply_markup=get_kb_categories_keyboard(
            categories=categories if categories else None,
            locale=locale,
        ).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("kb_cat_"),
    ~F.data.startswith("kb_cat_article_") & ~F.data.startswith("kb_cat_page_") & ~F.data.startswith("kb_cat_nop"),
)
async def kb_category_articles(
    callback: CallbackQuery,
    state: FSMContext,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """Show articles within a category."""
    logger.info(f"kb_category_articles: {callback.data}")

    if callback.message is None:
        return

    # Clear any active FSM state
    await state.clear()

    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    # Parse category ID and optional page from callback
    parts = callback.data.split("_")
    try:
        category_id = int(parts[2])
        # Handle page parameter if present: kb_cat_{id}_page_{page}
        page = int(parts[4]) if len(parts) >= 5 and parts[3] == "page" else 1
    except (ValueError, IndexError) as e:
        logger.exception(f"Failed to parse callback data: {e}, parts: {parts}")
        await callback.answer(t("common.error_generic", locale=locale))
        return

    await callback.answer(t("common.loading", locale=locale))

    # Fetch articles for this category
    skip = (page - 1) * 10
    articles_data = await knowledge_client.get_articles_by_category(category_id, auth_token, skip=skip, limit=10)
    articles = articles_data.get("articles", [])
    total_pages = articles_data.get("pages", 1)

    if articles:
        text = f"\U0001f4d6 *{t('knowledge.articles_in_category', locale=locale)}*\n\n{t('knowledge.select_article', locale=locale)}"
    else:
        text = f"\U0001f4d6 *{t('knowledge.articles_in_category', locale=locale)}*\n\n{t('knowledge.no_articles_in_category', locale=locale)}"

    await callback.message.edit_text(
        text,
        reply_markup=get_kb_category_articles_keyboard(
            articles=articles,
            category_id=category_id,
            locale=locale,
            page=page,
            total_pages=total_pages,
        ).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "kb_cat_nop")
async def category_pagination_nop(callback: CallbackQuery) -> None:
    """Handle category pagination no-op button."""
    await callback.answer()


@router.callback_query(F.data.startswith("kb_cat_page_"))
async def kb_category_pagination(
    callback: CallbackQuery,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """Handle category articles pagination."""
    if callback.message is None:
        return

    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    parts = callback.data.split("_")
    try:
        category_id = int(parts[3])
        page = int(parts[4])
    except (ValueError, IndexError):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    await callback.answer(t("common.loading", locale=locale))

    skip = (page - 1) * 10
    articles_data = await knowledge_client.get_articles_by_category(category_id, auth_token, skip=skip, limit=10)
    articles = articles_data.get("articles", [])
    total_pages = articles_data.get("pages", 1)

    if articles:
        text = f"\U0001f4d6 *{t('knowledge.articles_in_category', locale=locale)}*\n\n{t('knowledge.select_article', locale=locale)}"
    else:
        text = f"\U0001f4d6 *{t('knowledge.articles_in_category', locale=locale)}*\n\n{t('knowledge.no_articles_in_category', locale=locale)}"

    await callback.message.edit_text(
        text,
        reply_markup=get_kb_category_articles_keyboard(
            articles=articles,
            category_id=category_id,
            locale=locale,
            page=page,
            total_pages=total_pages,
        ).as_markup(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data.startswith("kb_cat_article_"))
async def view_category_article(
    callback: CallbackQuery,
    state: FSMContext,
    user: dict | None = None,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """View article from category view."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    # Clear any active FSM state
    await state.clear()

    if not auth_token:
        await callback.answer(t("common.auth_required_short", locale=locale))
        return

    # Parse: kb_cat_article_{article_id}_{category_id}_{page}
    parts = callback.data.split("_")
    try:
        article_id = int(parts[3])
        category_id = int(parts[4])
        page = int(parts[5]) if len(parts) > 5 else 1
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
        reply_markup=get_kb_category_article_view_keyboard(
            attachments,
            article_id,
            category_id,
            locale=locale,
            page=page,
        ).as_markup(),
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


@router.callback_query(F.data == "show_faq")
@router.callback_query(F.data == "faq_menu")
async def show_faq(callback: CallbackQuery, state: FSMContext, *, locale: str = "en") -> None:
    """Show frequently asked questions from API scenarios."""
    if callback.message is None:
        return

    await callback.answer(t("common.loading", locale=locale))

    # Fetch active scenarios from API
    scenarios_data = await knowledge_client.get_active_scenarios(skip=0, limit=50)
    scenarios = scenarios_data.get("scenarios", [])

    if scenarios:
        text = f"\u2753 *{t('knowledge.faq_title', locale=locale)}*\n\n{t('knowledge.faq_select_topic', locale=locale)}"
    else:
        text = f"\u2753 *{t('knowledge.faq_title', locale=locale)}*\n\n{t('knowledge.faq_empty', locale=locale)}"

    await callback.message.edit_text(
        text,
        reply_markup=get_faq_keyboard(
            scenarios=scenarios if scenarios else None,
            locale=locale,
        ).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "kb_faq_empty")
async def faq_empty_callback(callback: CallbackQuery) -> None:
    """Handle empty FAQ button click."""
    await callback.answer()


@router.callback_query(F.data.startswith("kb_faq_"), ~F.data.startswith("kb_faq_step_"))
async def view_faq_scenario(
    callback: CallbackQuery,
    state: FSMContext,
    user: dict | None = None,
    auth_token: str | None = None,
    *,
    locale: str = "en",
) -> None:
    """View FAQ scenario with steps."""
    logger.info(f"view_faq_scenario: callback_data={callback.data}")

    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    # Clear any active FSM state
    await state.clear()

    # Parse scenario ID from callback: kb_faq_{scenario_id}
    parts = callback.data.split("_")
    try:
        scenario_id = int(parts[2])
    except (ValueError, IndexError):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    await callback.answer(t("common.loading", locale=locale))

    # Fetch scenario details
    scenario = await knowledge_client.get_scenario(scenario_id)
    if not scenario or not scenario.get("id"):
        await callback.answer(t("knowledge.scenario_not_found", locale=locale), show_alert=True)
        return

    title = scenario.get("title", "Untitled")
    scenario.get("description", "")
    steps = scenario.get("steps", [])

    if not steps:
        text = f"\u2753 *{title}*\n\n_{t('knowledge.steps_not_found', locale=locale)}_\n"
        await callback.message.edit_text(
            text,
            reply_markup=get_faq_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
        await callback.answer()
        return

    # Build step map and find first step (step_number=1)
    step_map = {step.get("id"): step for step in steps}
    first_step = next((s for s in steps if s.get("step_number") == 1), None)

    if not first_step:
        first_step = steps[0]  # Fallback to first step

    current_step_id = first_step.get("id")

    # Store in state for navigation
    await state.update_data(
        faq_scenario_id=scenario_id,
        faq_step_map=step_map,
        faq_current_step_id=current_step_id,
    )

    # Show only current step
    question = first_step.get("question", "")
    text = f"\u2753 *{title}*\n\n{question}"

    await callback.message.edit_text(
        text,
        reply_markup=get_faq_scenario_keyboard(scenario_id, steps, current_step_id, locale=locale).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("kb_faq_step_"))
async def navigate_faq_step(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    locale: str = "en",
) -> None:
    """Navigate to next FAQ step based on user choice."""
    if callback.message is None:
        return

    # Parse callback: kb_faq_step_{scenario_id}_{current_step_id}_{next_step_number}
    parts = callback.data.split("_")
    try:
        scenario_id = int(parts[3])
        current_step_id = int(parts[4])
        next_step_number = int(parts[5])
    except (ValueError, IndexError):
        await callback.answer(t("common.error_generic", locale=locale))
        return

    # Get stored data
    data = await state.get_data()
    step_map = data.get("faq_step_map", {})

    import logging

    logger = logging.getLogger(__name__)
    logger.info(
        f"FAQ STEP: callback={callback.data}, step_map keys={list(step_map.keys())}, next_step={next_step_number}"
    )
    logger.info(f"FAQ STEP: full step_map={step_map}")

    # Handle special navigation
    if next_step_number == 100:  # Back to menu
        await state.clear()
        from telegram_bot.keyboards.main_menu import get_inline_main_menu

        # Get user for menu
        user = await _get_user_from_callback(callback)
        text = f"\U0001f4cb *{t('start.menu_header', locale=locale)}*"
        await callback.message.edit_text(
            text,
            reply_markup=get_inline_main_menu(user=user, locale=locale),
            parse_mode="Markdown",
        )
        await callback.answer()
        return

    if next_step_number == 101:  # Contact HR
        await callback.message.edit_text(
            f"\U0001f4ac *{t('knowledge.contact_hr', locale=locale)}*\n\n"
            f"{t('knowledge.hr_contact_info', locale=locale)}",
            reply_markup=get_faq_scenario_keyboard(
                scenario_id, list(step_map.values()), current_step_id, locale=locale
            ).as_markup(),
            parse_mode="Markdown",
        )
        await callback.answer()
        return

    # Find next step by step_number
    next_step = next((s for s in step_map.values() if s.get("step_number") == next_step_number), None)

    if not next_step:
        await callback.answer(t("knowledge.step_not_found", locale=locale), show_alert=True)
        return

    next_step_id = next_step.get("id")

    # Update state
    await state.update_data(faq_current_step_id=next_step_id)

    # Show next step
    question = next_step.get("question", "")
    text = f"\u2753 *{question}*"

    await callback.message.edit_text(
        text,
        reply_markup=get_faq_scenario_keyboard(
            scenario_id, list(step_map.values()), next_step_id, locale=locale
        ).as_markup(),
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
async def admin_knowledge_menu(callback: CallbackQuery, user: dict, *, locale: str = "en") -> None:
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
async def start_article_create(callback: CallbackQuery, state: FSMContext, user: dict, *, locale: str = "en") -> None:
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
@file_upload_rate_limit(max_uploads=20, window_seconds=3600)
async def process_article_file(message: Message, state: FSMContext) -> None:
    """Receive a file for the new article being created."""
    document = message.document
    if not document:
        await message.answer("No file detected.")
        return

    if not document.file_name or not _is_allowed_file(document.file_name):
        await message.answer(f"File type not allowed. Accepted: {', '.join(sorted(ALLOWED_FILE_EXTENSIONS))}")
        return

    if document.file_size and document.file_size > MAX_FILE_SIZE:
        await message.answer("File is too large. Maximum size is 10 MB.")
        return

    if not message.bot:
        return
    file = await message.bot.get_file(document.file_id)
    file_bytes = await message.bot.download_file(file.file_path) if file.file_path else None

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


@router.callback_query(ArticleCreateStates.waiting_for_files, F.data == "kb_create_save")
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


@router.callback_query(ArticleCreateStates.waiting_for_files, F.data == "kb_create_cancel")
async def cancel_article_create(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel article creation."""
    await state.clear()
    if callback.message:
        await callback.message.edit_text("Article creation cancelled.")
    await callback.answer()


@router.callback_query(F.data == "kb_upload_file")
async def start_file_upload(callback: CallbackQuery, state: FSMContext, user: dict, *, locale: str = "en") -> None:
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
@file_upload_rate_limit(max_uploads=20, window_seconds=3600)
async def process_upload_file(message: Message, state: FSMContext) -> None:
    """Receive a file for uploading to an article."""
    document = message.document
    if not document:
        await message.answer("No file detected.")
        return

    if not document.file_name or not _is_allowed_file(document.file_name):
        await message.answer(f"File type not allowed. Accepted: {', '.join(sorted(ALLOWED_FILE_EXTENSIONS))}")
        return

    if document.file_size and document.file_size > MAX_FILE_SIZE:
        await message.answer("File is too large. Maximum size is 10 MB.")
        return

    if not message.bot:
        return
    file = await message.bot.get_file(document.file_id)
    file_bytes = await message.bot.download_file(file.file_path) if file.file_path else None

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
