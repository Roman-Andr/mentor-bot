"""Unit tests for telegram_bot/handlers/knowledge_base.py."""

from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, Message

from telegram_bot.handlers.knowledge_base import (
    _format_file_size,
    _get_knowledge_base_menu,
    _get_user_from_callback,
    admin_knowledge_menu,
    back_to_search_results,
    cancel_article_create,
    cancel_file_upload,
    category_pagination_nop,
    download_kb_attachment,
    faq_empty_callback,
    handle_search_pagination,
    kb_categories,
    kb_category_articles,
    kb_category_pagination,
    knowledge_base_menu,
    navigate_faq_step,
    process_article_content,
    process_article_file,
    process_article_title,
    process_search_query,
    process_upload_article_id,
    process_upload_file,
    save_article,
    save_uploaded_files,
    search_pagination_nop,
    show_faq,
    start_article_create,
    start_file_upload,
    start_search,
    view_category_article,
    view_faq_scenario,
    view_search_result,
)
from telegram_bot.states.auth_states import ArticleCreateStates, FileUploadStates, SearchStates


class TestKnowledgeBaseMenu:
    """Test cases for knowledge_base_menu handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()

        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.clear = AsyncMock()

    async def test_knowledge_base_menu_callback(self):
        """Test knowledge base menu via callback."""
        with patch("telegram_bot.handlers.knowledge_base.get_knowledge_base_menu_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await knowledge_base_menu(self.mock_callback, self.mock_state, locale="en")

            self.mock_state.clear.assert_called_once()
            self.mock_callback.message.edit_text.assert_called_once()

    async def test_knowledge_base_menu_message(self):
        """Test knowledge base menu via message."""
        with patch("telegram_bot.handlers.knowledge_base.get_knowledge_base_menu_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await knowledge_base_menu(self.mock_message, self.mock_state, locale="en")

            self.mock_state.clear.assert_called_once()
            self.mock_message.answer.assert_called_once()

    async def test_knowledge_base_menu_callback_no_message(self):
        """Test knowledge base menu via callback with no message."""
        self.mock_callback.message = None

        await knowledge_base_menu(self.mock_callback, self.mock_state, locale="en")

        # Should return early without error
        self.mock_state.clear.assert_called_once()


class TestStartSearch:
    """Test cases for start_search handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.set_state = AsyncMock()
        self.mock_state.update_data = AsyncMock()

    async def test_start_search(self):
        """Test start search."""
        await start_search(self.mock_callback, self.mock_state, locale="en")

        self.mock_callback.message.edit_text.assert_called_once()
        self.mock_state.set_state.assert_called_once_with(SearchStates.waiting_for_query)
        self.mock_state.update_data.assert_called_once()
        self.mock_callback.answer.assert_called_once()

    async def test_start_search_no_message(self):
        """Test start search with no message."""
        self.mock_callback.message = None

        await start_search(self.mock_callback, self.mock_state, locale="en")

        self.mock_state.set_state.assert_called_once()


class TestProcessSearchQuery:
    """Test cases for process_search_query handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()
        self.mock_message.text = "search query"
        self.mock_message.from_user = MagicMock()
        self.mock_message.from_user.id = 123456

        self.mock_state = MagicMock()
        self.mock_state.clear = AsyncMock()

        self.mock_user = {"id": 1, "first_name": "John"}
        self.auth_token = "test_token_123"  # noqa: S105

    async def test_process_search_query_too_short(self):
        """Test search query too short."""
        self.mock_message.text = "ab"

        await process_search_query(self.mock_message, self.mock_state, self.mock_user, self.auth_token, locale="en")

        self.mock_message.answer.assert_called_once()

    async def test_process_search_query_no_auth(self):
        """Test search query without auth."""
        await process_search_query(self.mock_message, self.mock_state, self.mock_user, None, locale="en")

        self.mock_message.answer.assert_called_once()

    async def test_process_search_query_no_results(self):
        """Test search query with no results."""
        mock_results = MagicMock()
        mock_results.results = []

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.search_articles",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = mock_results
            with patch(
                "telegram_bot.handlers.knowledge_base.get_search_no_results_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await process_search_query(
                    self.mock_message, self.mock_state, self.mock_user, self.auth_token, locale="en"
                )

                self.mock_state.clear.assert_called_once()

    async def test_process_search_query_success(self):
        """Test search query success."""
        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.title = "Test Article"
        mock_result.excerpt = "Summary"
        mock_result.highlighted_content = "Content"
        mock_result.category_name = "General"
        mock_result.relevance_score = 0.95

        mock_results = MagicMock()
        mock_results.results = [mock_result]
        mock_results.page = 1
        mock_results.pages = 1

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.search_articles",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = mock_results
            with patch("telegram_bot.handlers.knowledge_base.cache.set", new_callable=AsyncMock):
                with patch(
                    "telegram_bot.handlers.knowledge_base.format_search_results",
                    return_value="Search results",
                ):
                    with patch(
                        "telegram_bot.handlers.knowledge_base.get_search_results_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value.as_markup.return_value = MagicMock()

                        await process_search_query(
                            self.mock_message, self.mock_state, self.mock_user, self.auth_token, locale="en"
                        )

                        self.mock_message.answer.assert_called_once()


class TestHandleSearchPagination:
    """Test cases for handle_search_pagination handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "kb_search_page_2_search_query"
        # Use spec=Message for isinstance checks
        self.mock_callback.message = MagicMock(spec=Message)
        self.mock_callback.message.edit_text = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_handle_search_pagination_no_auth(self):
        """Test pagination without auth."""
        await handle_search_pagination(self.mock_callback, None, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_handle_search_pagination_no_message(self):
        """Test pagination when callback.message is None."""
        self.mock_callback.message = None

        await handle_search_pagination(self.mock_callback, None, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_handle_search_pagination_invalid_data(self):
        """Test pagination with invalid data."""
        self.mock_callback.data = "kb_search_page_invalid"

        await handle_search_pagination(self.mock_callback, None, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_handle_search_pagination_no_results(self):
        """Test pagination with no results."""
        mock_results = MagicMock()
        mock_results.results = []

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.search_articles",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = mock_results
            with patch(
                "telegram_bot.handlers.knowledge_base.get_search_no_results_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await handle_search_pagination(
                    self.mock_callback, None, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()

    async def test_handle_search_pagination_success(self):
        """Test pagination success."""
        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.title = "Test"
        mock_result.excerpt = "Summary"
        mock_result.highlighted_content = "Content"
        mock_result.category_name = "General"
        mock_result.relevance_score = 0.9

        mock_results = MagicMock()
        mock_results.results = [mock_result]
        mock_results.page = 2
        mock_results.pages = 3

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.search_articles",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = mock_results
            with patch("telegram_bot.handlers.knowledge_base.cache.set", new_callable=AsyncMock):
                with patch(
                    "telegram_bot.handlers.knowledge_base.format_search_results",
                    return_value="Results",
                ):
                    with patch(
                        "telegram_bot.handlers.knowledge_base.get_search_results_keyboard"
                    ) as mock_kb:
                        mock_kb.return_value.as_markup.return_value = MagicMock()

                        await handle_search_pagination(
                            self.mock_callback, None, self.auth_token, locale="en"
                        )

                        self.mock_callback.message.edit_text.assert_called_once()


class TestSearchPaginationNop:
    """Test cases for search_pagination_nop handler."""

    async def test_search_pagination_nop(self):
        """Test search pagination no-op."""
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.answer = AsyncMock()

        await search_pagination_nop(mock_callback)

        mock_callback.answer.assert_called_once()


class TestBackToSearchResults:
    """Test cases for back_to_search_results handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "kb_back_to_search_1"
        # Use spec=Message for isinstance checks
        self.mock_callback.message = MagicMock(spec=Message)
        self.mock_callback.message.edit_text = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_back_to_search_no_auth(self):
        """Test back to search without auth."""
        await back_to_search_results(self.mock_callback, None, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_back_to_search_no_message(self):
        """Test back to search when callback.message is None."""
        self.mock_callback.message = None

        await back_to_search_results(self.mock_callback, None, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_back_to_search_no_cache(self):
        """Test back to search with no cache data."""
        with patch("telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = None
            with patch("telegram_bot.handlers.knowledge_base.get_knowledge_base_menu_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await back_to_search_results(self.mock_callback, None, self.auth_token, locale="en")

                self.mock_callback.message.edit_text.assert_called_once()

    async def test_back_to_search_page_parse_error(self):
        """Test back to search when page parsing raises ValueError."""
        self.mock_callback.data = "kb_back_to_search_invalid"  # Invalid page number

        with patch("telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = {
                "results": [{"id": 1, "title": "Test"}],
                "query": "test",
            }
            with patch(
                "telegram_bot.handlers.knowledge_base.knowledge_client.search_articles",
                new_callable=AsyncMock,
            ) as mock_search:
                mock_results = MagicMock()
                mock_results.results = [
                    MagicMock(
                        id=1, title="Test", excerpt="Summary",
                        highlighted_content="Content", category_name="General", relevance_score=0.9
                    )
                ]
                mock_results.page = 1
                mock_results.pages = 1
                mock_search.return_value = mock_results
                with patch("telegram_bot.handlers.knowledge_base.cache.set", new_callable=AsyncMock):
                    with patch(
                        "telegram_bot.handlers.knowledge_base.format_search_results",
                        return_value="Results",
                    ):
                        with patch(
                            "telegram_bot.handlers.knowledge_base.get_search_results_keyboard"
                        ) as mock_kb:
                            mock_kb.return_value.as_markup.return_value = MagicMock()

                            await back_to_search_results(
                                self.mock_callback, None, self.auth_token, locale="en"
                            )

                            # Should use default page=1 when parse fails
                            self.mock_callback.message.edit_text.assert_called_once()

    async def test_back_to_search_no_query(self):
        """Test back to search with no query in cache."""
        with patch("telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = {"results": [], "query": ""}
            with patch("telegram_bot.handlers.knowledge_base.get_knowledge_base_menu_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await back_to_search_results(self.mock_callback, None, self.auth_token, locale="en")

                self.mock_callback.message.edit_text.assert_called_once()

    async def test_back_to_search_no_results(self):
        """Test back to search when search returns no results."""
        mock_results = MagicMock()
        mock_results.results = []

        with patch(
            "telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock
        ) as mock_cache:
            mock_cache.return_value = {
                "results": [{"id": 1, "title": "Test"}],
                "query": "test",
                "page": 1,
            }
            with patch(
                "telegram_bot.handlers.knowledge_base.knowledge_client.search_articles",
                new_callable=AsyncMock,
            ) as mock_search:
                mock_search.return_value = mock_results
                with patch(
                    "telegram_bot.handlers.knowledge_base.get_search_no_results_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await back_to_search_results(
                        self.mock_callback, None, self.auth_token, locale="en"
                    )

                    self.mock_callback.message.edit_text.assert_called_once()

    async def test_back_to_search_success(self):
        """Test back to search success."""
        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.title = "Test"
        mock_result.excerpt = "Summary"
        mock_result.highlighted_content = "Content"
        mock_result.category_name = "General"
        mock_result.relevance_score = 0.9

        mock_results = MagicMock()
        mock_results.results = [mock_result]
        mock_results.page = 1
        mock_results.pages = 1

        with patch(
            "telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock
        ) as mock_cache:
            mock_cache.return_value = {
                "results": [{"id": 1, "title": "Test"}],
                "query": "test",
                "page": 1,
            }
            with patch(
                "telegram_bot.handlers.knowledge_base.knowledge_client.search_articles",
                new_callable=AsyncMock,
            ) as mock_search:
                mock_search.return_value = mock_results
                with patch("telegram_bot.handlers.knowledge_base.cache.set", new_callable=AsyncMock):
                    with patch(
                        "telegram_bot.handlers.knowledge_base.format_search_results",
                        return_value="Results",
                    ):
                        with patch(
                            "telegram_bot.handlers.knowledge_base.get_search_results_keyboard"
                        ) as mock_kb:
                            mock_kb.return_value.as_markup.return_value = MagicMock()

                            await back_to_search_results(
                                self.mock_callback, None, self.auth_token, locale="en"
                            )

                            self.mock_callback.message.edit_text.assert_called_once()


class TestViewSearchResult:
    """Test cases for view_search_result handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        self.mock_callback.data = "kb_view_0_1"
        # Use spec=Message for isinstance checks
        self.mock_callback.message = MagicMock(spec=Message)
        self.mock_callback.message.edit_text = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_view_search_result_no_auth(self):
        """Test view result without auth."""
        await view_search_result(self.mock_callback, None, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_view_search_result_no_message(self):
        """Test view result when callback.message is None."""
        self.mock_callback.message = None

        await view_search_result(self.mock_callback, None, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_view_search_result_invalid_data(self):
        """Test view result with invalid data."""
        self.mock_callback.data = "kb_view_invalid"

        await view_search_result(self.mock_callback, None, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_view_search_result_no_cache(self):
        """Test view result with no cache."""
        with patch("telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = None

            await view_search_result(self.mock_callback, None, self.auth_token, locale="en")

            self.mock_callback.answer.assert_called_once()

    async def test_view_search_result_index_out_of_range(self):
        """Test view result with index out of range."""
        self.mock_callback.data = "kb_view_5_1"  # idx 5, but only 1 result

        with patch("telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = {"results": [{"id": 1}]}  # Only 1 result at idx 0

            await view_search_result(self.mock_callback, None, self.auth_token, locale="en")

            self.mock_callback.answer.assert_called_once()

    async def test_view_search_result_article_not_found(self):
        """Test view result when article not found."""
        with patch(
            "telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock
        ) as mock_cache:
            mock_cache.return_value = {"results": [{"id": 1}]}
            with patch(
                "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_details",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = None

                await view_search_result(
                    self.mock_callback, None, self.auth_token, locale="en"
                )

                self.mock_callback.answer.assert_called_once()

    async def test_view_search_result_with_content_preview(self):
        """Test view result with content preview (no excerpt)."""
        article = {
            "id": 1,
            "title": "Test Article",
            "content": "A" * 1000,  # Long content to trigger preview
            "excerpt": "",  # Empty excerpt triggers content preview
            "attachments": []
        }

        with patch(
            "telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock
        ) as mock_cache:
            mock_cache.return_value = {"results": [{"id": 1}]}
            with patch(
                "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_details",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = article
                with patch(
                    "telegram_bot.handlers.knowledge_base.get_article_view_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await view_search_result(
                        self.mock_callback, None, self.auth_token, locale="en"
                    )

                    self.mock_callback.message.edit_text.assert_called_once()
                    # Check that the preview with "..." was generated
                    call_args = self.mock_callback.message.edit_text.call_args
                    assert "..." in call_args[0][0]

    async def test_view_search_result_success(self):
        """Test view result success."""
        article = {
            "id": 1,
            "title": "Test Article",
            "content": "Content",
            "excerpt": "Excerpt",
            "attachments": [{"id": 1, "name": "file.pdf", "file_size": 1024}]
        }

        with patch(
            "telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock
        ) as mock_cache:
            mock_cache.return_value = {"results": [{"id": 1}]}
            with patch(
                "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_details",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = article
                with patch(
                    "telegram_bot.handlers.knowledge_base.get_article_view_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await view_search_result(
                        self.mock_callback, None, self.auth_token, locale="en"
                    )

                    self.mock_callback.message.edit_text.assert_called_once()


class TestDownloadKbAttachment:
    """Test cases for download_kb_attachment handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.data = "kb_dl_1_1"
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.chat = MagicMock()
        self.mock_callback.message.chat.id = 123456

        self.mock_bot = MagicMock()
        self.mock_bot.send_document = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_download_kb_attachment_no_auth(self):
        """Test download without auth."""
        await download_kb_attachment(self.mock_callback, self.mock_bot, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_download_kb_attachment_invalid_data(self):
        """Test download with invalid data."""
        self.mock_callback.data = "kb_dl_invalid"

        await download_kb_attachment(self.mock_callback, self.mock_bot, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_download_kb_attachment_no_message(self):
        """Test download with no message."""
        self.mock_callback.message = None

        await download_kb_attachment(self.mock_callback, self.mock_bot, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_download_kb_attachment_not_found(self):
        """Test download when attachment not found."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_attachments",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 999, "name": "other.pdf"}]

            await download_kb_attachment(
                self.mock_callback, self.mock_bot, self.auth_token, locale="en"
            )

            # Handler calls answer() for loading, then for error alert
            assert self.mock_callback.answer.call_count >= 1

    async def test_download_kb_attachment_download_failed(self):
        """Test download when download fails."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_attachments",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "name": "file.pdf"}]
            with patch(
                "telegram_bot.handlers.knowledge_base.knowledge_client.download_attachment",
                new_callable=AsyncMock,
            ) as mock_dl:
                mock_dl.return_value = None

                await download_kb_attachment(
                    self.mock_callback, self.mock_bot, self.auth_token, locale="en"
                )

                # Handler calls answer() for loading, then for error alert
                assert self.mock_callback.answer.call_count >= 1

    async def test_download_kb_attachment_send_exception(self):
        """Test download when sending document raises exception."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_attachments",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "name": "file.pdf"}]
            with patch(
                "telegram_bot.handlers.knowledge_base.knowledge_client.download_attachment",
                new_callable=AsyncMock,
            ) as mock_dl:
                mock_dl.return_value = b"file content"
                self.mock_bot.send_document = AsyncMock(side_effect=Exception("Send failed"))

                await download_kb_attachment(
                    self.mock_callback, self.mock_bot, self.auth_token, locale="en"
                )

                # Should answer with error when exception occurs
                assert self.mock_callback.answer.call_count >= 1

    async def test_download_kb_attachment_success(self):
        """Test download success."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_attachments",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "name": "file.pdf"}]
            with patch(
                "telegram_bot.handlers.knowledge_base.knowledge_client.download_attachment",
                new_callable=AsyncMock,
            ) as mock_dl:
                mock_dl.return_value = b"file content"

                await download_kb_attachment(
                    self.mock_callback, self.mock_bot, self.auth_token, locale="en"
                )

                self.mock_bot.send_document.assert_called_once()


class TestKbCategories:
    """Test cases for kb_categories handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        # Use spec=Message for isinstance checks
        self.mock_callback.message = MagicMock(spec=Message)
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.clear = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_kb_categories_no_auth(self):
        """Test categories without auth."""
        await kb_categories(self.mock_callback, self.mock_state, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_kb_categories_success_with_data(self):
        """Test categories with data."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_categories",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = {
                "categories": [
                    {"id": 1, "name": "General"},
                    {"id": 2, "name": "Technical"},
                ]
            }
            with patch(
                "telegram_bot.handlers.knowledge_base.get_kb_categories_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await kb_categories(
                    self.mock_callback, self.mock_state, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()

    async def test_kb_categories_success_empty(self):
        """Test categories with no data."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_categories",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = {"categories": []}
            with patch(
                "telegram_bot.handlers.knowledge_base.get_kb_categories_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await kb_categories(
                    self.mock_callback, self.mock_state, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()

    async def test_kb_categories_no_message(self):
        """Test categories with no message - handler returns early."""
        self.mock_callback.message = None

        await kb_categories(self.mock_callback, self.mock_state, self.auth_token, locale="en")

        # When message is None, handler returns early without calling state.clear
        # because isinstance check fails before state.clear is reached


class TestKbCategoryArticles:
    """Test cases for kb_category_articles handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.clear = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_kb_category_articles_no_auth(self):
        """Test category articles without auth."""
        self.mock_callback.data = "kb_cat_1"

        await kb_category_articles(self.mock_callback, self.mock_state, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_kb_category_articles_no_message(self):
        """Test category articles when callback.message is None."""
        self.mock_callback.data = "kb_cat_1"
        self.mock_callback.message = None

        await kb_category_articles(self.mock_callback, self.mock_state, self.auth_token, locale="en")
        # Should return early without calling state.clear
        self.mock_state.clear.assert_not_called()

    async def test_kb_category_articles_invalid_data(self):
        """Test category articles with invalid data."""
        self.mock_callback.data = "kb_cat_invalid"

        await kb_category_articles(self.mock_callback, self.mock_state, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_kb_category_articles_success(self):
        """Test category articles success."""
        self.mock_callback.data = "kb_cat_1_page_1"

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_articles_by_category",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = {
                "articles": [
                    {"id": 1, "title": "Article 1"},
                    {"id": 2, "title": "Article 2"},
                ],
                "pages": 1,
            }
            with patch(
                "telegram_bot.handlers.knowledge_base.get_kb_category_articles_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await kb_category_articles(
                    self.mock_callback, self.mock_state, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()

    async def test_kb_category_articles_empty(self):
        """Test category articles empty."""
        self.mock_callback.data = "kb_cat_1"

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_articles_by_category",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = {"articles": [], "pages": 1}
            with patch(
                "telegram_bot.handlers.knowledge_base.get_kb_category_articles_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await kb_category_articles(
                    self.mock_callback, self.mock_state, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()


class TestCategoryPaginationNop:
    """Test cases for category_pagination_nop handler."""

    async def test_category_pagination_nop(self):
        """Test category pagination no-op."""
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.answer = AsyncMock()

        await category_pagination_nop(mock_callback)

        mock_callback.answer.assert_called_once()


class TestKbCategoryPagination:
    """Test cases for kb_category_pagination handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_kb_category_pagination_no_auth(self):
        """Test pagination without auth."""
        self.mock_callback.data = "kb_cat_page_1_2"

        await kb_category_pagination(self.mock_callback, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_kb_category_pagination_no_message(self):
        """Test pagination when callback.message is None."""
        self.mock_callback.data = "kb_cat_page_1_2"
        self.mock_callback.message = None

        await kb_category_pagination(self.mock_callback, self.auth_token, locale="en")
        # Should return early without calling answer

    async def test_kb_category_pagination_invalid_data(self):
        """Test pagination with invalid data."""
        self.mock_callback.data = "kb_cat_page_invalid"

        await kb_category_pagination(self.mock_callback, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_kb_category_pagination_empty_articles(self):
        """Test pagination with empty articles list."""
        self.mock_callback.data = "kb_cat_page_1_2"

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_articles_by_category",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = {
                "articles": [],
                "pages": 1,
            }
            with patch(
                "telegram_bot.handlers.knowledge_base.get_kb_category_articles_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await kb_category_pagination(
                    self.mock_callback, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()

    async def test_kb_category_pagination_success(self):
        """Test pagination success."""
        self.mock_callback.data = "kb_cat_page_1_2"

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_articles_by_category",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = {
                "articles": [{"id": 1, "title": "Article 1"}],
                "pages": 2,
            }
            with patch(
                "telegram_bot.handlers.knowledge_base.get_kb_category_articles_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await kb_category_pagination(
                    self.mock_callback, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()


class TestViewCategoryArticle:
    """Test cases for view_category_article handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.from_user = MagicMock()
        self.mock_callback.from_user.id = 123456
        # Use spec=Message for isinstance checks
        self.mock_callback.message = MagicMock(spec=Message)
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.clear = AsyncMock()

        self.mock_user = {"id": 1}
        self.auth_token = "test_token_123"  # noqa: S105

    async def test_view_category_article_no_message(self):
        """Test view article with no message."""
        self.mock_callback.message = None

        await view_category_article(self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en")
        self.mock_state.clear.assert_not_called()

    async def test_view_category_article_no_auth(self):
        """Test view article without auth."""
        self.mock_callback.data = "kb_cat_article_1_1_1"

        await view_category_article(self.mock_callback, self.mock_state, self.mock_user, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_view_category_article_invalid_data(self):
        """Test view article with invalid data."""
        self.mock_callback.data = "kb_cat_article_invalid"

        await view_category_article(
            self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
        )
        self.mock_callback.answer.assert_called_once()

    async def test_view_category_article_not_found(self):
        """Test view article when not found."""
        self.mock_callback.data = "kb_cat_article_1_1_1"

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_details",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            await view_category_article(
                self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
            )

            self.mock_callback.answer.assert_called_once()

    async def test_view_category_article_content_preview(self):
        """Test view article with content preview (no excerpt)."""
        self.mock_callback.data = "kb_cat_article_1_1_1"

        article = {
            "id": 1,
            "title": "Test Article",
            "content": "A" * 1000,  # Long content to trigger preview
            "excerpt": "",  # Empty excerpt triggers content preview
            "attachments": []
        }

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_details",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = article
            with patch(
                "telegram_bot.handlers.knowledge_base.get_kb_category_article_view_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await view_category_article(
                    self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()
                # Check that the preview with "..." was generated
                call_args = self.mock_callback.message.edit_text.call_args
                assert "..." in call_args[0][0]

    async def test_view_category_article_success(self):
        """Test view article success."""
        self.mock_callback.data = "kb_cat_article_1_1_1"

        article = {
            "id": 1,
            "title": "Test Article",
            "content": "Content",
            "excerpt": "Excerpt",
            "attachments": [{"id": 1, "name": "file.pdf", "file_size": 1024}]
        }

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_details",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = article
            with patch(
                "telegram_bot.handlers.knowledge_base.get_kb_category_article_view_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await view_category_article(
                    self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()


class TestShowFaq:
    """Test cases for show_faq handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        # Use spec=Message for isinstance checks
        self.mock_callback.message = MagicMock(spec=Message)
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()

    async def test_show_faq_success(self):
        """Test show FAQ success."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_active_scenarios",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = {
                "scenarios": [
                    {"id": 1, "title": "Getting Started"},
                    {"id": 2, "title": "Help"},
                ]
            }
            with patch("telegram_bot.handlers.knowledge_base.get_faq_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await show_faq(self.mock_callback, self.mock_state, locale="en")

                self.mock_callback.message.edit_text.assert_called_once()

    async def test_show_faq_empty(self):
        """Test show FAQ empty."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_active_scenarios",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = {"scenarios": []}
            with patch("telegram_bot.handlers.knowledge_base.get_faq_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await show_faq(self.mock_callback, self.mock_state, locale="en")

                self.mock_callback.message.edit_text.assert_called_once()

    async def test_show_faq_no_message(self):
        """Test show FAQ with no message."""
        self.mock_callback.message = None

        await show_faq(self.mock_callback, self.mock_state, locale="en")

        # When message is None, handler returns early without calling callback.answer
        # because the check happens before any callback.answer() call


class TestFaqEmptyCallback:
    """Test cases for faq_empty_callback handler."""

    async def test_faq_empty_callback(self):
        """Test FAQ empty callback."""
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.answer = AsyncMock()

        await faq_empty_callback(mock_callback)

        mock_callback.answer.assert_called_once()


class TestViewFaqScenario:
    """Test cases for view_faq_scenario handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        # Use spec=Message for isinstance checks
        self.mock_callback.message = MagicMock(spec=Message)
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.update_data = AsyncMock()
        self.mock_state.clear = AsyncMock()

        self.mock_user = {"id": 1}
        self.auth_token = "test_token_123"  # noqa: S105

    async def test_view_faq_scenario_no_message(self):
        """Test view scenario with no message."""
        self.mock_callback.message = None
        self.mock_callback.data = "kb_faq_1"  # Need to set data attribute

        await view_faq_scenario(self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en")
        # Should return early - handler checks for message existence

    async def test_view_faq_scenario_invalid_data(self):
        """Test view scenario with invalid data."""
        self.mock_callback.data = "kb_faq_invalid"

        await view_faq_scenario(self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_view_faq_scenario_not_found(self):
        """Test view scenario when not found."""
        self.mock_callback.data = "kb_faq_1"

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_scenario",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            await view_faq_scenario(
                self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
            )

            # Handler calls answer() for loading, then for scenario_not_found alert
            assert self.mock_callback.answer.call_count >= 1

    async def test_view_faq_scenario_no_steps(self):
        """Test view scenario with no steps."""
        self.mock_callback.data = "kb_faq_1"

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_scenario",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = {"id": 1, "title": "Test", "steps": []}
            with patch("telegram_bot.handlers.knowledge_base.get_faq_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await view_faq_scenario(
                    self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
                )

                self.mock_callback.message.edit_text.assert_called_once()

    async def test_view_faq_scenario_first_step_fallback(self):
        """Test view scenario when no step with step_number=1 exists (fallback to first step)."""
        self.mock_callback.data = "kb_faq_1"

        scenario = {
            "id": 1,
            "title": "Test Scenario",
            "description": "Description",
            "steps": [
                {"id": 2, "step_number": 2, "question": "Q2"},  # No step with step_number=1
                {"id": 3, "step_number": 3, "question": "Q3"}
            ]
        }

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_scenario",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = scenario
            with patch(
                "telegram_bot.handlers.knowledge_base.get_faq_scenario_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await view_faq_scenario(
                    self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
                )

                self.mock_state.update_data.assert_called_once()
                self.mock_callback.message.edit_text.assert_called_once()

    async def test_view_faq_scenario_success(self):
        """Test view scenario success."""
        self.mock_callback.data = "kb_faq_1"

        scenario = {
            "id": 1,
            "title": "Test Scenario",
            "description": "Description",
            "steps": [
                {"id": 1, "step_number": 1, "question": "Q1"},
                {"id": 2, "step_number": 2, "question": "Q2"}
            ]
        }

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_scenario",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = scenario
            with patch(
                "telegram_bot.handlers.knowledge_base.get_faq_scenario_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await view_faq_scenario(
                    self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
                )

                self.mock_state.update_data.assert_called_once()
                self.mock_callback.message.edit_text.assert_called_once()


class TestNavigateFaqStep:
    """Test cases for navigate_faq_step handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        # Use spec=Message for isinstance checks
        self.mock_callback.message = MagicMock(spec=Message)
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.update_data = AsyncMock()
        self.mock_state.clear = AsyncMock()

    async def test_navigate_faq_step_no_message(self):
        """Test navigate step with no message."""
        self.mock_callback.message = None

        await navigate_faq_step(self.mock_callback, self.mock_state, locale="en")
        # Should return early

    async def test_navigate_faq_step_invalid_data(self):
        """Test navigate step with invalid data."""
        self.mock_callback.data = "kb_faq_step_invalid"

        await navigate_faq_step(self.mock_callback, self.mock_state, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_navigate_faq_step_back_to_menu(self):
        """Test navigate step back to menu (100)."""
        self.mock_callback.data = "kb_faq_step_1_1_100"

        self.mock_state.get_data = AsyncMock(return_value={
            "faq_step_map": {
                1: {"id": 1, "step_number": 1, "question": "Q1"}
            }
        })

        # Patch where it's imported from, not where it's defined
        with patch("telegram_bot.keyboards.main_menu.get_inline_main_menu") as mock_kb:
            mock_kb.return_value = MagicMock()
            with patch("telegram_bot.handlers.knowledge_base._get_user_from_callback") as mock_get_user:
                mock_get_user.return_value = {"id": 1}

                await navigate_faq_step(self.mock_callback, self.mock_state, locale="en")

                # The handler calls state.clear() when navigating back to menu
                self.mock_state.clear.assert_called_once()

    async def test_navigate_faq_step_contact_hr(self):
        """Test navigate step contact HR (101)."""
        self.mock_callback.data = "kb_faq_step_1_1_101"

        self.mock_state.get_data = AsyncMock(return_value={
            "faq_step_map": {
                1: {"id": 1, "step_number": 1, "question": "Q1"}
            }
        })

        with patch("telegram_bot.handlers.knowledge_base.get_faq_scenario_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await navigate_faq_step(self.mock_callback, self.mock_state, locale="en")

            self.mock_callback.message.edit_text.assert_called_once()

    async def test_navigate_faq_step_not_found(self):
        """Test navigate step when next step not found."""
        self.mock_callback.data = "kb_faq_step_1_1_999"

        self.mock_state.get_data = AsyncMock(return_value={
            "faq_step_map": {
                1: {"id": 1, "step_number": 1, "question": "Q1"}
            }
        })

        await navigate_faq_step(self.mock_callback, self.mock_state, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_navigate_faq_step_success(self):
        """Test navigate step success."""
        self.mock_callback.data = "kb_faq_step_1_1_2"

        self.mock_state.get_data = AsyncMock(return_value={
            "faq_step_map": {
                1: {"id": 1, "step_number": 1, "question": "Q1"},
                2: {"id": 2, "step_number": 2, "question": "Q2"}
            }
        })

        with patch("telegram_bot.handlers.knowledge_base.get_faq_scenario_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await navigate_faq_step(self.mock_callback, self.mock_state, locale="en")

            self.mock_state.update_data.assert_called_once()
            self.mock_callback.message.edit_text.assert_called_once()


class TestAdminKnowledgeMenu:
    """Test cases for admin_knowledge_menu handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

    async def test_admin_knowledge_menu_not_admin(self):
        """Test admin menu without admin role."""
        user = {"id": 1, "role": "USER"}

        await admin_knowledge_menu(self.mock_callback, user, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_admin_knowledge_menu_admin_success(self):
        """Test admin menu success."""
        user = {"id": 1, "role": "ADMIN"}

        with patch("telegram_bot.handlers.knowledge_base.get_admin_knowledge_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await admin_knowledge_menu(self.mock_callback, user, locale="en")

            self.mock_callback.message.edit_text.assert_called_once()

    async def test_admin_knowledge_menu_hr_success(self):
        """Test admin menu with HR role."""
        user = {"id": 1, "role": "HR"}

        with patch("telegram_bot.handlers.knowledge_base.get_admin_knowledge_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await admin_knowledge_menu(self.mock_callback, user, locale="en")

            self.mock_callback.message.edit_text.assert_called_once()

    async def test_admin_knowledge_menu_no_message(self):
        """Test admin menu with no message."""
        user = {"id": 1, "role": "ADMIN"}
        self.mock_callback.message = None

        await admin_knowledge_menu(self.mock_callback, user, locale="en")
        # Should just answer callback


class TestStartArticleCreate:
    """Test cases for start_article_create handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.set_state = AsyncMock()
        self.mock_state.update_data = AsyncMock()

    async def test_start_article_create_not_admin(self):
        """Test start create without admin role."""
        user = {"id": 1, "role": "USER"}

        await start_article_create(self.mock_callback, self.mock_state, user, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_start_article_create_success(self):
        """Test start create success."""
        user = {"id": 1, "role": "ADMIN"}

        await start_article_create(self.mock_callback, self.mock_state, user, locale="en")

        self.mock_state.set_state.assert_called_once_with(ArticleCreateStates.waiting_for_title)
        self.mock_state.update_data.assert_called_once()

    async def test_start_article_create_no_message(self):
        """Test start create with no message."""
        user = {"id": 1, "role": "ADMIN"}
        self.mock_callback.message = None

        await start_article_create(self.mock_callback, self.mock_state, user, locale="en")

        self.mock_state.set_state.assert_called_once()
        self.mock_callback.answer.assert_called_once()


class TestProcessArticleTitle:
    """Test cases for process_article_title handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()
        self.mock_message.text = "Article Title"

        self.mock_state = MagicMock()
        self.mock_state.update_data = AsyncMock()
        self.mock_state.set_state = AsyncMock()

    async def test_process_article_title_empty(self):
        """Test process empty title."""
        self.mock_message.text = "   "

        await process_article_title(self.mock_message, self.mock_state)

        self.mock_message.answer.assert_called_once()
        self.mock_state.update_data.assert_not_called()

    async def test_process_article_title_success(self):
        """Test process title success."""
        await process_article_title(self.mock_message, self.mock_state)

        self.mock_state.update_data.assert_called_once_with(title="Article Title")
        self.mock_state.set_state.assert_called_once_with(ArticleCreateStates.waiting_for_content)


class TestProcessArticleContent:
    """Test cases for process_article_content handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()
        self.mock_message.text = "Article content here"

        self.mock_state = MagicMock()
        self.mock_state.update_data = AsyncMock()
        self.mock_state.set_state = AsyncMock()

    async def test_process_article_content_empty(self):
        """Test process empty content."""
        self.mock_message.text = "   "

        await process_article_content(self.mock_message, self.mock_state)

        self.mock_message.answer.assert_called_once()
        self.mock_state.update_data.assert_not_called()

    async def test_process_article_content_success(self):
        """Test process content success."""
        with patch("telegram_bot.handlers.knowledge_base.get_kb_create_files_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await process_article_content(self.mock_message, self.mock_state)

            self.mock_state.update_data.assert_called_once()
            self.mock_state.set_state.assert_called_once()


class TestProcessArticleFile:
    """Test cases for process_article_file handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()
        self.mock_message.document = MagicMock()
        self.mock_message.document.file_name = "test.pdf"
        self.mock_message.document.file_size = 1024
        self.mock_message.document.file_id = "file_123"
        self.mock_message.bot = MagicMock()
        self.mock_message.bot.get_file = AsyncMock(return_value=MagicMock(file_path="path/to/file"))
        self.mock_message.bot.download_file = AsyncMock(return_value=BytesIO(b"content"))

        self.mock_state = MagicMock()
        self.mock_state.get_data = AsyncMock(return_value={"files": []})
        self.mock_state.update_data = AsyncMock()

    async def test_process_article_file_no_document(self):
        """Test process with no document."""
        self.mock_message.document = None

        await process_article_file(self.mock_message, self.mock_state)

        self.mock_message.answer.assert_called_once()

    async def test_process_article_file_not_allowed(self):
        """Test process with not allowed file type."""
        self.mock_message.document.file_name = "test.exe"

        await process_article_file(self.mock_message, self.mock_state)

        self.mock_message.answer.assert_called_once()

    async def test_process_article_file_too_large(self):
        """Test process with file too large."""
        self.mock_message.document.file_size = 20 * 1024 * 1024

        await process_article_file(self.mock_message, self.mock_state)

        self.mock_message.answer.assert_called_once()

    async def test_process_article_file_no_bot(self):
        """Test process with no bot."""
        self.mock_message.bot = None

        await process_article_file(self.mock_message, self.mock_state)

        # Should return early

    async def test_process_article_file_download_failed(self):
        """Test process when download fails."""
        self.mock_message.bot.download_file = AsyncMock(return_value=None)

        await process_article_file(self.mock_message, self.mock_state)

        self.mock_message.answer.assert_called_once()

    async def test_process_article_file_success(self):
        """Test process file success."""
        await process_article_file(self.mock_message, self.mock_state)

        self.mock_state.update_data.assert_called_once()


class TestSaveArticle:
    """Test cases for save_article handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.clear = AsyncMock()

        self.mock_user = {"id": 1, "department": "Engineering"}
        self.auth_token = "test_token_123"  # noqa: S105

    async def test_save_article_no_auth(self):
        """Test save without auth."""
        await save_article(self.mock_callback, self.mock_state, self.mock_user, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_save_article_create_failed(self):
        """Test save when create fails."""
        self.mock_state.get_data = AsyncMock(return_value={
            "title": "Test",
            "content": "Content",
            "files": []
        })

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.create_article",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = None

            await save_article(
                self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
            )

            self.mock_state.clear.assert_called_once()

    async def test_save_article_no_article_id(self):
        """Test save when article has no ID."""
        self.mock_state.get_data = AsyncMock(return_value={
            "title": "Test",
            "content": "Content",
            "files": []
        })

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.create_article",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = {"title": "Test"}  # No id

            await save_article(
                self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
            )

            self.mock_state.clear.assert_called_once()

    async def test_save_article_success(self):
        """Test save success."""
        self.mock_state.get_data = AsyncMock(return_value={
            "title": "Test",
            "content": "Content",
            "files": [{"filename": "file.pdf", "content": b"content", "content_type": "application/pdf"}]
        })

        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.create_article",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = {"id": 1, "title": "Test"}
            with patch(
                "telegram_bot.handlers.knowledge_base.knowledge_client.upload_attachment",
                new_callable=AsyncMock,
            ) as mock_upload:
                mock_upload.return_value = {"id": 1}
                with patch(
                    "telegram_bot.handlers.knowledge_base.get_kb_article_saved_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await save_article(
                        self.mock_callback, self.mock_state, self.mock_user, self.auth_token, locale="en"
                    )

                    self.mock_state.clear.assert_called_once()
                    self.mock_callback.message.edit_text.assert_called_once()


class TestCancelArticleCreate:
    """Test cases for cancel_article_create handler."""

    async def test_cancel_article_create(self):
        """Test cancel article creation."""
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.answer = AsyncMock()
        mock_callback.message = MagicMock()
        mock_callback.message.edit_text = AsyncMock()

        mock_state = MagicMock()
        mock_state.clear = AsyncMock()

        await cancel_article_create(mock_callback, mock_state)

        mock_state.clear.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_cancel_article_create_no_message(self):
        """Test cancel with no message."""
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.answer = AsyncMock()
        mock_callback.message = None

        mock_state = MagicMock()
        mock_state.clear = AsyncMock()

        await cancel_article_create(mock_callback, mock_state)

        mock_state.clear.assert_called_once()


class TestStartFileUpload:
    """Test cases for start_file_upload handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.set_state = AsyncMock()

    async def test_start_file_upload_not_admin(self):
        """Test upload without admin role."""
        user = {"id": 1, "role": "USER"}

        await start_file_upload(self.mock_callback, self.mock_state, user, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_start_file_upload_success(self):
        """Test start upload success."""
        user = {"id": 1, "role": "ADMIN"}

        await start_file_upload(self.mock_callback, self.mock_state, user, locale="en")

        self.mock_state.set_state.assert_called_once_with(FileUploadStates.waiting_for_article_id)

    async def test_start_file_upload_no_message(self):
        """Test start upload with no message."""
        user = {"id": 1, "role": "ADMIN"}
        self.mock_callback.message = None

        await start_file_upload(self.mock_callback, self.mock_state, user, locale="en")

        self.mock_state.set_state.assert_called_once()


class TestProcessUploadArticleId:
    """Test cases for process_upload_article_id handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()
        self.mock_message.text = "123"

        self.mock_state = MagicMock()
        self.mock_state.update_data = AsyncMock()
        self.mock_state.set_state = AsyncMock()
        self.mock_state.clear = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_process_upload_article_id_invalid(self):
        """Test process invalid article ID."""
        self.mock_message.text = "abc"

        await process_upload_article_id(self.mock_message, self.mock_state, self.auth_token, locale="en")
        self.mock_message.answer.assert_called_once()

    async def test_process_upload_article_id_no_auth(self):
        """Test process without auth."""
        await process_upload_article_id(self.mock_message, self.mock_state, None, locale="en")
        self.mock_state.clear.assert_called_once()

    async def test_process_upload_article_id_not_found(self):
        """Test process when article not found."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_details",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            await process_upload_article_id(
                self.mock_message, self.mock_state, self.auth_token, locale="en"
            )
            self.mock_message.answer.assert_called_once()

    async def test_process_upload_article_id_success(self):
        """Test process success."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.get_article_details",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = {"id": 123, "title": "Test Article"}
            with patch(
                "telegram_bot.handlers.knowledge_base.get_kb_upload_files_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await process_upload_article_id(
                    self.mock_message, self.mock_state, self.auth_token, locale="en"
                )

                self.mock_state.update_data.assert_called_once()
                self.mock_state.set_state.assert_called_once()


class TestProcessUploadFile:
    """Test cases for process_upload_file handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock(spec=Message)
        self.mock_message.answer = AsyncMock()
        self.mock_message.document = MagicMock()
        self.mock_message.document.file_name = "test.pdf"
        self.mock_message.document.file_size = 1024
        self.mock_message.document.file_id = "file_123"
        self.mock_message.document.mime_type = "application/pdf"
        self.mock_message.bot = MagicMock()
        self.mock_message.bot.get_file = AsyncMock(return_value=MagicMock(file_path="path/to/file"))
        self.mock_message.bot.download_file = AsyncMock(return_value=BytesIO(b"content"))

        self.mock_state = MagicMock()
        self.mock_state.get_data = AsyncMock(return_value={"files": []})
        self.mock_state.update_data = AsyncMock()

    async def test_process_upload_file_no_document(self):
        """Test process with no document."""
        self.mock_message.document = None

        await process_upload_file(self.mock_message, self.mock_state)

        self.mock_message.answer.assert_called_once()

    async def test_process_upload_file_not_allowed(self):
        """Test process with not allowed file type."""
        self.mock_message.document.file_name = "test.exe"

        await process_upload_file(self.mock_message, self.mock_state)

        self.mock_message.answer.assert_called_once()

    async def test_process_upload_file_too_large(self):
        """Test process with file too large."""
        self.mock_message.document.file_size = 20 * 1024 * 1024

        await process_upload_file(self.mock_message, self.mock_state)

        self.mock_message.answer.assert_called_once()

    async def test_process_upload_file_no_bot(self):
        """Test process with no bot."""
        self.mock_message.bot = None

        await process_upload_file(self.mock_message, self.mock_state)

    async def test_process_upload_file_download_failed(self):
        """Test process when download fails."""
        self.mock_message.bot.download_file = AsyncMock(return_value=None)

        await process_upload_file(self.mock_message, self.mock_state)

        self.mock_message.answer.assert_called_once()

    async def test_process_upload_file_success(self):
        """Test process file success."""
        await process_upload_file(self.mock_message, self.mock_state)

        self.mock_state.update_data.assert_called_once()


class TestSaveUploadedFiles:
    """Test cases for save_uploaded_files handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock(spec=CallbackQuery)
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_state = MagicMock()
        self.mock_state.get_data = AsyncMock(return_value={
            "article_id": 1,
            "files": [{"filename": "file.pdf", "content": b"content", "content_type": "application/pdf"}]
        })
        self.mock_state.clear = AsyncMock()

        self.auth_token = "test_token_123"  # noqa: S105

    async def test_save_uploaded_files_no_auth(self):
        """Test save without auth."""
        await save_uploaded_files(self.mock_callback, self.mock_state, None, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_save_uploaded_files_no_files(self):
        """Test save with no files."""
        self.mock_state.get_data = AsyncMock(return_value={"article_id": 1, "files": []})

        await save_uploaded_files(self.mock_callback, self.mock_state, self.auth_token, locale="en")
        self.mock_callback.answer.assert_called_once()

    async def test_save_uploaded_files_success(self):
        """Test save success."""
        with patch(
            "telegram_bot.handlers.knowledge_base.knowledge_client.upload_attachment",
            new_callable=AsyncMock,
        ) as mock_upload:
            mock_upload.return_value = {"id": 1}
            with patch(
                "telegram_bot.handlers.knowledge_base.get_kb_upload_complete_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await save_uploaded_files(
                    self.mock_callback, self.mock_state, self.auth_token, locale="en"
                )

                self.mock_state.clear.assert_called_once()
                self.mock_callback.message.edit_text.assert_called_once()


class TestCancelFileUpload:
    """Test cases for cancel_file_upload handler."""

    async def test_cancel_file_upload(self):
        """Test cancel file upload."""
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.answer = AsyncMock()
        mock_callback.message = MagicMock()
        mock_callback.message.edit_text = AsyncMock()

        mock_state = MagicMock()
        mock_state.clear = AsyncMock()

        await cancel_file_upload(mock_callback, mock_state)

        mock_state.clear.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_cancel_file_upload_no_message(self):
        """Test cancel with no message."""
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.answer = AsyncMock()
        mock_callback.message = None

        mock_state = MagicMock()
        mock_state.clear = AsyncMock()

        await cancel_file_upload(mock_callback, mock_state)

        mock_state.clear.assert_called_once()


class TestFormatFileSize:
    """Test cases for _format_file_size helper."""

    def test_format_file_size_none(self):
        """Test format None."""
        assert _format_file_size(None) == ""

    def test_format_file_size_bytes(self):
        """Test format bytes."""
        assert _format_file_size(100) == "100 B"

    def test_format_file_size_kb(self):
        """Test format KB."""
        assert _format_file_size(1024) == "1.0 KB"

    def test_format_file_size_mb(self):
        """Test format MB."""
        assert _format_file_size(1024 * 1024) == "1.0 MB"


class TestGetUserFromCallback:
    """Test cases for _get_user_from_callback helper."""

    async def test_get_user_from_callback_success(self):
        """Test getting user from callback with valid from_user."""
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.from_user = MagicMock()
        mock_callback.from_user.id = 123456
        mock_callback.from_user.first_name = "John"
        mock_callback.from_user.last_name = "Doe"
        mock_callback.from_user.username = "johndoe"

        result = await _get_user_from_callback(mock_callback)

        assert result is not None
        assert result["id"] == 123456
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["username"] == "johndoe"

    async def test_get_user_from_callback_no_from_user(self):
        """Test getting user from callback when from_user is None."""
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.from_user = None

        result = await _get_user_from_callback(mock_callback)

        assert result is None


class TestGetKnowledgeBaseMenu:
    """Test cases for _get_knowledge_base_menu helper."""

    async def test_get_knowledge_base_menu_cached(self):
        """Test cached menu."""
        with patch("telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = {"title": "Cached"}

            result = await _get_knowledge_base_menu()

            # When cache returns a value, the cached result should be returned
            assert result["title"] == "Cached"

    async def test_get_knowledge_base_menu_uncached(self):
        """Test uncached menu returns default menu dict."""
        with patch("telegram_bot.handlers.knowledge_base.cache.get", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = None

            result = await _get_knowledge_base_menu()

            assert result["title"] == "Knowledge Base"
            assert "description" in result
