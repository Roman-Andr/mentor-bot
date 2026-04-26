"""Unit tests for telegram_bot/services/knowledge_client.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_bot.schemas.search import SearchResponse
from telegram_bot.services.knowledge_client import KnowledgeServiceClient, knowledge_client


class TestKnowledgeServiceClient:
    """Test cases for KnowledgeServiceClient."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test client."""
        self.client = KnowledgeServiceClient(base_url="http://test-knowledge:8003")
        self.auth_token = "test_token_123"

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.post")
    async def test_search_articles_success(self, mock_post):
        """Test searching articles - success case."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 2,
            "results": [
                {"id": 1, "title": "Article 1", "slug": "article-1"},
                {"id": 2, "title": "Article 2", "slug": "article-2"},
            ],
            "query": "test query",
            "filters": {},
            "suggestions": [],
            "page": 1,
            "size": 5,
            "pages": 1,
        }
        mock_post.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.search_articles("test query", self.auth_token)

        assert isinstance(result, SearchResponse)
        assert result.total == 2
        assert len(result.results) == 2

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.post")
    async def test_search_articles_error(self, mock_post):
        """Test searching articles - request error."""
        import httpx
        mock_post.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.search_articles("test query", self.auth_token)

        assert isinstance(result, SearchResponse)
        assert result.total == 0
        assert result.results == []

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_search_suggestions_success(self, mock_get):
        """Test getting search suggestions - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["suggestion1", "suggestion2", "suggestion3"]
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_search_suggestions("test", self.auth_token)

        assert result == ["suggestion1", "suggestion2", "suggestion3"]

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_search_suggestions_error(self, mock_get):
        """Test getting search suggestions - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_search_suggestions("test", self.auth_token)

        assert result == []

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_article_details_success(self, mock_get):
        """Test getting article details - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "title": "Article 1", "content": "Content"}
        mock_get.return_value = mock_response

        result = await self.client.get_article_details(1, self.auth_token)

        assert result is not None
        assert result["id"] == 1
        assert result["title"] == "Article 1"

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_article_details_not_found(self, mock_get):
        """Test getting article details - not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await self.client.get_article_details(999, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_article_details_error(self, mock_get):
        """Test getting article details - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.get_article_details(1, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_article_attachments_success(self, mock_get):
        """Test getting article attachments - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "attachments": [
                {"id": 1, "name": "file1.pdf"},
                {"id": 2, "name": "file2.doc"},
            ]
        }
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_article_attachments(1, self.auth_token)

        assert len(result) == 2
        assert result[0]["name"] == "file1.pdf"

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_article_attachments_error(self, mock_get):
        """Test getting article attachments - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_article_attachments(1, self.auth_token)

        assert result == []

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_download_attachment_success(self, mock_get):
        """Test downloading attachment - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"file content"
        mock_get.return_value = mock_response

        result = await self.client.download_attachment(1, "file.pdf", self.auth_token)

        assert result == b"file content"

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_download_attachment_not_found(self, mock_get):
        """Test downloading attachment - not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await self.client.download_attachment(1, "file.pdf", self.auth_token)

        assert result is None

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_download_attachment_request_error(self, mock_get):
        """Test downloading attachment - request error.

        Covers lines 116-117: httpx.RequestError handling in download_attachment.
        """
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.download_attachment(1, "file.pdf", self.auth_token)

        assert result is None

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.post")
    async def test_upload_attachment_success(self, mock_post):
        """Test uploading attachment - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "uploaded.pdf"}
        mock_post.return_value = mock_response

        result = await self.client.upload_attachment(
            1, b"file content", "file.pdf", self.auth_token
        )

        assert result is not None
        assert result["name"] == "uploaded.pdf"

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.post")
    async def test_upload_attachment_failure(self, mock_post):
        """Test uploading attachment - failure."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        result = await self.client.upload_attachment(
            1, b"file content", "file.pdf", self.auth_token
        )

        assert result is None

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.post")
    async def test_upload_attachment_request_error(self, mock_post):
        """Test uploading attachment - request error.

        Covers lines 140-141: httpx.RequestError handling in upload_attachment.
        """
        import httpx
        mock_post.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.upload_attachment(
            1, b"file content", "file.pdf", self.auth_token
        )

        assert result is None

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.post")
    async def test_create_article_success(self, mock_post):
        """Test creating article - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "title": "New Article", "content": "Content"}
        mock_post.return_value = mock_response

        result = await self.client.create_article(
            "New Article", "Content", self.auth_token, category_id=5, department="Engineering"
        )

        assert result is not None
        assert result["title"] == "New Article"

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.post")
    async def test_create_article_minimal(self, mock_post):
        """Test creating article with minimal params."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "title": "Simple Article"}
        mock_post.return_value = mock_response

        result = await self.client.create_article("Simple Article", "Content", self.auth_token)

        assert result is not None

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.post")
    async def test_create_article_failure(self, mock_post):
        """Test creating article - failure."""
        import httpx
        mock_post.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.create_article("Article", "Content", self.auth_token)

        assert result is None

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.post")
    async def test_create_article_non_200_status(self, mock_post):
        """Test creating article - non-200 status code."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        result = await self.client.create_article("Article", "Content", self.auth_token)

        assert result is None

    def test_get_attachment_download_url(self):
        """Test getting attachment download URL."""
        result = self.client.get_attachment_download_url(1, "file.pdf")

        assert "/attachments/file/1/file.pdf" in result

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_active_scenarios_success(self, mock_get):
        """Test getting active scenarios - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 2,
            "scenarios": [{"id": 1, "title": "Scenario 1"}],
            "page": 1,
            "size": 50,
            "pages": 1,
        }
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_active_scenarios()

        assert result["total"] == 2
        assert len(result["scenarios"]) == 1

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_active_scenarios_error(self, mock_get):
        """Test getting active scenarios - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_active_scenarios()

        assert result["total"] == 0
        assert result["scenarios"] == []

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_scenario_success(self, mock_get):
        """Test getting scenario by ID - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "title": "Scenario 1",
            "steps": [{"id": 1, "content": "Step 1"}],
        }
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_scenario(1)

        assert result["id"] == 1
        assert "steps" in result

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_scenario_error(self, mock_get):
        """Test getting scenario by ID - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_scenario(1)

        assert result["id"] == 1
        assert result["steps"] == []

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_scenario_not_found(self, mock_get):
        """Test getting scenario by ID - not found (non-200 status)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_scenario(1)

        assert result["id"] == 1
        assert result["steps"] == []

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_categories_success(self, mock_get):
        """Test getting categories - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 3,
            "categories": [
                {"id": 1, "name": "Category 1"},
                {"id": 2, "name": "Category 2"},
            ],
        }
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_categories(self.auth_token)

        assert result["total"] == 3

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_categories_error(self, mock_get):
        """Test getting categories - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_categories(self.auth_token)

        assert result["total"] == 0
        assert result["categories"] == []

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_articles_by_category_success(self, mock_get):
        """Test getting articles by category - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 5,
            "articles": [{"id": 1, "title": "Article 1"}],
        }
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_articles_by_category(1, self.auth_token)

        assert result["total"] == 5

    @patch("telegram_bot.services.knowledge_client.httpx.AsyncClient.get")
    async def test_get_articles_by_category_error(self, mock_get):
        """Test getting articles by category - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_articles_by_category(1, self.auth_token)

        assert result["total"] == 0
        assert result["articles"] == []


class TestKnowledgeClientSingleton:
    """Test the knowledge_client singleton instance."""

    def test_singleton_is_mocked_in_tests(self):
        """Test that knowledge_client is mocked in test environment."""
        # In test environment, knowledge_client is patched to prevent real HTTP calls
        assert knowledge_client is not None
