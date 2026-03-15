"""SQLAlchemy implementation of Article repository."""

from collections.abc import Sequence
from datetime import date, timedelta
from typing import cast

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import text

from knowledge_service.config import settings
from knowledge_service.core import ArticleStatus
from knowledge_service.models import Article
from knowledge_service.models.article_view import ArticleView
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.article import IArticleRepository


class ArticleRepository(SqlAlchemyBaseRepository[Article, int], IArticleRepository):
    """SQLAlchemy implementation of Article repository."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Article)

    async def get_by_slug(self, slug: str) -> Article | None:
        stmt = (
            select(Article)
            .where(Article.slug == slug)
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(self, entity_id: int) -> Article | None:
        stmt = (
            select(Article)
            .where(Article.id == entity_id)
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_articles(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
        tag_id: int | None = None,
        department: str | None = None,
        status: str | None = None,
        user_filters: dict | None = None,
        featured_only: bool = False,
        pinned_only: bool = False,
    ) -> tuple[Sequence[Article], int]:
        stmt = select(Article)
        count_stmt = select(func.count(Article.id))

        if category_id:
            stmt = stmt.where(Article.category_id == category_id)
            count_stmt = count_stmt.where(Article.category_id == category_id)

        if tag_id:
            stmt = stmt.where(Article.tags.any(id=tag_id))
            count_stmt = count_stmt.where(Article.tags.any(id=tag_id))

        if department:
            stmt = stmt.where(Article.department == department)
            count_stmt = count_stmt.where(Article.department == department)

        if status:
            stmt = stmt.where(Article.status == status)
            count_stmt = count_stmt.where(Article.status == status)

        if featured_only:
            stmt = stmt.where(Article.is_featured)
            count_stmt = count_stmt.where(Article.is_featured)

        if pinned_only:
            stmt = stmt.where(Article.is_pinned)
            count_stmt = count_stmt.where(Article.is_pinned)

        if user_filters:
            filters = []
            if user_filters.get("department"):
                filters.append(Article.department == user_filters["department"])
            if user_filters.get("position"):
                filters.append(Article.position == user_filters["position"])
            if user_filters.get("level"):
                filters.append(Article.level == user_filters["level"])
            if filters:
                stmt = stmt.where(or_(*filters))
                count_stmt = count_stmt.where(or_(*filters))

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        stmt = (
            stmt.options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
            .order_by(Article.is_pinned.desc(), Article.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    async def find_department_articles(
        self, department: str, *, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[Article], int]:
        condition = and_(
            Article.department == department,
            Article.status == ArticleStatus.PUBLISHED,
        )
        stmt = select(Article).where(condition)
        count_stmt = select(func.count(Article.id)).where(condition)

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        stmt = (
            stmt.options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
            .order_by(Article.is_pinned.desc(), Article.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    async def slug_exists(self, slug: str, *, exclude_id: int | None = None) -> bool:
        stmt = select(Article).where(Article.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Article.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def increment_view_count(self, article_id: int) -> None:
        stmt = update(Article).where(Article.id == article_id).values(view_count=Article.view_count + 1)
        await self._session.execute(stmt)

    async def update_search_vector(self, article_id: int) -> None:
        stmt = text(f"""
            UPDATE {settings.DATABASE_SCHEMA}.articles
            SET search_vector =
                setweight(to_tsvector('russian', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('russian', coalesce(content, '')), 'B') ||
                setweight(to_tsvector('russian', coalesce(excerpt, '')), 'C')
            WHERE id = :article_id
        """)
        await self._session.execute(stmt, {"article_id": article_id})

    async def get_daily_views(self, article_id: int, start_date: date) -> dict[date, int]:
        stmt = (
            select(
                func.date(ArticleView.viewed_at).label("view_date"),
                func.count(ArticleView.id).label("count"),
            )
            .where(
                and_(
                    ArticleView.article_id == article_id,
                    func.date(ArticleView.viewed_at) >= start_date,
                )
            )
            .group_by(func.date(ArticleView.viewed_at))
            .order_by(func.date(ArticleView.viewed_at))
        )
        result = await self._session.execute(stmt)
        return {row.view_date: row.count for row in result.all()}

    async def get_previous_week_views(self, article_id: int, before_date: date) -> int:
        stmt = select(func.count(ArticleView.id)).where(
            and_(
                ArticleView.article_id == article_id,
                func.date(ArticleView.viewed_at) >= before_date - timedelta(days=6),
                func.date(ArticleView.viewed_at) < before_date,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one() or 0
