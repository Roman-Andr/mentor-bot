"""HTTP client for document service integration."""

import httpx
from fastapi import status
from loguru import logger

from telegram_bot.config import settings
from telegram_bot.utils.cache import cached


class DocumentServiceClient:
    """HTTP client for document service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize document service HTTP client."""
        self.base_url = base_url or settings.KNOWLEDGE_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT
        )

    @cached(ttl=60, key_prefix="dept_docs")
    async def get_department_documents(
        self, department: str, auth_token: str
    ) -> list[dict]:
        """Get documents for department (cached)."""
        logger.debug("Fetching department documents (department={})", department)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/articles/department/{department}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                logger.debug("Department documents fetched (department={}, count={})", department, len(data.get("articles", [])))
                return data.get("articles", [])
        except httpx.RequestError:
            logger.exception("Document service request failed (department={})", department)
        return []

    @cached(ttl=60, key_prefix="company_policies")
    async def get_company_policies(self, auth_token: str) -> list[dict]:
        """Get company policies (cached)."""
        # Assuming company policies are stored in a specific category or department
        # For now, return empty list or fetch from a specific endpoint
        logger.debug("Fetching company policies")
        try:
            # This is a placeholder - adjust based on actual API structure
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/articles",
                params={"category": "company_policies"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                logger.debug("Company policies fetched (count={})", len(data.get("articles", [])))
                return data.get("articles", [])
        except httpx.RequestError:
            logger.exception("Document service request failed")
        return []

    @cached(ttl=60, key_prefix="training_materials")
    async def get_training_materials(self, auth_token: str) -> list[dict]:
        """Get training materials (cached)."""
        logger.debug("Fetching training materials")
        try:
            # This is a placeholder - adjust based on actual API structure
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/articles",
                params={"category": "training"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                logger.debug("Training materials fetched (count={})", len(data.get("articles", [])))
                return data.get("articles", [])
        except httpx.RequestError:
            logger.exception("Document service request failed")
        return []

    async def get_article_details(
        self, article_id: int, auth_token: str
    ) -> dict | None:
        """Get article details with attachments."""
        logger.debug("Fetching article details (article_id={})", article_id)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/articles/{article_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("Article details fetched (article_id={})", article_id)
                return response.json()
            logger.warning("Article not found (article_id={})", article_id)
        except httpx.RequestError:
            logger.exception("Document service request failed (article_id={})", article_id)
        return None


# Singleton instance
document_client = DocumentServiceClient()
