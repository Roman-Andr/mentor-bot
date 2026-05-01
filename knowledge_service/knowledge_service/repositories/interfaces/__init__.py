"""Repository interfaces."""

from knowledge_service.repositories.interfaces.article import IArticleRepository
from knowledge_service.repositories.interfaces.article_change_history import IArticleChangeHistoryRepository
from knowledge_service.repositories.interfaces.article_view import IArticleViewRepository
from knowledge_service.repositories.interfaces.article_view_history import IArticleViewHistoryRepository
from knowledge_service.repositories.interfaces.attachment import IAttachmentRepository
from knowledge_service.repositories.interfaces.base import BaseRepository
from knowledge_service.repositories.interfaces.category import ICategoryRepository
from knowledge_service.repositories.interfaces.category_change_history import ICategoryChangeHistoryRepository
from knowledge_service.repositories.interfaces.dialogue import IDialogueScenarioRepository, IDialogueStepRepository
from knowledge_service.repositories.interfaces.dialogue_scenario_change_history import (
    IDialogueScenarioChangeHistoryRepository,
)
from knowledge_service.repositories.interfaces.search_history import ISearchHistoryRepository
from knowledge_service.repositories.interfaces.tag import ITagRepository

__all__ = [
    "BaseRepository",
    "IArticleChangeHistoryRepository",
    "IArticleRepository",
    "IArticleViewHistoryRepository",
    "IArticleViewRepository",
    "IAttachmentRepository",
    "ICategoryChangeHistoryRepository",
    "ICategoryRepository",
    "IDialogueScenarioChangeHistoryRepository",
    "IDialogueScenarioRepository",
    "IDialogueStepRepository",
    "ISearchHistoryRepository",
    "ITagRepository",
]
