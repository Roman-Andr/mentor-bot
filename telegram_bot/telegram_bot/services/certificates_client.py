"""Certificates service client for Telegram bot."""

import logging

import httpx

from telegram_bot.config import settings

logger = logging.getLogger(__name__)


class CertificatesClient:
    """HTTP client for certificates service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize certificates service HTTP client."""
        self.base_url = base_url or settings.CHECKLISTS_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.SERVICE_TIMEOUT,
        )

    async def get_my_certificates(self, auth_token: str) -> list[dict]:
        """Get certificates for the current user."""
        try:
            response = await self.client.get(
                "/api/v1/certificates/my",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error("Failed to fetch certificates: %s", e)
            return []
        except httpx.HTTPStatusError as e:
            logger.error("Certificates service error: %s", e)
            return []

    async def download_certificate(self, cert_uid: str, locale: str, auth_token: str) -> bytes:
        """Download certificate PDF."""
        try:
            response = await self.client.get(
                f"/api/v1/certificates/{cert_uid}/download",
                headers={"Authorization": f"Bearer {auth_token}"},
                params={"locale": locale},
            )
            response.raise_for_status()
            return response.content
        except httpx.RequestError as e:
            logger.error("Failed to download certificate: %s", e)
            raise
        except httpx.HTTPStatusError as e:
            logger.error("Certificate download error: %s", e)
            raise


certificates_client = CertificatesClient()
