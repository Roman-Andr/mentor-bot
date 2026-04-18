"""Unit tests for telegram_bot/handlers/documents.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from telegram_bot.handlers.documents import (
    _format_file_size,
    _get_file_emoji,
    company_policies,
    department_docs,
    documents_menu,
    download_attachment,
    training_materials,
    view_article_detail,
)


class TestDocumentHelpers:
    """Test cases for document helper functions."""

    def test_format_file_size_none(self):
        """Test format file size with None."""
        result = _format_file_size(None)
        assert result == ""

    def test_format_file_size_bytes(self):
        """Test format file size in bytes."""
        result = _format_file_size(500)
        assert result == "500 B"

    def test_format_file_size_kb(self):
        """Test format file size in KB."""
        result = _format_file_size(1024)
        assert result == "1.0 KB"

    def test_format_file_size_mb(self):
        """Test format file size in MB."""
        result = _format_file_size(1024 * 1024)
        assert result == "1.0 MB"

    def test_get_file_emoji_none(self):
        """Test get file emoji with None."""
        result = _get_file_emoji(None)
        assert result == "\U0001f4ce"

    def test_get_file_emoji_image(self):
        """Test get file emoji for image."""
        result = _get_file_emoji("image/jpeg")
        assert result == "\U0001f5bc\ufe0f"

    def test_get_file_emoji_pdf(self):
        """Test get file emoji for PDF."""
        result = _get_file_emoji("application/pdf")
        assert result == "\U0001f4d5"

    def test_get_file_emoji_word(self):
        """Test get file emoji for Word."""
        result = _get_file_emoji("application/msword")
        assert result == "\U0001f4d8"

    def test_get_file_emoji_docx(self):
        """Test get file emoji for DOCX."""
        result = _get_file_emoji(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert result == "\U0001f4d8"

    def test_get_file_emoji_excel(self):
        """Test get file emoji for Excel."""
        result = _get_file_emoji("application/vnd.ms-excel")
        assert result == "\U0001f4ca"

    def test_get_file_emoji_generic(self):
        """Test get file emoji for generic file."""
        result = _get_file_emoji("text/plain")
        assert result == "\U0001f4c4"


class TestDocumentsHandlers:
    """Test cases for document handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        msg = MagicMock(spec=Message)
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "callback_data"
        cb.answer = AsyncMock()
        msg_mock = MagicMock(spec=Message)
        msg_mock.edit_text = AsyncMock()
        msg_mock.answer = AsyncMock()
        cb.message = msg_mock
        return cb

    @pytest.fixture
    def mock_state(self):
        """Create a mock FSM state."""
        state = MagicMock(spec=FSMContext)
        state.clear = AsyncMock()
        return state

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        return {"id": 1, "first_name": "John", "department": "Engineering"}

    @pytest.fixture
    def mock_user_no_dept(self):
        """Create a mock user without department."""
        return {"id": 1, "first_name": "John"}

    @pytest.fixture
    def mock_auth_token(self):
        """Create a mock auth token."""
        return "test_auth_token_123"

    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot."""
        bot = MagicMock(spec=Bot)
        bot.send_document = AsyncMock()
        return bot

    # Tests for documents_menu
    async def test_documents_menu_callback(self, mock_callback, mock_state, mock_user):
        """Test documents menu via callback."""
        with patch(
            "telegram_bot.handlers.documents.get_documents_menu_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await documents_menu(mock_callback, mock_state, mock_user, locale="en")

        mock_state.clear.assert_called_once()
        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_documents_menu_message(self, mock_message, mock_state, mock_user):
        """Test documents menu via message."""
        with patch(
            "telegram_bot.handlers.documents.get_documents_menu_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await documents_menu(mock_message, mock_state, mock_user, locale="en")

        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called_once()

    async def test_documents_menu_no_user(self, mock_message, mock_state):
        """Test documents menu with no user."""
        await documents_menu(mock_message, mock_state, None, locale="en")

        mock_message.answer.assert_called_once()

    async def test_documents_menu_no_message(self, mock_callback, mock_state, mock_user):
        """Test documents menu with no message."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "documents_menu"
        cb.answer = AsyncMock()  # Need this for the first await in the handler
        cb.message = None

        result = await documents_menu(cb, mock_state, mock_user, locale="en")
        assert result is None

    # Tests for department_docs
    async def test_department_docs_success(self, mock_callback, mock_user, mock_auth_token):
        """Test department docs with data."""
        mock_docs = [
            {"id": 1, "title": "Doc 1"},
            {"id": 2, "title": "Doc 2"},
        ]

        with patch(
            "telegram_bot.handlers.documents.document_client.get_department_documents",
            new_callable=AsyncMock,
            return_value=mock_docs,
        ):
            with patch(
                "telegram_bot.handlers.documents.get_article_list_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await department_docs(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_department_docs_empty(self, mock_callback, mock_user, mock_auth_token):
        """Test department docs with no data."""
        with patch(
            "telegram_bot.handlers.documents.document_client.get_department_documents",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with patch(
                "telegram_bot.handlers.documents.get_article_list_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await department_docs(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_department_docs_no_user(self, mock_callback, mock_auth_token):
        """Test department docs with no user."""
        await department_docs(mock_callback, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_department_docs_no_auth(self, mock_callback, mock_user):
        """Test department docs with no auth token."""
        await department_docs(mock_callback, mock_user, None, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_department_docs_no_department(self, mock_callback, mock_user_no_dept, mock_auth_token):
        """Test department docs with no department."""
        await department_docs(mock_callback, mock_user_no_dept, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_department_docs_no_message(self, mock_callback, mock_user, mock_auth_token):
        """Test department docs with no message."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "dept_docs"
        cb.answer = AsyncMock()
        cb.message = None

        result = await department_docs(cb, mock_user, mock_auth_token, locale="en")
        assert result is None

    # Tests for company_policies
    async def test_company_policies_success(self, mock_callback, mock_user, mock_auth_token):
        """Test company policies with data."""
        mock_policies = [
            {"id": 1, "title": "Policy 1"},
            {"id": 2, "title": "Policy 2"},
        ]

        with patch(
            "telegram_bot.handlers.documents.document_client.get_company_policies",
            new_callable=AsyncMock,
            return_value=mock_policies,
        ):
            with patch(
                "telegram_bot.handlers.documents.get_article_list_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await company_policies(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_company_policies_empty(self, mock_callback, mock_user, mock_auth_token):
        """Test company policies with no data."""
        with patch(
            "telegram_bot.handlers.documents.document_client.get_company_policies",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with patch(
                "telegram_bot.handlers.documents.get_article_list_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await company_policies(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_company_policies_no_user(self, mock_callback, mock_auth_token):
        """Test company policies with no user."""
        await company_policies(mock_callback, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_company_policies_no_auth(self, mock_callback, mock_user):
        """Test company policies with no auth token."""
        await company_policies(mock_callback, mock_user, None, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_company_policies_no_message(self, mock_callback, mock_user, mock_auth_token):
        """Test company policies with no message (lines 143-144)."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "company_policies"
        cb.answer = AsyncMock()
        cb.message = None

        result = await company_policies(cb, mock_user, mock_auth_token, locale="en")
        assert result is None
        cb.answer.assert_called_once()

    async def test_company_policies_message_not_message_instance(self, mock_callback, mock_user, mock_auth_token):
        """Test company policies when message is not a Message instance (lines 143-144)."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "company_policies"
        cb.answer = AsyncMock()
        cb.message = "not a message object"  # Not a Message instance

        result = await company_policies(cb, mock_user, mock_auth_token, locale="en")
        assert result is None
        cb.answer.assert_called_once()

    # Tests for training_materials
    async def test_training_materials_success(self, mock_callback, mock_user, mock_auth_token):
        """Test training materials with data."""
        mock_materials = [
            {"id": 1, "title": "Material 1"},
            {"id": 2, "title": "Material 2"},
        ]

        with patch(
            "telegram_bot.handlers.documents.document_client.get_training_materials",
            new_callable=AsyncMock,
            return_value=mock_materials,
        ):
            with patch(
                "telegram_bot.handlers.documents.get_article_list_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await training_materials(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_training_materials_empty(self, mock_callback, mock_user, mock_auth_token):
        """Test training materials with no data."""
        with patch(
            "telegram_bot.handlers.documents.document_client.get_training_materials",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with patch(
                "telegram_bot.handlers.documents.get_article_list_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await training_materials(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_training_materials_no_user(self, mock_callback, mock_auth_token):
        """Test training materials with no user."""
        await training_materials(mock_callback, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_training_materials_no_message(self, mock_callback, mock_user, mock_auth_token):
        """Test training materials with no message (lines 176-177)."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "training_materials"
        cb.answer = AsyncMock()
        cb.message = None

        result = await training_materials(cb, mock_user, mock_auth_token, locale="en")
        assert result is None
        cb.answer.assert_called_once()

    async def test_training_materials_message_not_message_instance(self, mock_callback, mock_user, mock_auth_token):
        """Test training materials when message is not a Message instance (lines 176-177)."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "training_materials"
        cb.answer = AsyncMock()
        cb.message = "not a message object"  # Not a Message instance

        result = await training_materials(cb, mock_user, mock_auth_token, locale="en")
        assert result is None
        cb.answer.assert_called_once()

    # Tests for view_article_detail
    async def test_view_article_detail_success(self, mock_callback, mock_user, mock_auth_token):
        """Test view article detail with data."""
        mock_callback.data = "view_article_123"
        mock_article = {
            "id": 123,
            "title": "Test Article",
            "content": "This is a test article with lots of content...",
            "excerpt": "Short excerpt",
            "attachments": [
                {"id": 1, "name": "file.pdf", "mime_type": "application/pdf", "file_size": 1024},
            ],
        }

        with patch(
            "telegram_bot.handlers.documents.knowledge_client.get_article_details",
            new_callable=AsyncMock,
            return_value=mock_article,
        ):
            with patch(
                "telegram_bot.handlers.documents.get_article_detail_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await view_article_detail(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_view_article_detail_no_excerpt(self, mock_callback, mock_user, mock_auth_token):
        """Test view article detail with content but no excerpt."""
        mock_callback.data = "view_article_123"
        mock_article = {
            "id": 123,
            "title": "Test Article",
            "content": "This is a test article.",
            "excerpt": None,
            "attachments": [],
        }

        with patch(
            "telegram_bot.handlers.documents.knowledge_client.get_article_details",
            new_callable=AsyncMock,
            return_value=mock_article,
        ):
            with patch(
                "telegram_bot.handlers.documents.get_article_detail_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await view_article_detail(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_view_article_detail_long_content(self, mock_callback, mock_user, mock_auth_token):
        """Test view article detail with long content."""
        mock_callback.data = "view_article_123"
        mock_article = {
            "id": 123,
            "title": "Test Article",
            "content": "A" * 500,  # Long content
            "excerpt": None,
            "attachments": [],
        }

        with patch(
            "telegram_bot.handlers.documents.knowledge_client.get_article_details",
            new_callable=AsyncMock,
            return_value=mock_article,
        ):
            with patch(
                "telegram_bot.handlers.documents.get_article_detail_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await view_article_detail(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_view_article_detail_not_found(self, mock_callback, mock_user, mock_auth_token):
        """Test view article detail when article not found."""
        mock_callback.data = "view_article_999"

        with patch(
            "telegram_bot.handlers.documents.knowledge_client.get_article_details",
            new_callable=AsyncMock,
            return_value=None,
        ):
            await view_article_detail(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_view_article_detail_invalid_id(self, mock_callback, mock_user, mock_auth_token):
        """Test view article detail with invalid ID."""
        mock_callback.data = "view_article_invalid"

        await view_article_detail(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_view_article_detail_no_user(self, mock_callback, mock_auth_token):
        """Test view article detail with no user."""
        mock_callback.data = "view_article_123"

        await view_article_detail(mock_callback, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_view_article_detail_no_message(self, mock_callback, mock_user, mock_auth_token):
        """Test view article detail with no message."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "view_article_123"
        cb.answer = AsyncMock()
        cb.message = None

        result = await view_article_detail(cb, mock_user, mock_auth_token, locale="en")
        assert result is None

    # Tests for download_attachment
    async def test_download_attachment_success(self, mock_callback, mock_user, mock_auth_token, mock_bot):
        """Test download attachment success."""
        mock_callback.data = "download_att_1_123"
        mock_callback.message.chat = MagicMock()
        mock_callback.message.chat.id = 123456
        mock_attachments = [
            {"id": 1, "name": "document.pdf"},
        ]

        with patch(
            "telegram_bot.handlers.documents.knowledge_client.get_article_attachments",
            new_callable=AsyncMock,
            return_value=mock_attachments,
        ):
            with patch(
                "telegram_bot.handlers.documents.knowledge_client.download_attachment",
                new_callable=AsyncMock,
                return_value=b"pdf content",
            ):
                await download_attachment(
                    mock_callback, mock_bot, mock_user, mock_auth_token, locale="en"
                )

        mock_bot.send_document.assert_called_once()

    async def test_download_attachment_attachment_not_found(self, mock_callback, mock_user, mock_auth_token, mock_bot):
        """Test download attachment when attachment not found."""
        mock_callback.data = "download_att_999_123"

        with patch(
            "telegram_bot.handlers.documents.knowledge_client.get_article_attachments",
            new_callable=AsyncMock,
            return_value=[],
        ):
            await download_attachment(
                mock_callback, mock_bot, mock_user, mock_auth_token, locale="en"
            )

        # Answer is called twice: once for loading, once for error
        assert mock_callback.answer.call_count == 2
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_download_attachment_no_content(self, mock_callback, mock_user, mock_auth_token, mock_bot):
        """Test download attachment when download fails."""
        mock_callback.data = "download_att_1_123"
        mock_attachments = [
            {"id": 1, "name": "document.pdf"},
        ]

        with patch(
            "telegram_bot.handlers.documents.knowledge_client.get_article_attachments",
            new_callable=AsyncMock,
            return_value=mock_attachments,
        ):
            with patch(
                "telegram_bot.handlers.documents.knowledge_client.download_attachment",
                new_callable=AsyncMock,
                return_value=None,
            ):
                await download_attachment(
                    mock_callback, mock_bot, mock_user, mock_auth_token, locale="en"
                )

        # Answer is called twice: once for loading, once for error
        assert mock_callback.answer.call_count == 2
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_download_attachment_send_fails(self, mock_callback, mock_user, mock_auth_token, mock_bot):
        """Test download attachment when send fails."""
        mock_callback.data = "download_att_1_123"
        mock_callback.message.chat = MagicMock()
        mock_callback.message.chat.id = 123456
        mock_attachments = [
            {"id": 1, "name": "document.pdf"},
        ]

        mock_bot.send_document = AsyncMock(side_effect=Exception("Send failed"))

        with patch(
            "telegram_bot.handlers.documents.knowledge_client.get_article_attachments",
            new_callable=AsyncMock,
            return_value=mock_attachments,
        ):
            with patch(
                "telegram_bot.handlers.documents.knowledge_client.download_attachment",
                new_callable=AsyncMock,
                return_value=b"pdf content",
            ):
                with patch("telegram_bot.handlers.documents.logger"):
                    await download_attachment(
                        mock_callback, mock_bot, mock_user, mock_auth_token, locale="en"
                    )

        # Answer is called twice: once for loading, once for error
        assert mock_callback.answer.call_count == 2
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_download_attachment_no_user(self, mock_callback, mock_bot, mock_auth_token):
        """Test download attachment with no user."""
        mock_callback.data = "download_att_1_123"

        await download_attachment(mock_callback, mock_bot, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_download_attachment_no_message(self, mock_callback, mock_user, mock_auth_token, mock_bot):
        """Test download attachment with no message."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.data = "download_att_1_123"
        cb.answer = AsyncMock()
        cb.message = None

        result = await download_attachment(cb, mock_bot, mock_user, mock_auth_token, locale="en")
        assert result is None

    async def test_download_attachment_invalid_data(self, mock_callback, mock_user, mock_auth_token, mock_bot):
        """Test download attachment with invalid callback data."""
        mock_callback.data = "download_att_invalid"

        await download_attachment(
            mock_callback, mock_bot, mock_user, mock_auth_token, locale="en"
        )

        mock_callback.answer.assert_called_once()
