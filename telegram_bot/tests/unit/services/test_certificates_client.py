"""Unit tests for telegram_bot/services/certificates_client.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import httpx

from telegram_bot.services.certificates_client import CertificatesClient, certificates_client


class TestCertificatesClient:
    """Test cases for CertificatesClient."""

    @pytest.fixture
    def client(self):
        """Create a CertificatesClient instance."""
        with patch("telegram_bot.services.certificates_client.httpx.AsyncClient"):
            return CertificatesClient(base_url="http://test.com")

    async def test_get_my_certificates_success(self, client):
        """Test successful retrieval of certificates."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"cert_uid": "cert123", "issued_at": "2024-01-01"}]
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.get_my_certificates("test_token")

        assert result == [{"cert_uid": "cert123", "issued_at": "2024-01-01"}]
        client.client.get.assert_called_once_with(
            "/api/v1/certificates/my",
            headers={"Authorization": "Bearer test_token"},
        )

    async def test_get_my_certificates_request_error(self, client):
        """Test get_my_certificates with RequestError."""
        client.client.get = AsyncMock(side_effect=httpx.RequestError("Connection error"))

        result = await client.get_my_certificates("test_token")

        assert result == []

    async def test_get_my_certificates_http_error(self, client):
        """Test get_my_certificates with HTTPStatusError."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=MagicMock(), response=MagicMock()
        )
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.get_my_certificates("test_token")

        assert result == []

    async def test_download_certificate_success(self, client):
        """Test successful certificate download."""
        mock_response = MagicMock()
        mock_response.content = b"fake pdf content"
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.download_certificate("cert123", "en", "test_token")

        assert result == b"fake pdf content"
        client.client.get.assert_called_once_with(
            "/api/v1/certificates/cert123/download",
            headers={"Authorization": "Bearer test_token"},
            params={"locale": "en"},
        )

    async def test_download_certificate_request_error(self, client):
        """Test download_certificate with RequestError."""
        client.client.get = AsyncMock(side_effect=httpx.RequestError("Connection error"))

        with pytest.raises(httpx.RequestError):
            await client.download_certificate("cert123", "en", "test_token")

    async def test_download_certificate_http_error(self, client):
        """Test download_certificate with HTTPStatusError."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=MagicMock(), response=MagicMock()
        )
        client.client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(httpx.HTTPStatusError):
            await client.download_certificate("cert123", "en", "test_token")

    def test_certificates_client_singleton(self):
        """Test that certificates_client is a singleton instance."""
        assert isinstance(certificates_client, CertificatesClient)
