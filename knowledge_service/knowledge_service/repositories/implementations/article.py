"""SQLAlchemy implementation of Article repository."""

from collections.abc import Sequence
from datetime import date, timedelta
from typing import cast

from sqlalchemy import Column, and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import text

from knowledge_service.core import ArticleStatus
from knowledge_service.models import Article
from knowledge_service.models.article_view import ArticleView
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.article import IArticleRepository


class ArticleRepository(SqlAlchemyBaseRepository[Article, int], IArticleRepository):
    """SQLAlchemy implementation of Article repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize article repository."""
        super().__init__(session, Article)

    async def create(self, entity: Article) -> Article:
        """Create article with eager-loaded relations."""
        self._session.add(entity)
        await self._session.flush()
        stmt = (
            select(Article)
            .where(Article.id == entity.id)
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update(self, entity: Article) -> Article:
        """Update article with eager-loaded relations."""
        await self._session.flush()
        stmt = (
            select(Article)
            .where(Article.id == entity.id)
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_by_slug(self, slug: str) -> Article | None:
        """Retrieve article by slug with relations."""
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
        """Retrieve article by ID with category, tags, and attachments."""
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

    def _get_sort_column(self, sort_by: str | None) -> Column:
        """Get SQLAlchemy column for sorting."""
        column_map = {
            "title": Article.title,
            "slug": Article.slug,
            "status": Article.status,
            "createdAt": Article.created_at,
            "updatedAt": Article.updated_at,
            "publishedAt": Article.published_at,
            "viewCount": Article.view_count,
            "isPinned": Article.is_pinned,
            "isFeatured": Article.is_featured,
            "department": Article.department_id,
            "category": Article.category_id,
        }
        return column_map.get(sort_by, Article.created_at)

    async def find_articles(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
        tag_id: int | None = None,
        department_id: int | None = None,
        status: str | None = None,
        search: str | None = None,
        user_filters: dict | None = None,
        featured_only: bool = False,
        pinned_only: bool = False,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[Sequence[Article], int]:
        """Find articles with filters and return total count."""
        stmt = select(Article)
        count_stmt = select(func.count(Article.id))

        if category_id:
            stmt = stmt.where(Article.category_id == category_id)
            count_stmt = count_stmt.where(Article.category_id == category_id)

        if tag_id:
            stmt = stmt.where(Article.tags.any(id=tag_id))
            count_stmt = count_stmt.where(Article.tags.any(id=tag_id))

        if department_id:
            stmt = stmt.where(Article.department_id == department_id)
            count_stmt = count_stmt.where(Article.department_id == department_id)

        if status:
            stmt = stmt.where(Article.status == status)
            count_stmt = count_stmt.where(Article.status == status)

        if search:
            search_filter = or_(
                Article.title.ilike(f"%{search}%"),
                Article.content.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        if featured_only:
            stmt = stmt.where(Article.is_featured)
            count_stmt = count_stmt.where(Article.is_featured)

        if pinned_only:
            stmt = stmt.where(Article.is_pinned)
            count_stmt = count_stmt.where(Article.is_pinned)

        if user_filters:
            filters = []
            if user_filters.get("department_id"):
                filters.append(Article.department_id == user_filters["department_id"])
            if user_filters.get("position"):
                filters.append(Article.position == user_filters["position"])
            if user_filters.get("level"):
                filters.append(Article.level == user_filters["level"])
            if filters:
                stmt = stmt.where(or_(*filters))
                count_stmt = count_stmt.where(or_(*filters))

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        # Apply sorting
        sort_column = self._get_sort_column(sort_by)

        stmt = (
            stmt.options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
            .offset(skip)
            .limit(limit)
        )

        # Apply order - pinned articles first if sorting by createdAt or publishedAt
        if sort_by in ("createdAt", "publishedAt", None):
            if sort_order.lower() == "asc":
                stmt = stmt.order_by(Article.is_pinned.desc(), sort_column.asc())
            else:
                stmt = stmt.order_by(Article.is_pinned.desc(), sort_column.desc())
        elif sort_order.lower() == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    async def find_department_articles(
        self, department_id: int, *, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[Article], int]:
        """Find published articles for a department."""
        condition = and_(
            Article.department_id == department_id,
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
        """Check if slug exists, optionally excluding an article ID."""
        stmt = select(Article).where(Article.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Article.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def increment_view_count(self, article_id: int) -> None:
        """Increment view count for an article."""
        stmt = update(Article).where(Article.id == article_id).values(view_count=Article.view_count + 1)
        await self._session.execute(stmt)

    async def update_search_vector(self, article_id: int) -> None:
        """Update full-text search vector for an article."""
        stmt = text("""
            UPDATE articles
            SET search_vector =
                setweight(to_tsvector('russian', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('russian', coalesce(content, '')), 'B') ||
                setweight(to_tsvector('russian', coalesce(excerpt, '')), 'C')
            WHERE id = :article_id
        """)
        await self._session.execute(stmt, {"article_id": article_id})

    async def get_daily_views(self, article_id: int, start_date: date) -> dict[date, int]:
        """Get daily view counts for an article since start date."""
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
        """Get view count for the 7 days before a given date."""
        stmt = select(func.count(ArticleView.id)).where(
            and_(
                ArticleView.article_id == article_id,
                func.date(ArticleView.viewed_at) >= before_date - timedelta(days=6),
                func.date(ArticleView.viewed_at) < before_date,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

    async def get_by_ids(self, article_ids: list[int]) -> Sequence[Article]:
        """Get multiple articles by their IDs."""
        if not article_ids:
            return []
        stmt = (
            select(Article)
            .where(Article.id.in_(article_ids))
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().unique().all()
