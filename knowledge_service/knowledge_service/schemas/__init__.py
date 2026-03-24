"""Pydantic schemas for request/response validation."""

from knowledge_service.schemas.article import (
    ArticleBase,
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
    ArticleViewStats,
)
from knowledge_service.schemas.attachment import (
    AttachmentBase,
    AttachmentCreate,
    AttachmentListResponse,
    AttachmentResponse,
)
from knowledge_service.schemas.category import (
    CategoryBase,
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
    CategoryWithArticles,
)
from knowledge_service.schemas.responses import (
    HealthCheck,
    MessageResponse,
    ServiceStatus,
)
from knowledge_service.schemas.search import (
    SearchHistoryResponse,
    SearchQuery,
    SearchResponse,
    SearchStats,
)
from knowledge_service.schemas.tag import TagBase, TagCreate, TagResponse, TagUpdate

__all__ = [
    "ArticleBase",
    "ArticleCreate",
    "ArticleListResponse",
    "ArticleResponse",
    "ArticleUpdate",
    "ArticleViewStats",
    "AttachmentBase",
    "AttachmentCreate",
    "AttachmentListResponse",
    "AttachmentResponse",
    "CategoryBase",
    "CategoryCreate",
    "CategoryListResponse",
    "CategoryResponse",
    "CategoryUpdate",
    "CategoryWithArticles",
    "HealthCheck",
    "MessageResponse",
    "SearchHistoryResponse",
    "SearchQuery",
    "SearchResponse",
    "SearchStats",
    "ServiceStatus",
    "TagBase",
    "TagCreate",
    "TagResponse",
    "TagUpdate",
]
