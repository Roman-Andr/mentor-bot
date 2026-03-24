"""Document access keyboards."""

from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_documents_menu_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build documents menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f4c4 {t('documents.btn_dept', locale=locale)}",
            callback_data="dept_docs",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4cb {t('documents.btn_policies', locale=locale)}",
            callback_data="company_policies",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4da {t('documents.btn_training', locale=locale)}",
            callback_data="training_materials",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_article_list_keyboard(
    articles: list[dict], back_callback: str, *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build keyboard with article buttons."""
    builder = InlineKeyboardBuilder()
    for article in articles[:10]:
        article_id = article.get("id")
        title = article.get("title", "Untitled")
        attachments = article.get("attachments", [])
        icon = "\U0001f4ce" if attachments else "\U0001f4c4"
        builder.add(
            create_inline_button(
                f"{icon} {title[:50]}",
                callback_data=f"view_article_{article_id}",
            )
        )
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data=back_callback,
        )
    )
    builder.adjust(1)
    return builder


def get_article_detail_keyboard(
    attachments: list, article_id: int, *, locale: str = "en"
) -> InlineKeyboardBuilder:
    """Build keyboard for article detail view with attachment downloads."""
    builder = InlineKeyboardBuilder()
    for att in attachments:
        att_id = att.get("id")
        att_name = att.get("name", "file")
        emoji = _get_file_emoji(att.get("mime_type"))
        builder.add(
            create_inline_button(
                f"{emoji} Download {att_name[:35]}",
                callback_data=f"download_att_{att_id}_{article_id}",
            )
        )
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="documents_menu",
        )
    )
    builder.adjust(1)
    return builder


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
