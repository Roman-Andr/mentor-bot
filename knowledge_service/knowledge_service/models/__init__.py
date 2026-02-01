"""Models package for the Knowledge Service."""

from knowledge_service.models.article import Article
from knowledge_service.models.association import article_tags
from knowledge_service.models.attachment import Attachment
from knowledge_service.models.category import Category
from knowledge_service.models.search_history import SearchHistory
from knowledge_service.models.tag import Tag

__all__ = [
    "Article",
    "Attachment",
    "Category",
    "SearchHistory",
    "Tag",
    "article_tags",
]
