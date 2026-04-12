"""API endpoint routers."""

from knowledge_service.api.endpoints.articles import router as articles_router
from knowledge_service.api.endpoints.categories import router as categories_router
from knowledge_service.api.endpoints.departments import router as departments_router
from knowledge_service.api.endpoints.search import router as search_router
from knowledge_service.api.endpoints.tags import router as tags_router

__all__ = [
    "articles_router",
    "categories_router",
    "departments_router",
    "search_router",
    "tags_router",
]
