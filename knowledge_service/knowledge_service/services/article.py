"""Article management service with repository pattern."""

from datetime import UTC, datetime, timedelta
from typing import Any

from slugify import slugify

from knowledge_service.core import ArticleStatus, NotFoundException
from knowledge_service.models import Article
from knowledge_service.repositories import IUnitOfWork
from knowledge_service.schemas import ArticleCreate, ArticleUpdate


class ArticleService:
    """Service for article management operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize article service with Unit of Work."""
        self._uow = uow

    async def create_article(self, article_data: ArticleCreate, author_id: int, author_name: str) -> Article:
        """Create new article."""
        base_slug = slugify(article_data.title)
        slug = base_slug
        counter = 1
        while await self._uow.articles.slug_exists(slug):
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

        created = await self._uow.articles.create(article)

        if article_data.tag_ids:
            tags = await self._uow.tags.get_all()
            matched_tags = [t for t in tags if t.id in article_data.tag_ids]
            if matched_tags:
                for tag in matched_tags:
                    tag.usage_count += 1
                    await self._uow.tags.update(tag)
                created.tags.extend(matched_tags)

        if article_data.status == ArticleStatus.PUBLISHED:
            created.published_at = datetime.now(UTC)

        await self._uow.articles.update_search_vector(created.id)
        await self._uow.commit()

        return await self._uow.articles.get_by_id_with_relations(created.id)

    async def get_article_by_id(self, article_id: int) -> Article:
        """Get article by ID."""
        article = await self._uow.articles.get_by_id_with_relations(article_id)
        if not article:
            msg = "Article"
            raise NotFoundException(msg)
        return article

    async def get_article_by_slug(self, slug: str) -> Article:
        """Get article by slug."""
        article = await self._uow.articles.get_by_slug(slug)
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
            while await self._uow.articles.slug_exists(slug, exclude_id=article_id):
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
                await self._uow.tags.update(tag)
                article.tags.remove(tag)

            if update_dict["tag_ids"]:
                tags = await self._uow.tags.get_all()
                matched_tags = [t for t in tags if t.id in update_dict["tag_ids"]]
                if matched_tags:
                    article.tags.extend(matched_tags)
                    for tag in matched_tags:
                        tag.usage_count += 1
                        await self._uow.tags.update(tag)

        article.updated_at = datetime.now(UTC)
        await self._uow.articles.update_search_vector(article.id)
        updated = await self._uow.articles.update(article)
        await self._uow.commit()
        return updated

    async def delete_article(self, article_id: int) -> None:
        """Delete article."""
        article = await self.get_article_by_id(article_id)

        for tag in list(article.tags):
            tag.usage_count -= 1
            await self._uow.tags.update(tag)

        await self._uow.articles.delete(article_id)
        await self._uow.commit()

    async def get_articles(
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
        items, total = await self._uow.articles.find_articles(
            skip=skip,
            limit=limit,
            category_id=category_id,
            tag_id=tag_id,
            department=department,
            status=status,
            featured_only=featured_only,
            pinned_only=pinned_only,
            user_filters=user_filters,
        )
        return list(items), total

    async def publish_article(self, article_id: int) -> Article:
        """Publish article."""
        article = await self.get_article_by_id(article_id)

        article.status = ArticleStatus.PUBLISHED
        article.published_at = datetime.now(UTC)
        article.updated_at = datetime.now(UTC)

        await self._uow.articles.update(article)
        await self._uow.commit()

        return await self.get_article_by_id(article_id)

    async def record_view(self, article_id: int, user_id: int | None = None) -> None:
        """Record article view and increment counter."""
        await self._uow.articles.increment_view_count(article_id)
        await self._uow.article_views.record_view(article_id, user_id)
        await self._uow.commit()

    async def get_department_articles(
        self, department: str, skip: int = 0, limit: int = 50
    ) -> tuple[list[Article], int]:
        """Get articles for specific department."""
        items, total = await self._uow.articles.find_department_articles(department, skip=skip, limit=limit)
        return list(items), total

    async def get_article_stats(self, article_id: int) -> dict[str, Any]:
        """Get detailed view statistics for an article."""
        article = await self.get_article_by_id(article_id)

        end_date = datetime.now(UTC).date()
        start_date = end_date - timedelta(days=6)

        daily = await self._uow.articles.get_daily_views(article_id, start_date)

        daily_views = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            daily_views.append(
                {
                    "date": day.isoformat(),
                    "count": daily.get(day, 0),
                }
            )

        total_last_7 = sum(item["count"] for item in daily_views)
        total_previous_7 = await self._uow.articles.get_previous_week_views(article_id, start_date - timedelta(days=7))
        weekly_growth = 0.0
        if total_previous_7 > 0:
            weekly_growth = ((total_last_7 - total_previous_7) / total_previous_7) * 100

        return {
            "article_id": article.id,
            "title": article.title,
            "view_count": article.view_count,
            "daily_views": daily_views,
            "weekly_growth": round(weekly_growth, 2),
            "popular_tags": [tag.name for tag in article.tags],
        }
