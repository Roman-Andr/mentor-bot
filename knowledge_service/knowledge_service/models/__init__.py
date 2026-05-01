"""SQLAlchemy models for knowledge service."""

from knowledge_service.models.article import Article
from knowledge_service.models.article_change_history import ArticleChangeHistory
from knowledge_service.models.article_view import ArticleView
from knowledge_service.models.article_view_history import ArticleViewHistory
from knowledge_service.models.association import article_tags
from knowledge_service.models.attachment import Attachment
from knowledge_service.models.category import Category
from knowledge_service.models.category_change_history import CategoryChangeHistory
from knowledge_service.models.dialogue import DialogueScenario, DialogueStep
from knowledge_service.models.dialogue_scenario_change_history import DialogueScenarioChangeHistory
from knowledge_service.models.search_history import SearchHistory
from knowledge_service.models.tag import Tag

__all__ = [
    "Article",
    "ArticleChangeHistory",
    "ArticleView",
    "ArticleViewHistory",
    "Attachment",
    "Category",
    "CategoryChangeHistory",
    "DialogueScenario",
    "DialogueScenarioChangeHistory",
    "DialogueStep",
    "SearchHistory",
    "Tag",
    "article_tags",
]
