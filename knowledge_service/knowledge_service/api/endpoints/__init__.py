"""API endpoint routers."""

from knowledge_service.api.endpoints.articles import router as articles_router
from knowledge_service.api.endpoints.audit import router as audit_router
from knowledge_service.api.endpoints.categories import router as categories_router
from knowledge_service.api.endpoints.search import router as search_router
from knowledge_service.api.endpoints.tags import router as tags_router

__all__ = [
    "articles_router",
    "audit_router",
    "categories_router",
    "search_router",
    "tags_router",
]
