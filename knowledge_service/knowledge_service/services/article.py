"""Article management service."""

from datetime import UTC, datetime
from typing import Any

from slugify import slugify
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import text

from knowledge_service.config import settings
from knowledge_service.core import ArticleStatus, NotFoundException
from knowledge_service.models import Article, Tag
from knowledge_service.schemas import ArticleCreate, ArticleUpdate


class ArticleService:
    """Service for article management operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize article service with database session."""
        self.db = db

    async def create_article(self, article_data: ArticleCreate, author_id: int, author_name: str) -> Article:
        """Create new article."""
        base_slug = slugify(article_data.title)
        slug = base_slug

        counter = 1
        while True:
            stmt = select(Article).where(Article.slug == slug)
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                break

            slug = f"{base_slug}-{counter}"
            counter += 1

        article = Article(
            title=article_data.title,
            slug=slug,
            content=article_data.content,
            excerpt=article_data.excerpt,
            category_id=article_data.category_id,
            author_id=author_id,
            author_name=author_name,
            department=article_data.department,
            position=article_data.position,
            level=article_data.level,
            status=article_data.status,
            is_pinned=article_data.is_pinned,
            is_featured=article_data.is_featured,
            meta_title=article_data.meta_title,
            meta_description=article_data.meta_description,
            keywords=article_data.keywords,
        )

        self.db.add(article)
        await self.db.flush()

        if article_data.tag_ids:
            stmt = select(Tag).where(Tag.id.in_(article_data.tag_ids))
            result = await self.db.execute(stmt)
            tags = list(result.scalars().all())

            if tags:
                article.tags.extend(tags)

                for tag in tags:
                    tag.usage_count += 1

        if article_data.status == ArticleStatus.PUBLISHED:
            article.published_at = datetime.now(UTC)

        await self._update_search_vector(article.id)

        await self.db.commit()
        await self.db.refresh(article)

        stmt = (
            select(Article)
            .where(Article.id == article.id)
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_article_by_id(self, article_id: int) -> Article:
        """Get article by ID."""
        stmt = (
            select(Article)
            .where(Article.id == article_id)
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
        )
        result = await self.db.execute(stmt)
        article = result.scalar_one_or_none()

        if not article:
            msg = "Article"
            raise NotFoundException(msg)

        return article

    async def get_article_by_slug(self, slug: str) -> Article:
        """Get article by slug."""
        stmt = (
            select(Article)
            .where(Article.slug == slug)
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
        )
        result = await self.db.execute(stmt)
        article = result.scalar_one_or_none()

        if not article:
            msg = "Article"
            raise NotFoundException(msg)

        return article

    async def update_article(self, article_id: int, update_data: ArticleUpdate) -> Article:
        """Update article."""
        article = await self.get_article_by_id(article_id)

        update_dict = update_data.model_dump(exclude_unset=True)

        if "title" in update_dict and update_dict["title"] != article.title:
            base_slug = slugify(update_dict["title"])
            slug = base_slug

            counter = 1
            while True:
                stmt = select(Article).where(Article.slug == slug, Article.id != article_id)
                result = await self.db.execute(stmt)
                existing = result.scalar_one_or_none()

                if not existing:
                    break

                slug = f"{base_slug}-{counter}"
                counter += 1

            article.slug = slug
            article.title = update_dict["title"]

        if (
            "status" in update_dict
            and update_dict["status"] == ArticleStatus.PUBLISHED
            and article.status != ArticleStatus.PUBLISHED
        ):
            article.published_at = datetime.now(UTC)

        for field, value in update_dict.items():
            if field not in ["title", "status", "tag_ids"]:
                setattr(article, field, value)

        if "tag_ids" in update_dict:
            for tag in list(article.tags):
                tag.usage_count -= 1
                article.tags.remove(tag)

            if update_dict["tag_ids"]:
                stmt = select(Tag).where(Tag.id.in_(update_dict["tag_ids"]))
                result = await self.db.execute(stmt)
                tags = list(result.scalars().all())

                if tags:
                    article.tags.extend(tags)

                    for tag in tags:
                        tag.usage_count += 1

        article.updated_at = datetime.now(UTC)

        await self._update_search_vector(article.id)

        await self.db.commit()
        await self.db.refresh(article)

        return await self.get_article_by_id(article_id)

    async def delete_article(self, article_id: int) -> None:
        """Delete article."""
        article = await self.get_article_by_id(article_id)

        for tag in list(article.tags):
            tag.usage_count -= 1

        await self.db.delete(article)
        await self.db.commit()

    async def get_articles(  # noqa: PLR0913
        self,
        skip: int = 0,
        limit: int = 50,
        category_id: int | None = None,
        tag_id: int | None = None,
        department: str | None = None,
        status: str | None = None,
        user_filters: dict | None = None,
        *,
        featured_only: bool = False,
        pinned_only: bool = False,
    ) -> tuple[list[Article], int]:
        """Get paginated list of articles with filters."""
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

        # Apply user-specific filters (for non-admins)
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

        # Get total count
        result = await self.db.execute(count_stmt)
        total = result.scalar_one()

        # Get paginated results with relationships
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
        result = await self.db.execute(stmt)
        articles = list(result.scalars().all())

        return articles, total

    async def publish_article(self, article_id: int) -> Article:
        """Publish article."""
        article = await self.get_article_by_id(article_id)

        article.status = ArticleStatus.PUBLISHED
        article.published_at = datetime.now(UTC)
        article.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(article)

        # Return article with loaded relationships
        return await self.get_article_by_id(article_id)

    async def record_view(self, article_id: int) -> None:
        """Record article view."""
        stmt = update(Article).where(Article.id == article_id).values(view_count=Article.view_count + 1)
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_department_articles(
        self, department: str, skip: int = 0, limit: int = 50
    ) -> tuple[list[Article], int]:
        """Get articles for specific department."""
        stmt = select(Article).where(
            and_(
                Article.department == department,
                Article.status == ArticleStatus.PUBLISHED,
            )
        )
        count_stmt = select(func.count(Article.id)).where(
            and_(
                Article.department == department,
                Article.status == ArticleStatus.PUBLISHED,
            )
        )

        result = await self.db.execute(count_stmt)
        total = result.scalar_one()

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
        result = await self.db.execute(stmt)
        articles = list(result.scalars().all())

        return articles, total

    async def get_article_stats(self, article_id: int) -> dict[str, Any]:
        """Get article view statistics."""
        article = await self.get_article_by_id(article_id)

        daily_views = []
        tag_names = [tag.name for tag in article.tags]

        return {
            "article_id": article.id,
            "title": article.title,
            "view_count": article.view_count,
            "daily_views": daily_views,
            "weekly_growth": 0.0,
            "popular_tags": tag_names,
        }

    async def _update_search_vector(self, article_id: int) -> None:
        """Update search vector for article."""
        # Update the search vector column using PostgreSQL full-text search
        update_stmt = text(f"""
            UPDATE {settings.DATABASE_SCHEMA}.articles
            SET search_vector =
                setweight(to_tsvector('russian', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('russian', coalesce(content, '')), 'B') ||
                setweight(to_tsvector('russian', coalesce(excerpt, '')), 'C')
            WHERE id = :article_id
        """)
        await self.db.execute(update_stmt, {"article_id": article_id})
