"""Internal maintenance endpoints for knowledge data."""

from fastapi import APIRouter
from sqlalchemy import delete, or_, select, update

from knowledge_service.api.deps import ServiceAuth, UOWDep
from knowledge_service.models import (
    Article,
    ArticleChangeHistory,
    ArticleView,
    ArticleViewHistory,
    CategoryChangeHistory,
    DepartmentDocument,
    DialogueScenarioChangeHistory,
    SearchHistory,
    article_tags,
)

router = APIRouter()


@router.delete("/users/{user_id}")
async def cleanup_user_knowledge_data(
    user_id: int,
    uow: UOWDep,
    _service_auth: ServiceAuth,
) -> dict[str, int]:
    """Remove knowledge-service data that belongs or points to a deleted user."""
    session = uow._session
    if session is None:
        msg = "Session not initialized"
        raise RuntimeError(msg)

    article_ids = list((await session.execute(select(Article.id).where(Article.author_id == user_id))).scalars())

    article_history = await session.execute(
        delete(ArticleChangeHistory).where(
            or_(ArticleChangeHistory.user_id == user_id, ArticleChangeHistory.changed_by == user_id)
        )
    )
    category_history = await session.execute(
        delete(CategoryChangeHistory).where(
            or_(CategoryChangeHistory.user_id == user_id, CategoryChangeHistory.changed_by == user_id)
        )
    )
    dialogue_history = await session.execute(
        delete(DialogueScenarioChangeHistory).where(
            or_(DialogueScenarioChangeHistory.user_id == user_id, DialogueScenarioChangeHistory.changed_by == user_id)
        )
    )
    search_history = await session.execute(delete(SearchHistory).where(SearchHistory.user_id == user_id))
    article_views = await session.execute(delete(ArticleView).where(ArticleView.user_id == user_id))
    article_view_history = await session.execute(
        delete(ArticleViewHistory).where(ArticleViewHistory.user_id == user_id)
    )
    department_documents = await session.execute(
        delete(DepartmentDocument).where(DepartmentDocument.uploaded_by == user_id)
    )

    deleted_articles = 0
    if article_ids:
        article_history_by_article = await session.execute(
            delete(ArticleChangeHistory).where(ArticleChangeHistory.article_id.in_(article_ids))
        )
        views_by_article = await session.execute(delete(ArticleView).where(ArticleView.article_id.in_(article_ids)))
        view_history_by_article = await session.execute(
            delete(ArticleViewHistory).where(ArticleViewHistory.article_id.in_(article_ids))
        )
        await session.execute(delete(article_tags).where(article_tags.c.article_id.in_(article_ids)))
        articles = await session.execute(delete(Article).where(Article.id.in_(article_ids)))
        article_history_count = article_history_by_article.rowcount or 0
        article_views_count = views_by_article.rowcount or 0
        article_view_history_count = view_history_by_article.rowcount or 0
        deleted_articles = articles.rowcount or 0
    else:
        article_history_count = 0
        article_views_count = 0
        article_view_history_count = 0

    anonymized = await session.execute(
        update(Article).where(Article.author_id == user_id).values(author_name="Deleted User")
    )

    await uow.commit()
    return {
        "articles": deleted_articles,
        "anonymized_articles": anonymized.rowcount or 0,
        "article_history": (article_history.rowcount or 0) + article_history_count,
        "category_history": category_history.rowcount or 0,
        "dialogue_history": dialogue_history.rowcount or 0,
        "search_history": search_history.rowcount or 0,
        "article_views": (article_views.rowcount or 0) + article_views_count,
        "article_view_history": (article_view_history.rowcount or 0) + article_view_history_count,
        "department_documents": department_documents.rowcount or 0,
    }
