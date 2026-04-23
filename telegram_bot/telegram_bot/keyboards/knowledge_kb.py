"""Knowledge base keyboards."""

from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_knowledge_base_menu_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build knowledge base main menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f50d {t('knowledge.btn_search', locale=locale)}",
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2753 {t('knowledge.btn_faq', locale=locale)}",
            callback_data="show_faq",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4d6 {t('knowledge.btn_categories', locale=locale)}",
            callback_data="kb_categories",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_search_no_results_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build keyboard for search with no results."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f50d {t('knowledge.search_again', locale=locale)}",
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u274c {t('knowledge.answer_not_found', locale=locale)}",
            callback_data="escalate_question",
            style=ButtonStyle.DANGER,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_search_results_keyboard(
    results: list,
    *,
    locale: str = "en",
    page: int = 1,
    total_pages: int = 1,
    query: str = "",
) -> InlineKeyboardBuilder:
    """Build keyboard for search results with pagination."""
    builder = InlineKeyboardBuilder()
    for idx, result in enumerate(results):
        builder.add(
            create_inline_button(
                f"\U0001f4c4 {(result.title or 'View result')[:45]}",
                callback_data=f"kb_view_{idx}_{page}",
            )
        )

    # Add pagination buttons if needed
    if total_pages > 1:
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(
                create_inline_button(
                    "\u25c0\ufe0f",
                    callback_data=f"kb_search_page_{page - 1}_{query[:50]}",
                )
            )
        pagination_buttons.append(
            create_inline_button(
                f"{page}/{total_pages}",
                callback_data="kb_search_nop",
            )
        )
        if page < total_pages:
            pagination_buttons.append(
                create_inline_button(
                    "\u25b6\ufe0f",
                    callback_data=f"kb_search_page_{page + 1}_{query[:50]}",
                )
            )
        builder.add(*pagination_buttons)

    builder.add(
        create_inline_button(
            f"\U0001f50d {t('knowledge.search_again', locale=locale)}",
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u274c {t('knowledge.answer_not_found', locale=locale)}",
            callback_data="escalate_question",
            style=ButtonStyle.DANGER,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_article_view_keyboard(
    attachments: list,
    article_id: int,
    *,
    locale: str = "en",
    from_search: bool = False,
    search_page: int = 1,
) -> InlineKeyboardBuilder:
    """Build keyboard for article view with optional attachment downloads."""
    builder = InlineKeyboardBuilder()
    if attachments:
        for att in attachments[:5]:
            att_id = att.get("id")
            att_name = att.get("name", "file")
            builder.add(
                create_inline_button(
                    f"\U0001f4e5 {att_name[:40]}",
                    callback_data=f"kb_dl_{att_id}_{article_id}",
                )
            )

    # Back button - either to search results or knowledge base menu
    if from_search:
        builder.add(
            create_inline_button(
                f"\u2190 {t('knowledge.back_to_results', locale=locale)}",
                callback_data=f"kb_back_to_search_{search_page}",
            )
        )

    builder.add(
        create_inline_button(
            f"\U0001f50d {t('knowledge.btn_search', locale=locale)}",
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('knowledge.back_to_kb', locale=locale)}",
            callback_data="knowledge_base",
        ),
    )
    builder.adjust(1)
    return builder


def get_kb_categories_keyboard(
    categories: list | None = None, *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build knowledge base categories keyboard."""
    builder = InlineKeyboardBuilder()

    if categories:
        for category in categories[:20]:  # Limit to 20 categories
            cat_id = category.get("id", 0)
            cat_name = category.get("name", "Unknown")
            article_count = category.get("articles_count", 0)
            display_name = (
                f"{cat_name} ({article_count})" if article_count else cat_name
            )
            builder.add(
                create_inline_button(
                    f"\U0001f4c1 {display_name[:40]}",
                    callback_data=f"kb_cat_{cat_id}",
                )
            )
    else:
        builder.add(
            create_inline_button(
                t("knowledge.no_categories", locale=locale),
                callback_data="kb_categories",
            )
        )

    builder.add(
        create_inline_button(
            f"\U0001f50d {t('knowledge.btn_search', locale=locale)}",
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="knowledge_base",
        ),
    )
    builder.adjust(1)
    return builder


def get_kb_category_articles_keyboard(
    articles: list,
    category_id: int,
    *,
    locale: str = "en",
    page: int = 1,
    total_pages: int = 1,
) -> InlineKeyboardBuilder:
    """Build keyboard for articles within a category."""
    builder = InlineKeyboardBuilder()

    for _idx, article in enumerate(articles):
        art_id = article.get("id", 0)
        art_title = article.get("title", "Untitled")
        builder.add(
            create_inline_button(
                f"\U0001f4c4 {art_title[:45]}",
                callback_data=f"kb_cat_article_{art_id}_{category_id}_{page}",
            )
        )

    # Pagination
    if total_pages > 1:
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(
                create_inline_button(
                    "\u25c0\ufe0f",
                    callback_data=f"kb_cat_page_{category_id}_{page - 1}",
                )
            )
        pagination_buttons.append(
            create_inline_button(
                f"{page}/{total_pages}",
                callback_data="kb_cat_nop",
            )
        )
        if page < total_pages:
            pagination_buttons.append(
                create_inline_button(
                    "\u25b6\ufe0f",
                    callback_data=f"kb_cat_page_{category_id}_{page + 1}",
                )
            )
        builder.add(*pagination_buttons)

    builder.add(
        create_inline_button(
            f"\u2190 {t('knowledge.back_to_categories', locale=locale)}",
            callback_data="kb_categories",
        ),
        create_inline_button(
            f"\U0001f4da {t('knowledge.back_to_kb', locale=locale)}",
            callback_data="knowledge_base",
        ),
    )
    builder.adjust(1)
    return builder


def get_kb_category_article_view_keyboard(
    attachments: list,
    article_id: int,
    category_id: int,
    *,
    locale: str = "en",
    page: int = 1,
) -> InlineKeyboardBuilder:
    """Build keyboard for viewing article from category."""
    builder = InlineKeyboardBuilder()
    if attachments:
        for att in attachments[:5]:
            att_id = att.get("id")
            att_name = att.get("name", "file")
            builder.add(
                create_inline_button(
                    f"\U0001f4e5 {att_name[:40]}",
                    callback_data=f"kb_dl_{att_id}_{article_id}",
                )
            )

    builder.add(
        create_inline_button(
            f"\u2190 {t('knowledge.back_to_category', locale=locale)}",
            callback_data=f"kb_cat_{category_id}_page_{page}",
        ),
        create_inline_button(
            f"\U0001f4d6 {t('knowledge.back_to_categories', locale=locale)}",
            callback_data="kb_categories",
        ),
        create_inline_button(
            f"\U0001f4da {t('knowledge.back_to_kb', locale=locale)}",
            callback_data="knowledge_base",
        ),
    )
    builder.adjust(1)
    return builder


def get_faq_keyboard(
    scenarios: list | None = None, *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build FAQ keyboard with scenario buttons."""
    builder = InlineKeyboardBuilder()

    if scenarios:
        for scenario in scenarios[:15]:  # Limit to 15 scenarios
            scenario_id = scenario.get("id", 0)
            scenario_title = scenario.get("title", "Untitled")
            scenario_category = scenario.get("category", "")
            prefix = "\u2753" if not scenario_category else f"\ud83d\udcda"
            builder.add(
                create_inline_button(
                    f"{prefix} {scenario_title[:45]}",
                    callback_data=f"kb_faq_{scenario_id}",
                )
            )
    else:
        builder.add(
            create_inline_button(
                t("knowledge.faq_empty", locale=locale),
                callback_data="kb_faq_empty",
            )
        )

    builder.add(
        create_inline_button(
            f"\U0001f50d {t('knowledge.btn_search', locale=locale)}",
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="knowledge_base",
        ),
    )
    builder.adjust(1)
    return builder


def get_faq_scenario_keyboard(
    scenario_id: int,
    steps: list[dict],
    current_step_id: int,
    *,
    locale: str = "en",
) -> InlineKeyboardBuilder:
    """Build keyboard for FAQ scenario step with options."""
    builder = InlineKeyboardBuilder()

    # Find current step
    current_step = None
    for step in steps:
        if step.get("id") == current_step_id:
            current_step = step
            break

    if current_step:
        # Add options as buttons
        options = current_step.get("options", [])
        for opt in options:
            label = opt.get("label", "")
            next_step = opt.get("next_step", 0)
            if label:
                builder.add(
                    create_inline_button(
                        f"\u2022 {label[:45]}",
                        callback_data=f"kb_faq_step_{scenario_id}_{current_step_id}_{next_step}",
                    )
                )

    builder.adjust(1)

    # Add navigation buttons
    builder.add(
        create_inline_button(
            f"\u2190 {t('knowledge.back_to_faq', locale=locale)}",
            callback_data="show_faq",
        ),
        create_inline_button(
            f"\U0001f4da {t('knowledge.back_to_kb', locale=locale)}",
            callback_data="knowledge_base",
        ),
    )
    return builder


def get_admin_knowledge_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build admin knowledge base management keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            "\U0001f4dd Create Article",
            callback_data="kb_create_article",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            "\U0001f4e4 Upload File",
            callback_data="kb_upload_file",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="admin_panel",
        ),
    )
    builder.adjust(1)
    return builder


def get_kb_create_files_keyboard() -> InlineKeyboardBuilder:
    """Build keyboard for article creation file step."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            "\u2705 Done \u2014 Save Article", callback_data="kb_create_save"
        ),
        create_inline_button("\u274c Cancel", callback_data="kb_create_cancel"),
    )
    builder.adjust(1)
    return builder


def get_kb_article_saved_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build keyboard shown after article is saved."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            "\U0001f4da Knowledge Base", callback_data="knowledge_base"
        ),
        create_inline_button(
            f"\u2190 {t('admin.title', locale=locale)}", callback_data="admin_panel"
        ),
    )
    builder.adjust(1)
    return builder


def get_kb_upload_files_keyboard() -> InlineKeyboardBuilder:
    """Build keyboard for file upload step."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("\u2705 Done", callback_data="kb_upload_save"),
        create_inline_button("\u274c Cancel", callback_data="kb_upload_cancel"),
    )
    builder.adjust(1)
    return builder


def get_kb_upload_complete_keyboard() -> InlineKeyboardBuilder:
    """Build keyboard shown after file upload is complete."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("\U0001f4e4 Upload More", callback_data="kb_upload_file"),
        create_inline_button(
            "\U0001f4da Knowledge Base", callback_data="knowledge_base"
        ),
        create_inline_button("\u2190 Admin", callback_data="admin_panel"),
    )
    builder.adjust(1)
    return builder
