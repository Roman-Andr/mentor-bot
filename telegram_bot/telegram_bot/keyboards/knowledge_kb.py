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
            t("buttons.contact_hr", locale=locale),
            callback_data="contact_hr",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_search_results_keyboard(
    results: list, *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build keyboard for search results."""
    builder = InlineKeyboardBuilder()
    for idx, result in enumerate(results):
        builder.add(
            create_inline_button(
                f"\U0001f4c4 {(result.title or 'View result')[:45]}",
                callback_data=f"kb_view_{idx}",
            )
        )
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
            t("buttons.contact_hr", locale=locale),
            callback_data="contact_hr",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_article_view_keyboard(
    attachments: list, article_id: int, *, locale: str = "en"
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
    builder.add(
        create_inline_button(
            f"\U0001f50d {t('knowledge.btn_search', locale=locale)}",
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_kb_categories_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build knowledge base categories keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            t("buttons.search", locale=locale),
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            t("knowledge.btn_faq", locale=locale),
            callback_data="show_faq",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="knowledge_base",
        ),
    )
    builder.adjust(1)
    return builder


def get_faq_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build FAQ keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f50d {t('knowledge.btn_search', locale=locale)}",
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            t("buttons.contact_hr", locale=locale),
            callback_data="contact_hr",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="knowledge_base",
        ),
    )
    builder.adjust(1)
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
