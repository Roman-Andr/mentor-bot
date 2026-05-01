"""Search service for knowledge base with repository pattern."""

import json
import re
from typing import Any

from loguru import logger
from sqlalchemy import and_, case, func, literal, or_, select
from sqlalchemy.orm import selectinload

from knowledge_service.config import settings
from knowledge_service.core import ArticleStatus, SearchSortBy
from knowledge_service.models import Article, Tag
from knowledge_service.repositories import IUnitOfWork
from knowledge_service.utils import cache

MIN_QUERY_LENGTH = 2
MIN_WORD_LENGTH_HIGHLIGHT = 2


class SearchService:
    """Service for search operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize search service with Unit of Work."""
        self._uow = uow

    async def search_articles(
        self,
        query: str,
        filters: dict,
        sort_by: SearchSortBy,
        page: int,
        size: int,
        user_filters: dict | None = None,
        user_id: int | None = None,
    ) -> tuple[list[dict], int, list[str]]:
        """Search articles with full-text search and proper relevance scoring."""
        logger.debug(
            "Searching articles (query_present={}, page={}, size={}, user_id={})",
            bool(query.strip()),
            page,
            size,
            user_id,
        )
        filters_str = json.dumps(filters, sort_keys=True)
        cache_key = f"search:{query}:{filters_str}:{sort_by}:{page}:{size}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.debug("Search cache hit (query_present={}, total={})", bool(query.strip()), cached_result["total"])
            return (
                cached_result["results"],
                cached_result["total"],
                cached_result["suggestions"],
            )

        where_conditions = []

        if query.strip():
            ts_query = func.plainto_tsquery("russian", query)
            where_conditions.append(Article.search_vector.op("@@")(ts_query))
            rank_column = func.ts_rank(Article.search_vector, ts_query).label("relevance")
        else:
            rank_column = literal(1.0).label("relevance")

        if filters.get("category_id"):
            where_conditions.append(Article.category_id == filters["category_id"])
        if filters.get("tag_ids"):
            where_conditions.append(Article.tags.any(Tag.id.in_(filters["tag_ids"])))
        if filters.get("department_id"):
            where_conditions.append(Article.department_id == filters["department_id"])
        if filters.get("position"):
            where_conditions.append(Article.position == filters["position"])
        if filters.get("level"):
            where_conditions.append(Article.level == filters["level"])
        if filters.get("only_published", True):
            where_conditions.append(Article.status == ArticleStatus.PUBLISHED)

        if user_filters:
            user_filter_conditions = []
            if user_filters.get("department_id"):
                user_filter_conditions.append(Article.department_id == user_filters["department_id"])
            if user_filters.get("position"):
                user_filter_conditions.append(Article.position == user_filters["position"])
            if user_filters.get("level"):
                user_filter_conditions.append(Article.level == user_filters["level"])
            if user_filter_conditions:
                where_conditions.append(or_(*user_filter_conditions))

        session = self._uow.session

        count_stmt = select(func.count(Article.id))
        if where_conditions:
            count_stmt = count_stmt.where(and_(*where_conditions))
        result = await session.execute(count_stmt)
        total = result.scalar_one()

        id_stmt = select(Article.id, rank_column).where(and_(*where_conditions))

        if sort_by == SearchSortBy.RELEVANCE and query.strip():
            id_stmt = id_stmt.order_by(rank_column.desc())
        elif sort_by == SearchSortBy.DATE_NEWEST:
            id_stmt = id_stmt.order_by(Article.published_at.desc())
        elif sort_by == SearchSortBy.DATE_OLDEST:
            id_stmt = id_stmt.order_by(Article.published_at.asc())
        elif sort_by == SearchSortBy.VIEWS:
            id_stmt = id_stmt.order_by(Article.view_count.desc())
        elif sort_by == SearchSortBy.TITLE:
            id_stmt = id_stmt.order_by(Article.title.asc())

        skip = (page - 1) * size
        id_stmt = id_stmt.offset(skip).limit(size)

        result = await session.execute(id_stmt)
        rows = result.all()

        if not rows:
            empty_result = [], 0, []
            logger.info("Search returned no results (query_present={}, user_id={})", bool(query.strip()), user_id)
            if user_id:
                await self._uow.search_history.record_search(
                    user_id=user_id,
                    query=query,
                    results_count=0,
                    filters=filters,
                    department_id=user_filters.get("department_id") if user_filters else None,
                )
                await self._uow.commit()
            return empty_result

        article_ids = [row[0] for row in rows]
        relevance_map = {row[0]: float(row[1]) for row in rows}

        stmt = (
            select(Article)
            .where(Article.id.in_(article_ids))
            .options(
                selectinload(Article.category),
                selectinload(Article.tags),
                selectinload(Article.attachments),
            )
        )

        ordering = case({id_: index for index, id_ in enumerate(article_ids)}, value=Article.id)
        stmt = stmt.order_by(ordering)

        result = await session.execute(stmt)
        articles = result.scalars().unique().all()

        formatted_results = []
        for article in articles:
            relevance = relevance_map.get(article.id, 1.0)

            highlighted_content = None
            if query.strip():
                text_to_highlight = article.excerpt or article.content[:500]
                highlighted_content = self._highlight_text(text_to_highlight, query)

            formatted_results.append(
                {
                    "id": article.id,
                    "title": article.title,
                    "slug": article.slug,
                    "excerpt": article.excerpt,
                    "category_name": article.category.name if article.category else None,
                    "tags": [tag.name for tag in article.tags],
                    "relevance_score": round(relevance, 4),
                    "highlighted_content": highlighted_content,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                }
            )

        suggestions = []
        if query.strip():
            suggestions = await self.get_search_suggestions(query)

        if user_id:
            await self._uow.search_history.record_search(
                user_id=user_id,
                query=query,
                results_count=total,
                filters=filters,
                department_id=user_filters.get("department_id") if user_filters else None,
            )
            await self._uow.commit()

        await cache.set(
            cache_key,
            {
                "results": formatted_results,
                "total": total,
                "suggestions": suggestions,
            },
            ttl=settings.SEARCH_CACHE_TTL,
        )

        logger.info(
            "Search completed (query_present={}, total={}, returned={})",
            bool(query.strip()),
            total,
            len(formatted_results),
        )
        return formatted_results, total, suggestions

    async def get_search_suggestions(
        self,
        query: str,
        department_id: int | None = None,
        limit: int = 10,
    ) -> list[str]:
        """Get search suggestions based on query."""
        if not query or len(query) < MIN_QUERY_LENGTH:
            logger.debug("Skipping suggestions: query too short")
            return []

        cache_key = f"suggestions:{query}:{department_id}"
        cached = await cache.get(cache_key)
        if cached:
            logger.debug("Search suggestions cache hit (department_id={})", department_id)
            return cached

        search_suggestions = await self._uow.search_history.get_suggestions(query, department_id, limit)
        suggestions = list(search_suggestions)

        if len(suggestions) < limit:
            session = self._uow.session
            title_conditions = [
                Article.title.ilike(f"%{query}%"),
                Article.status == ArticleStatus.PUBLISHED,
            ]
            if department_id is not None:
                title_conditions.append(Article.department_id == department_id)

            stmt = select(Article.title).where(and_(*title_conditions)).limit(limit - len(suggestions))
            result = await session.execute(stmt)
            title_suggestions = [row[0] for row in result.all()]
            suggestions.extend(title_suggestions)

        suggestions = list(dict.fromkeys(suggestions))[:limit]

        await cache.set(cache_key, suggestions, ttl=settings.SEARCH_SUGGESTIONS_CACHE_TTL)

        logger.debug("Search suggestions generated (count={}, department_id={})", len(suggestions), department_id)
        return suggestions

    async def get_popular_searches(
        self,
        department_id: int | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Get popular searches."""
        cache_key = f"popular_searches:{department_id}"
        cached = await cache.get(cache_key)
        if cached:
            logger.debug("Popular searches cache hit (department_id={})", department_id)
            return cached

        popular = await self._uow.search_history.get_popular_searches(department_id, limit)
        await cache.set(cache_key, popular, ttl=settings.POPULAR_SEARCHES_CACHE_TTL)

        logger.debug("Popular searches fetched (count={}, department_id={})", len(popular), department_id)
        return popular

    async def get_user_search_history(self, user_id: int, skip: int = 0, limit: int = 50) -> tuple[list, int]:
        """Get user's search history."""
        items, total = await self._uow.search_history.find_by_user(user_id, skip=skip, limit=limit)
        logger.debug("User search history fetched (user_id={}, count={}, total={})", user_id, len(items), total)
        return list(items), total

    async def clear_user_search_history(self, user_id: int) -> None:
        """Clear user's search history."""
        await self._uow.search_history.clear_user_history(user_id)
        await self._uow.commit()
        logger.info("User search history cleared (user_id={})", user_id)

    async def get_search_stats(self) -> dict[str, Any]:
        """Get search statistics."""
        stats = await self._uow.search_history.get_search_stats()
        logger.debug("Search stats fetched")
        return stats

    def _highlight_text(self, text: str, query: str) -> str:
        """Highlight search terms in text."""
        if not text or not query:
            return text

        words = re.split(r"\s+", query)
        highlighted = text

        for word in words:
            if len(word) >= MIN_WORD_LENGTH_HIGHLIGHT:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                highlighted = pattern.sub(f"<mark>{word}</mark>", highlighted)

        return highlighted
