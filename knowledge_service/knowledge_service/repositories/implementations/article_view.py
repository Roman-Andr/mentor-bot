"""SQLAlchemy implementation of ArticleView repository."""

from datetime import datetime
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models.article import Article
from knowledge_service.models.article_view import ArticleView
from knowledge_service.models.association import article_tags
from knowledge_service.models.category import Category
from knowledge_service.models.tag import Tag
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.article_view import IArticleViewRepository


class ArticleViewRepository(SqlAlchemyBaseRepository[ArticleView, int], IArticleViewRepository):
    """SQLAlchemy implementation of ArticleView repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize article view repository."""
        super().__init__(session, ArticleView)

    async def record_view(self, article_id: int, user_id: int | None = None) -> ArticleView:
        """Record a view event for an article."""
        view = ArticleView(article_id=article_id, user_id=user_id)
        return await self.create(view)

    async def get_top_articles(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 10,
        department_id: int | None = None,
    ) -> list[dict[str, object]]:
        """Get top articles by view count."""
        query = (
            select(
                Article.id.label("article_id"),
                Article.title,
                func.count(ArticleView.id).label("view_count"),
                func.count(func.distinct(ArticleView.user_id)).label("unique_viewers"),
            )
            .join(ArticleView, Article.id == ArticleView.article_id)
            .group_by(Article.id, Article.title)
        )

        if from_date:
            query = query.where(ArticleView.viewed_at >= from_date)
        if to_date:
            query = query.where(ArticleView.viewed_at <= to_date)
        if department_id:
            query = query.where(Article.department_id == department_id)

        query = query.order_by(func.count(ArticleView.id).desc()).limit(limit)

        result = await self._session.execute(query)
        rows = result.all()

        return [
            {
                "article_id": row.article_id,
                "title": row.title,
                "view_count": row.view_count,
                "unique_viewers": row.unique_viewers or 0,
            }
            for row in rows
        ]

    async def get_timeseries(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        granularity: Literal["day", "week"] = "day",
        article_id: int | None = None,
    ) -> list[dict[str, object]]:
        """Get views timeseries data."""
        trunc_func = func.date_trunc(granularity, ArticleView.viewed_at)

        query = select(
            trunc_func.label("bucket"),
            func.count(ArticleView.id).label("views"),
            func.count(func.distinct(ArticleView.user_id)).label("unique_viewers"),
        ).group_by(trunc_func)

        if from_date:
            query = query.where(ArticleView.viewed_at >= from_date)
        if to_date:
            query = query.where(ArticleView.viewed_at <= to_date)
        if article_id:
            query = query.where(ArticleView.article_id == article_id)

        query = query.order_by(trunc_func)

        result = await self._session.execute(query)
        rows = result.all()

        return [
            {
                "bucket": row.bucket.isoformat() if row.bucket else "",
                "views": row.views,
                "unique_viewers": row.unique_viewers or 0,
            }
            for row in rows
        ]

    async def get_by_category(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[dict[str, object]]:
        """Get view statistics by category."""
        query = (
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                func.count(ArticleView.id).label("view_count"),
            )
            .join(Article, Category.id == Article.category_id, isouter=True)
            .join(ArticleView, Article.id == ArticleView.article_id)
            .group_by(Category.id, Category.name)
        )

        if from_date:
            query = query.where(ArticleView.viewed_at >= from_date)
        if to_date:
            query = query.where(ArticleView.viewed_at <= to_date)

        query = query.order_by(func.count(ArticleView.id).desc())

        result = await self._session.execute(query)
        rows = result.all()

        return [
            {
                "category_id": row.category_id,
                "category_name": row.category_name,
                "view_count": row.view_count,
            }
            for row in rows
        ]

    async def get_by_tag(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[dict[str, object]]:
        """Get view statistics by tag."""
        query = (
            select(
                Tag.id.label("tag_id"),
                Tag.name.label("tag_name"),
                func.count(ArticleView.id).label("view_count"),
            )
            .join(article_tags, Tag.id == article_tags.c.tag_id)
            .join(Article, article_tags.c.article_id == Article.id)
            .join(ArticleView, Article.id == ArticleView.article_id)
            .group_by(Tag.id, Tag.name)
        )

        if from_date:
            query = query.where(ArticleView.viewed_at >= from_date)
        if to_date:
            query = query.where(ArticleView.viewed_at <= to_date)

        query = query.order_by(func.count(ArticleView.id).desc())

        result = await self._session.execute(query)
        rows = result.all()

        return [
            {
                "tag_id": row.tag_id,
                "tag_name": row.tag_name,
                "view_count": row.view_count,
            }
            for row in rows
        ]

    async def get_summary_stats(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict[str, object]:
        """Get summary statistics for knowledge base."""
        # Total views
        views_query = select(func.count(ArticleView.id))
        if from_date:
            views_query = views_query.where(ArticleView.viewed_at >= from_date)
        if to_date:
            views_query = views_query.where(ArticleView.viewed_at <= to_date)
        total_views_result = await self._session.execute(views_query)
        total_views = total_views_result.scalar() or 0

        # Unique viewers
        viewers_query = select(func.count(func.distinct(ArticleView.user_id)))
        if from_date:
            viewers_query = viewers_query.where(ArticleView.viewed_at >= from_date)
        if to_date:
            viewers_query = viewers_query.where(ArticleView.viewed_at <= to_date)
        unique_viewers_result = await self._session.execute(viewers_query)
        unique_viewers = unique_viewers_result.scalar() or 0

        # Total articles
        total_articles_query = select(func.count(Article.id))
        total_articles_result = await self._session.execute(total_articles_query)
        total_articles = total_articles_result.scalar() or 0

        # Average views per article
        avg_views = total_views / total_articles if total_articles > 0 else 0.0

        return {
            "total_views": total_views,
            "unique_viewers": unique_viewers,
            "total_articles": total_articles,
            "avg_views_per_article": avg_views,
        }
