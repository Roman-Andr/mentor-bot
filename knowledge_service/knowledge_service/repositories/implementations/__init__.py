"""Repository implementations."""

from knowledge_service.repositories.implementations.article import ArticleRepository
from knowledge_service.repositories.implementations.article_view import ArticleViewRepository
from knowledge_service.repositories.implementations.attachment import AttachmentRepository
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.implementations.category import CategoryRepository
from knowledge_service.repositories.implementations.dialogue import DialogueScenarioRepository, DialogueStepRepository
from knowledge_service.repositories.implementations.search_history import SearchHistoryRepository
from knowledge_service.repositories.implementations.tag import TagRepository

__all__ = [
    "ArticleRepository",
    "ArticleViewRepository",
    "AttachmentRepository",
    "CategoryRepository",
    "DialogueScenarioRepository",
    "DialogueStepRepository",
    "SearchHistoryRepository",
    "SqlAlchemyBaseRepository",
    "TagRepository",
]
