"""Repository implementations."""

from knowledge_service.repositories.implementations.article import ArticleRepository
from knowledge_service.repositories.implementations.article_change_history import ArticleChangeHistoryRepository
from knowledge_service.repositories.implementations.article_view import ArticleViewRepository
from knowledge_service.repositories.implementations.article_view_history import ArticleViewHistoryRepository
from knowledge_service.repositories.implementations.attachment import AttachmentRepository
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.implementations.category import CategoryRepository
from knowledge_service.repositories.implementations.category_change_history import CategoryChangeHistoryRepository
from knowledge_service.repositories.implementations.dialogue import DialogueScenarioRepository, DialogueStepRepository
from knowledge_service.repositories.implementations.dialogue_scenario_change_history import DialogueScenarioChangeHistoryRepository
from knowledge_service.repositories.implementations.search_history import SearchHistoryRepository
from knowledge_service.repositories.implementations.tag import TagRepository

__all__ = [
    "ArticleRepository",
    "ArticleChangeHistoryRepository",
    "ArticleViewHistoryRepository",
    "ArticleViewRepository",
    "AttachmentRepository",
    "CategoryChangeHistoryRepository",
    "CategoryRepository",
    "DialogueScenarioChangeHistoryRepository",
    "DialogueScenarioRepository",
    "DialogueStepRepository",
    "SearchHistoryRepository",
    "SqlAlchemyBaseRepository",
    "TagRepository",
]
