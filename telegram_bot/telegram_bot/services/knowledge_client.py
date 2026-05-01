"""HTTP client for knowledge service integration."""

import httpx
from fastapi import status
from loguru import logger

from telegram_bot.config import settings
from telegram_bot.schemas.search import SearchResponse
from telegram_bot.utils.cache import cached


class KnowledgeServiceClient:
    """HTTP client for knowledge service integration."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize knowledge service HTTP client."""
        self.base_url = base_url or settings.KNOWLEDGE_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT)

    @cached(ttl=30, key_prefix="kb_search")
    async def search_articles(self, query: str, auth_token: str, page: int = 1, size: int = 5) -> SearchResponse:
        """Search articles in knowledge base (cached)."""
        logger.debug("Searching articles (query={}, page={}, size={})", query, page, size)
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
                logger.debug("Articles searched (query={}, total={})", query, response.json().get("total", 0))
                return SearchResponse(**response.json())
        except httpx.RequestError:
            logger.exception("Knowledge service search request failed (query={})", query)
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
    async def get_search_suggestions(self, query: str, auth_token: str, limit: int = 10) -> list[str]:
        """Get search suggestions (cached)."""
        logger.debug("Fetching search suggestions (query={}, limit={})", query, limit)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/search/suggest",
                params={"query": query, "limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("Search suggestions fetched (query={}, count={})", query, len(response.json()))
                return response.json()
        except httpx.RequestError:
            logger.exception("Knowledge service suggestions request failed (query={})", query)
        return []

    async def get_article_details(self, article_id: int, auth_token: str) -> dict | None:
        """Get article details by ID."""
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
            logger.exception("Knowledge service article details request failed (article_id={})", article_id)
        return None

    @cached(ttl=30, key_prefix="kb_attachments")
    async def get_article_attachments(self, article_id: int, auth_token: str) -> list[dict]:
        """Get all attachments for an article (cached)."""
        logger.debug("Fetching article attachments (article_id={})", article_id)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/attachments/article/{article_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                logger.debug(
                    "Article attachments fetched (article_id={}, count={})",
                    article_id,
                    len(data.get("attachments", [])),
                )
                return data.get("attachments", [])
        except httpx.RequestError:
            logger.exception("Knowledge service attachments request failed (article_id={})", article_id)
        return []

    async def download_attachment(self, article_id: int, filename: str, auth_token: str) -> bytes | None:
        """Download attachment file content."""
        logger.debug("Downloading attachment (article_id={}, filename={})", article_id, filename)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/attachments/file/{article_id}/{filename}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.info("Attachment downloaded (article_id={}, filename={})", article_id, filename)
                return response.content
            logger.warning("Attachment download failed (article_id={}, filename={})", article_id, filename)
        except httpx.RequestError:
            logger.exception(
                "Knowledge service file download failed (article_id={}, filename={})", article_id, filename
            )
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
        logger.debug("Uploading attachment (article_id={}, filename={})", article_id, filename)
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
                logger.info("Attachment uploaded (article_id={}, filename={})", article_id, filename)
                return response.json()
            logger.warning("Attachment upload failed (article_id={}, filename={})", article_id, filename)
        except httpx.RequestError:
            logger.exception("Knowledge service file upload failed (article_id={}, filename={})", article_id, filename)
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
        logger.info("Creating article (title={})", title)
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
                logger.info("Article created (title={})", title)
                return response.json()
            logger.warning("Article creation failed (title={})", title)
        except httpx.RequestError:
            logger.exception("Knowledge service article creation failed (title={})", title)
        return None

    def get_attachment_download_url(self, article_id: int, filename: str) -> str:
        """Get the full download URL for an attachment."""
        return f"{self.base_url}{settings.API_V1_PREFIX}/attachments/file/{article_id}/{filename}"

    @cached(ttl=300, key_prefix="faq_scenarios")
    async def get_active_scenarios(self, skip: int = 0, limit: int = 50) -> dict:
        """Get active dialogue scenarios for FAQ menu (cached)."""
        logger.debug("Fetching active scenarios (skip={}, limit={})", skip, limit)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/dialogue-scenarios/active",
                params={"skip": skip, "limit": limit},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("Active scenarios fetched (count={})", len(response.json().get("scenarios", [])))
                return response.json()
        except httpx.RequestError:
            logger.exception("Knowledge service get active scenarios request failed")
        return {"total": 0, "scenarios": [], "page": 1, "size": limit, "pages": 0}

    @cached(ttl=300, key_prefix="faq_scenario")
    async def get_scenario(self, scenario_id: int) -> dict:
        """Get dialogue scenario by ID with steps (cached)."""
        logger.debug("Fetching scenario (scenario_id={})", scenario_id)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/dialogue-scenarios/{scenario_id}",
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("Scenario fetched (scenario_id={})", scenario_id)
                return response.json()
            logger.warning("Scenario not found (scenario_id={})", scenario_id)
        except httpx.RequestError:
            logger.exception("Knowledge service get scenario request failed (scenario_id={})", scenario_id)
        return {"id": scenario_id, "title": "", "steps": []}

    @cached(ttl=300, key_prefix="kb_categories")
    async def get_categories(self, auth_token: str, skip: int = 0, limit: int = 50) -> dict:
        """Get knowledge base categories (cached)."""
        logger.debug("Fetching categories (skip={}, limit={})", skip, limit)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/categories",
                params={"skip": skip, "limit": limit},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug("Categories fetched (count={})", len(response.json().get("categories", [])))
                return response.json()
        except httpx.RequestError:
            logger.exception("Knowledge service categories request failed")
        return {"total": 0, "categories": [], "page": 1, "size": limit, "pages": 0}

    @cached(ttl=60, key_prefix="kb_category_articles")
    async def get_articles_by_category(self, category_id: int, auth_token: str, skip: int = 0, limit: int = 20) -> dict:
        """Get articles by category ID (cached)."""
        logger.debug("Fetching articles by category (category_id={}, skip={}, limit={})", category_id, skip, limit)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/articles",
                params={
                    "category_id": category_id,
                    "skip": skip,
                    "limit": limit,
                },
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if response.status_code == status.HTTP_200_OK:
                logger.debug(
                    "Articles by category fetched (category_id={}, count={})",
                    category_id,
                    len(response.json().get("articles", [])),
                )
                return response.json()
        except httpx.RequestError:
            logger.exception("Knowledge service articles by category request failed (category_id={})", category_id)
        return {"total": 0, "articles": [], "page": 1, "size": limit, "pages": 0}


# Singleton instance
knowledge_client = KnowledgeServiceClient()
