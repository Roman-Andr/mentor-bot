"""Repository interfaces."""

from knowledge_service.repositories.interfaces.article import IArticleRepository
from knowledge_service.repositories.interfaces.article_view import IArticleViewRepository
from knowledge_service.repositories.interfaces.attachment import IAttachmentRepository
from knowledge_service.repositories.interfaces.base import BaseRepository
from knowledge_service.repositories.interfaces.category import ICategoryRepository
from knowledge_service.repositories.interfaces.search_history import ISearchHistoryRepository
from knowledge_service.repositories.interfaces.tag import ITagRepository

__all__ = [
    "BaseRepository",
    "IArticleRepository",
    "IArticleViewRepository",
    "IAttachmentRepository",
    "ICategoryRepository",
    "ISearchHistoryRepository",
    "ITagRepository",
]
