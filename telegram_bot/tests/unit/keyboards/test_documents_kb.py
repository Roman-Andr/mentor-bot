"""Unit tests for telegram_bot documents keyboards."""

from aiogram.types import InlineKeyboardMarkup

from telegram_bot.keyboards.documents_kb import (
    _get_file_emoji,
    get_article_detail_keyboard,
    get_article_list_keyboard,
    get_documents_menu_keyboard,
)


class TestGetDocumentsMenuKeyboard:
    """Test cases for get_documents_menu_keyboard."""

    def test_documents_menu_keyboard(self):
        """Test documents menu keyboard structure."""
        keyboard = get_documents_menu_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 5  # 4 menu items + back button

    def test_documents_menu_with_different_locale(self):
        """Test documents menu keyboard with different locale."""
        keyboard = get_documents_menu_keyboard(locale="ru")

        assert isinstance(keyboard, InlineKeyboardMarkup)


class TestGetArticleListKeyboard:
    """Test cases for get_article_list_keyboard."""

    def test_empty_article_list(self):
        """Test keyboard with empty article list."""
        articles = []
        keyboard = get_article_list_keyboard(articles, back_callback="docs_menu", locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1  # Just back button

    def test_single_article_without_attachments(self):
        """Test keyboard with single article without attachments."""
        articles = [{"id": 1, "title": "Test Article", "attachments": []}]
        keyboard = get_article_list_keyboard(articles, back_callback="docs_menu", locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Article + back button

    def test_single_article_with_attachments(self):
        """Test keyboard with single article with attachments."""
        articles = [{"id": 1, "title": "Test Article", "attachments": [{"id": 1}]}]
        keyboard = get_article_list_keyboard(articles, back_callback="docs_menu", locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Check attachment icon is present
        button_text = keyboard.inline_keyboard[0][0].text
        assert "\U0001f4ce" in button_text

    def test_multiple_articles(self):
        """Test keyboard with multiple articles."""
        articles = [
            {"id": 1, "title": "Article 1", "attachments": []},
            {"id": 2, "title": "Article 2", "attachments": [{"id": 1}]},
            {"id": 3, "title": "Article 3", "attachments": []},
        ]
        keyboard = get_article_list_keyboard(articles, back_callback="docs_menu", locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 4  # 3 articles + back button

    def test_article_title_truncation(self):
        """Test that long article titles are truncated."""
        articles = [{"id": 1, "title": "A" * 100, "attachments": []}]
        keyboard = get_article_list_keyboard(articles, back_callback="docs_menu", locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Title should be truncated to 50 chars
        button_text = keyboard.inline_keyboard[0][0].text
        assert len(button_text) < 60

    def test_department_docs_keyboard(self):
        """Test keyboard with department documents (is_department_docs=True)."""
        articles = [
            {"id": 1, "title": "Document 1", "file_name": "doc1.pdf", "mime_type": "application/pdf"},
            {"id": 2, "title": "Document 2", "file_name": "doc2.docx", "mime_type": "application/msword"},
        ]
        keyboard = get_article_list_keyboard(articles, back_callback="docs_menu", locale="en", is_department_docs=True)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3  # 2 documents + back button
        # Check that callback data uses download_dept_doc prefix
        assert keyboard.inline_keyboard[0][0].callback_data == "download_dept_doc_1"
        assert keyboard.inline_keyboard[1][0].callback_data == "download_dept_doc_2"


class TestGetArticleDetailKeyboard:
    """Test cases for get_article_detail_keyboard."""

    def test_no_attachments(self):
        """Test keyboard with no attachments."""
        attachments = []
        keyboard = get_article_detail_keyboard(attachments, 1, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1  # Just back button

    def test_single_attachment(self):
        """Test keyboard with single attachment."""
        attachments = [{"id": 1, "name": "document.pdf", "mime_type": "application/pdf"}]
        keyboard = get_article_detail_keyboard(attachments, 1, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Attachment + back button

    def test_multiple_attachments(self):
        """Test keyboard with multiple attachments."""
        attachments = [
            {"id": 1, "name": "doc.pdf", "mime_type": "application/pdf"},
            {"id": 2, "name": "image.png", "mime_type": "image/png"},
            {"id": 3, "name": "sheet.xlsx", "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
        ]
        keyboard = get_article_detail_keyboard(attachments, 1, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 4  # 3 attachments + back button

    def test_attachment_name_truncation(self):
        """Test that long attachment names are truncated."""
        attachments = [{"id": 1, "name": "A" * 100 + ".pdf", "mime_type": "application/pdf"}]
        keyboard = get_article_detail_keyboard(attachments, 1, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        button_text = keyboard.inline_keyboard[0][0].text
        assert len(button_text) < 50


class TestGetFileEmoji:
    """Test cases for _get_file_emoji helper."""

    def test_image_mime_type(self):
        """Test emoji for image files."""
        assert _get_file_emoji("image/png") == "\U0001f5bc\ufe0f"
        assert _get_file_emoji("image/jpeg") == "\U0001f5bc\ufe0f"

    def test_pdf_mime_type(self):
        """Test emoji for PDF files."""
        assert _get_file_emoji("application/pdf") == "\U0001f4d5"

    def test_word_mime_type(self):
        """Test emoji for Word documents."""
        assert _get_file_emoji("application/msword") == "\U0001f4d8"
        assert _get_file_emoji("application/vnd.openxmlformats-officedocument.wordprocessingml.document") == "\U0001f4d8"

    def test_excel_mime_type(self):
        """Test emoji for Excel files."""
        assert _get_file_emoji("application/vnd.ms-excel") == "\U0001f4ca"
        assert _get_file_emoji("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") == "\U0001f4ca"

    def test_unknown_mime_type(self):
        """Test default emoji for unknown mime types."""
        assert _get_file_emoji("application/unknown") == "\U0001f4c4"

    def test_none_mime_type(self):
        """Test default emoji for None mime type."""
        assert _get_file_emoji(None) == "\U0001f4ce"
