# knowledge_service/knowledge_service/services/search.py
"""Search service for knowledge base."""

import json
import re
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, case, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from knowledge_service.config import settings
from knowledge_service.core import ArticleStatus, SearchSortBy
from knowledge_service.models import Article, SearchHistory, Tag
from knowledge_service.utils import cache


class SearchService:
    """Service for search operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize search service with database session."""
        self.db = db

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
        filters_str = json.dumps(filters, sort_keys=True)
        cache_key = f"search:{query}:{filters_str}:{sort_by}:{page}:{size}"
        cached_result = await cache.get(cache_key)
        if cached_result:
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
        if filters.get("department"):
            where_conditions.append(Article.department == filters["department"])
        if filters.get("position"):
            where_conditions.append(Article.position == filters["position"])
        if filters.get("level"):
            where_conditions.append(Article.level == filters["level"])
        if filters.get("only_published", True):
            where_conditions.append(Article.status == ArticleStatus.PUBLISHED)

        if user_filters:
            user_filter_conditions = []
            if user_filters.get("department"):
                user_filter_conditions.append(Article.department == user_filters["department"])
            if user_filters.get("position"):
                user_filter_conditions.append(Article.position == user_filters["position"])
            if user_filters.get("level"):
                user_filter_conditions.append(Article.level == user_filters["level"])
            if user_filter_conditions:
                where_conditions.append(or_(*user_filter_conditions))

        count_stmt = select(func.count(Article.id))
        if where_conditions:
            count_stmt = count_stmt.where(and_(*where_conditions))
        result = await self.db.execute(count_stmt)
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

        result = await self.db.execute(id_stmt)
        rows = result.all()

        if not rows:
            empty_result = [], 0, []
            if user_id:
                await self._record_search_history(
                    user_id=user_id,
                    query=query,
                    results_count=0,
                    filters=filters,
                    department=user_filters.get("department") if user_filters else None,
                )
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

        result = await self.db.execute(stmt)
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
            await self._record_search_history(
                user_id=user_id,
                query=query,
                results_count=total,
                filters=filters,
                department=user_filters.get("department") if user_filters else None,
            )

        await cache.set(
            cache_key,
            {
                "results": formatted_results,
                "total": total,
                "suggestions": suggestions,
            },
            ttl=settings.SEARCH_CACHE_TTL,
        )

        return formatted_results, total, suggestions

    async def get_search_suggestions(
        self,
        query: str,
        department: str | None = None,
        limit: int = 10,
    ) -> list[str]:
        """Get search suggestions based on query."""
        if not query or len(query) < 2:
            return []

        # Try to get from cache
        cache_key = f"suggestions:{query}:{department}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        # Get suggestions from recent searches
        conditions = [
            SearchHistory.query.ilike(f"%{query}%"),
            SearchHistory.created_at >= datetime.now(UTC) - timedelta(days=30),
        ]
        if department is not None:
            conditions.append(SearchHistory.department == department)

        stmt = (
            select(SearchHistory.query, func.count(SearchHistory.id).label("count"))
            .where(and_(*conditions))
            .group_by(SearchHistory.query)
            .order_by(func.count(SearchHistory.id).desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        suggestions = [row[0] for row in result.all()]

        # If not enough suggestions, get from article titles
        if len(suggestions) < limit:
            title_conditions = [
                Article.title.ilike(f"%{query}%"),
                Article.status == ArticleStatus.PUBLISHED,
            ]
            if department is not None:
                title_conditions.append(Article.department == department)

            stmt = select(Article.title).where(and_(*title_conditions)).limit(limit - len(suggestions))
            result = await self.db.execute(stmt)
            title_suggestions = [row[0] for row in result.all()]
            suggestions.extend(title_suggestions)

        # Remove duplicates and limit
        suggestions = list(dict.fromkeys(suggestions))[:limit]

        # Cache suggestions
        await cache.set(cache_key, suggestions, ttl=300)

        return suggestions

    async def get_popular_searches(
        self,
        department: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Get popular searches."""
        cache_key = f"popular_searches:{department}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        conditions = [
            SearchHistory.created_at >= datetime.now(UTC) - timedelta(days=7),
        ]
        if department is not None:
            conditions.append(SearchHistory.department == department)

        stmt = (
            select(
                SearchHistory.query,
                func.count(SearchHistory.id).label("search_count"),
                func.avg(SearchHistory.results_count).label("avg_results"),
            )
            .where(and_(*conditions))
            .group_by(SearchHistory.query)
            .order_by(func.count(SearchHistory.id).desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        popular = [
            {
                "query": row[0],
                "search_count": row[1],
                "avg_results": float(row[2]) if row[2] else 0,
            }
            for row in result.all()
        ]

        await cache.set(cache_key, popular, ttl=3600)

        return popular

    async def get_user_search_history(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[SearchHistory], int]:
        """Get user's search history."""
        stmt = select(SearchHistory).where(SearchHistory.user_id == user_id)
        count_stmt = select(func.count(SearchHistory.id)).where(SearchHistory.user_id == user_id)

        result = await self.db.execute(count_stmt)
        total = result.scalar_one()

        stmt = stmt.order_by(SearchHistory.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        history = list(result.scalars().all())

        return history, total

    async def clear_user_search_history(self, user_id: int) -> None:
        """Clear user's search history."""
        stmt = select(SearchHistory).where(SearchHistory.user_id == user_id)
        result = await self.db.execute(stmt)
        history_items = list(result.scalars().all())

        for item in history_items:
            await self.db.delete(item)

        await self.db.commit()

    async def get_search_stats(self) -> dict[str, Any]:
        """Get search statistics."""
        # Total searches
        total_stmt = select(func.count(SearchHistory.id))
        total_result = await self.db.execute(total_stmt)
        total_searches = total_result.scalar_one() or 0

        # Popular queries
        popular_stmt = (
            select(
                SearchHistory.query,
                func.count(SearchHistory.id).label("count"),
            )
            .group_by(SearchHistory.query)
            .order_by(func.count(SearchHistory.id).desc())
            .limit(10)
        )
        popular_result = await self.db.execute(popular_stmt)
        popular_queries = [{"query": row[0], "count": row[1]} for row in popular_result.all()]

        # No results queries
        no_results_stmt = (
            select(
                SearchHistory.query,
                func.count(SearchHistory.id).label("count"),
            )
            .where(SearchHistory.results_count == 0)
            .group_by(SearchHistory.query)
            .order_by(func.count(SearchHistory.id).desc())
            .limit(10)
        )
        no_results_result = await self.db.execute(no_results_stmt)
        no_results_queries = [{"query": row[0], "count": row[1]} for row in no_results_result.all()]

        # Searches by department
        dept_stmt = (
            select(
                SearchHistory.department,
                func.count(SearchHistory.id).label("count"),
            )
            .where(SearchHistory.department.is_not(None))
            .group_by(SearchHistory.department)
        )
        dept_result = await self.db.execute(dept_stmt)
        searches_by_department = {row[0]: row[1] for row in dept_result.all()}

        # Average results per search
        avg_stmt = select(func.avg(SearchHistory.results_count))
        avg_result = await self.db.execute(avg_stmt)
        avg_results_per_search = float(avg_result.scalar_one() or 0)

        # Searches last 30 days
        last_30_days_stmt = (
            select(
                func.date(SearchHistory.created_at).label("date"),
                func.count(SearchHistory.id).label("count"),
            )
            .where(SearchHistory.created_at >= datetime.now(UTC) - timedelta(days=30))
            .group_by(func.date(SearchHistory.created_at))
        )
        last_30_days_result = await self.db.execute(last_30_days_stmt)
        searches_last_30_days = [{"date": row[0].isoformat(), "count": row[1]} for row in last_30_days_result.all()]

        return {
            "total_searches": total_searches,
            "popular_queries": popular_queries,
            "no_results_queries": no_results_queries,
            "searches_by_department": searches_by_department,
            "avg_results_per_search": round(avg_results_per_search, 2),
            "searches_last_30_days": searches_last_30_days,
        }

    def _highlight_text(self, text: str, query: str) -> str:
        """Highlight search terms in text."""
        if not text or not query:
            return text

        # Simple highlighting - wrap search terms in <mark> tags
        words = re.split(r"\s+", query)
        highlighted = text

        for word in words:
            if len(word) > 2:  # Only highlight words longer than 2 characters
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                highlighted = pattern.sub(f"<mark>{word}</mark>", highlighted)

        return highlighted

    async def _record_search_history(
        self,
        user_id: int,
        query: str,
        results_count: int,
        filters: dict,
        department: str | None = None,
    ) -> None:
        """Record search history."""
        search_history = SearchHistory(
            user_id=user_id,
            query=query,
            filters=filters,
            results_count=results_count,
            department=department,
        )

        self.db.add(search_history)
        await self.db.commit()
