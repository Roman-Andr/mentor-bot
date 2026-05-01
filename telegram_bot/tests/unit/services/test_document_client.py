"""Unit tests for telegram_bot/services/document_client.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_bot.services.document_client import DocumentServiceClient, document_client


class TestDocumentServiceClient:
    """Test cases for DocumentServiceClient."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test client."""
        self.client = DocumentServiceClient(base_url="http://test-knowledge:8003")
        self.auth_token = "test_token_123"

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_department_documents_success(self, mock_get):
        """Test getting department documents - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {"id": 1, "title": "Doc 1"},
                {"id": 2, "title": "Doc 2"},
            ]
        }
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_department_documents("Engineering", self.auth_token)

        assert len(result) == 2
        assert result[0]["title"] == "Doc 1"

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_department_documents_empty(self, mock_get):
        """Test getting department documents - empty result."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"articles": []}
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_department_documents("HR", self.auth_token)

        assert result == []

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_department_documents_error(self, mock_get):
        """Test getting department documents - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_department_documents("Engineering", self.auth_token)

        assert result == []

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_company_policies_success(self, mock_get):
        """Test getting company policies - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {"id": 1, "title": "Policy 1"},
                {"id": 2, "title": "Policy 2"},
            ]
        }
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_company_policies(self.auth_token)

        assert len(result) == 2

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_company_policies_error(self, mock_get):
        """Test getting company policies - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_company_policies(self.auth_token)

        assert result == []

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_training_materials_success(self, mock_get):
        """Test getting training materials - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {"id": 1, "title": "Training 1"},
            ]
        }
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_training_materials(self.auth_token)

        assert len(result) == 1

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_training_materials_error(self, mock_get):
        """Test getting training materials - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_training_materials(self.auth_token)

        assert result == []

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
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

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_article_details_not_found(self, mock_get):
        """Test getting article details - not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await self.client.get_article_details(999, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_article_details_error(self, mock_get):
        """Test getting article details - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.get_article_details(1, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_department_documents_list_success(self, mock_get):
        """Test getting department documents list - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "documents": [
                {"id": 1, "title": "Doc 1"},
                {"id": 2, "title": "Doc 2"},
            ]
        }
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_department_documents_list(1, self.auth_token)

        assert len(result) == 2
        assert result[0]["title"] == "Doc 1"

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_department_documents_list_no_department_id(self, mock_get):
        """Test getting department documents list without department_id."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"documents": []}
        mock_get.return_value = mock_response

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_department_documents_list(None, self.auth_token)

        assert result == []

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_department_documents_list_error(self, mock_get):
        """Test getting department documents list - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                result = await self.client.get_department_documents_list(1, self.auth_token)

        assert result == []

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_department_document_download_url_302(self, mock_get):
        """Test getting department document download URL - 302 redirect."""
        from fastapi import status
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_302_FOUND
        mock_response.headers = {"location": "https://example.com/file.pdf"}
        mock_get.return_value = mock_response

        result = await self.client.get_department_document_download_url(1, self.auth_token)

        assert result == "https://example.com/file.pdf"

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_department_document_download_url_200(self, mock_get):
        """Test getting department document download URL - 200 OK."""
        from fastapi import status
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.url = "https://example.com/file.pdf"
        mock_get.return_value = mock_response

        result = await self.client.get_department_document_download_url(1, self.auth_token)

        assert result == "https://example.com/file.pdf"

    @patch("telegram_bot.services.document_client.httpx.AsyncClient.get")
    async def test_get_department_document_download_url_error(self, mock_get):
        """Test getting department document download URL - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.get_department_document_download_url(1, self.auth_token)

        assert result is None


class TestDocumentClientSingleton:
    """Test the document_client singleton instance."""

    def test_singleton_exists(self):
        """Test that document_client singleton exists."""
        assert document_client is not None
        assert isinstance(document_client, DocumentServiceClient)
