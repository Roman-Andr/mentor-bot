"""Repository pattern for knowledge_service data access."""

from knowledge_service.repositories.implementations import (
    ArticleRepository,
    ArticleViewRepository,
    AttachmentRepository,
    CategoryRepository,
    SearchHistoryRepository,
    SqlAlchemyBaseRepository,
    TagRepository,
)
from knowledge_service.repositories.interfaces import (
    BaseRepository,
    IArticleRepository,
    IArticleViewRepository,
    IAttachmentRepository,
    ICategoryRepository,
    ISearchHistoryRepository,
    ITagRepository,
)
from knowledge_service.repositories.unit_of_work import (
    IUnitOfWork,
    SqlAlchemyUnitOfWork,
    sqlalchemy_uow,
)

__all__ = [
    "ArticleRepository",
    "ArticleViewRepository",
    "AttachmentRepository",
    "BaseRepository",
    "CategoryRepository",
    "IArticleRepository",
    "IArticleViewRepository",
    "IAttachmentRepository",
    "ICategoryRepository",
    "ISearchHistoryRepository",
    "ITagRepository",
    "IUnitOfWork",
    "SearchHistoryRepository",
    "SqlAlchemyBaseRepository",
    "SqlAlchemyUnitOfWork",
    "TagRepository",
    "sqlalchemy_uow",
]
