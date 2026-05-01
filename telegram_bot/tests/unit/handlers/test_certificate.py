"""Unit tests for telegram_bot/handlers/certificate.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import BufferedInputFile
from telegram_bot.handlers.certificate import download_certificate, show_certificates


class TestCertificateHandlers:
    """Test cases for certificate handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 123456
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query."""
        cb = MagicMock()
        cb.id = "callback_123"
        cb.from_user = MagicMock()
        cb.from_user.id = 123456
        cb.data = "download_cert:test_cert_uid"
        cb.answer = AsyncMock()
        cb.message = MagicMock()
        cb.message.answer_document = AsyncMock()
        return cb

    async def test_show_certificates_no_auth_token(self, mock_message):
        """Test show certificates when auth_token is missing."""
        await show_certificates(mock_message, auth_token="", user={"id": 123456}, locale="en")
        mock_message.answer.assert_called_once()

    async def test_show_certificates_no_user(self, mock_message):
        """Test show certificates when user is missing."""
        await show_certificates(mock_message, auth_token="test_token", user=None, locale="en")
        mock_message.answer.assert_called_once()

    async def test_show_certificates_no_certificates(self, mock_message):
        """Test show certificates when user has no certificates."""
        with patch("telegram_bot.handlers.certificate.certificates_client") as mock_client:
            mock_client.get_my_certificates = AsyncMock(return_value=[])

            await show_certificates(mock_message, auth_token="test_token", user={"id": 123456}, locale="en")

            mock_client.get_my_certificates.assert_called_once_with("test_token")
            mock_message.answer.assert_called_once()

    async def test_show_certificates_with_certificates(self, mock_message):
        """Test show certificates when user has certificates."""
        with patch("telegram_bot.handlers.certificate.certificates_client") as mock_client:
            mock_client.get_my_certificates = AsyncMock(
                return_value=[
                    {"cert_uid": "cert123", "issued_at": "2024-01-01"},
                    {"cert_uid": "cert456", "issued_at": "2024-02-01"},
                ]
            )

            await show_certificates(mock_message, auth_token="test_token", user={"id": 123456}, locale="en")

            mock_client.get_my_certificates.assert_called_once_with("test_token")
            mock_message.answer.assert_called_once()
            # Check that reply_markup is set (keyboard is built)
            call_kwargs = mock_message.answer.call_args[1]
            assert "reply_markup" in call_kwargs

    async def test_download_certificate_no_auth_token(self, mock_callback):
        """Test download certificate when auth_token is missing."""
        await download_certificate(mock_callback, auth_token="", user={"id": 123456}, locale="en")
        mock_callback.answer.assert_called_once()

    async def test_download_certificate_no_user(self, mock_callback):
        """Test download certificate when user is missing."""
        await download_certificate(mock_callback, auth_token="test_token", user=None, locale="en")
        mock_callback.answer.assert_called_once()

    async def test_download_certificate_success(self, mock_callback):
        """Test successful certificate download."""
        mock_callback.data = "download_cert:test_cert_uid"
        with patch("telegram_bot.handlers.certificate.certificates_client") as mock_client:
            pdf_bytes = b"fake pdf content"
            mock_client.download_certificate = AsyncMock(return_value=pdf_bytes)

            await download_certificate(mock_callback, auth_token="test_token", user={"id": 123456}, locale="en")

            mock_client.download_certificate.assert_called_once_with("test_cert_uid", "en", "test_token")
            mock_callback.message.answer_document.assert_called_once()
            mock_callback.answer.assert_called_once()

            # Check that the file is passed correctly
            call_args = mock_callback.message.answer_document.call_args[0]
            assert isinstance(call_args[0], BufferedInputFile)

    async def test_download_certificate_error(self, mock_callback):
        """Test download certificate when an error occurs."""
        with patch("telegram_bot.handlers.certificate.certificates_client") as mock_client:
            mock_client.download_certificate = AsyncMock(side_effect=Exception("Download failed"))

            await download_certificate(mock_callback, auth_token="test_token", user={"id": 123456}, locale="en")

            mock_callback.answer.assert_called_once()
