"""HTTP client for knowledge service integration."""

import logging

import httpx
from fastapi import status

from telegram_bot.config import settings
from telegram_bot.schemas.search import SearchResponse
from telegram_bot.utils.cache import cached

logger = logging.getLogger(__name__)


class KnowledgeServiceClient:
    """HTTP client for knowledge service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize knowledge service HTTP client."""
        self.base_url = base_url or settings.KNOWLEDGE_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT
        )

    @cached(ttl=30, key_prefix="kb_search")
    async def search_articles(
        self, query: str, auth_token: str, page: int = 1, size: int = 5
    ) -> SearchResponse:
        """Search articles in knowledge base (cached)."""
        try:
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/search",
                json={
                    "query": query,
                    "page": page,
                    "size": size,
                    "only_published": True,
                },
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return SearchResponse(**response.json())
        except httpx.RequestError:
            logger.exception("Knowledge service search request failed")
        return SearchResponse(
            total=0,
            results=[],
            query=query,
            filters={},
            suggestions=[],
            page=page,
            size=size,
            pages=0,
        )

    @cached(ttl=60, key_prefix="kb_suggestions")
    async def get_search_suggestions(
        self, query: str, auth_token: str, limit: int = 10
    ) -> list[str]:
        """Get search suggestions (cached)."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/search/suggest",
                params={"query": query, "limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Knowledge service suggestions request failed")
        return []

    async def get_article_details(
        self, article_id: int, auth_token: str
    ) -> dict | None:
        """Get article details by ID."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/articles/{article_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Knowledge service article details request failed")
        return None

    @cached(ttl=30, key_prefix="kb_attachments")
    async def get_article_attachments(
        self, article_id: int, auth_token: str
    ) -> list[dict]:
        """Get all attachments for an article (cached)."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/attachments/article/{article_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                return data.get("attachments", [])
        except httpx.RequestError:
            logger.exception("Knowledge service attachments request failed")
        return []

    async def download_attachment(
        self, article_id: int, filename: str, auth_token: str
    ) -> bytes | None:
        """Download attachment file content."""
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/attachments/file/{article_id}/{filename}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.content
        except httpx.RequestError:
            logger.exception("Knowledge service file download failed")
        return None

    async def upload_attachment(
        self,
        article_id: int,
        file_bytes: bytes,
        filename: str,
        auth_token: str,
        content_type: str = "application/octet-stream",
    ) -> dict | None:
        """Upload a file attachment to an article."""
        try:
            files = {"file": (filename, file_bytes, content_type)}
            data = {"article_id": str(article_id)}
            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/attachments/upload",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Knowledge service file upload failed")
        return None

    async def create_article(
        self,
        title: str,
        content: str,
        auth_token: str,
        *,
        category_id: int | None = None,
        department: str | None = None,
        status_value: str = "DRAFT",
    ) -> dict | None:
        """Create a new article in the knowledge base."""
        try:
            payload: dict = {
                "title": title,
                "content": content,
                "status": status_value,
            }
            if category_id is not None:
                payload["category_id"] = category_id
            if department is not None:
                payload["department"] = department

            response = await self.client.post(
                f"{settings.API_V1_PREFIX}/articles",
                json=payload,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()
        except httpx.RequestError:
            logger.exception("Knowledge service article creation failed")
        return None

    def get_attachment_download_url(self, article_id: int, filename: str) -> str:
        """Get the full download URL for an attachment."""
        return f"{self.base_url}{settings.API_V1_PREFIX}/attachments/file/{article_id}/{filename}"


# Singleton instance
knowledge_client = KnowledgeServiceClient()
