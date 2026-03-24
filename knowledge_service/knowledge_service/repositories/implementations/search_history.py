"""SQLAlchemy implementation of SearchHistory repository."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import SearchHistory
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.search_history import ISearchHistoryRepository


class SearchHistoryRepository(SqlAlchemyBaseRepository[SearchHistory, int], ISearchHistoryRepository):
    """SQLAlchemy implementation of SearchHistory repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize search history repository."""
        super().__init__(session, SearchHistory)

    async def record_search(
        self,
        user_id: int,
        query: str,
        results_count: int,
        filters: dict,
        department_id: int | None = None,
    ) -> SearchHistory:
        """Record a search query."""
        search_history = SearchHistory(
            user_id=user_id,
            query=query,
            filters=filters,
            results_count=results_count,
            department_id=department_id,
        )
        return await self.create(search_history)

    async def find_by_user(
        self, user_id: int, *, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[SearchHistory], int]:
        """Find search history entries for a user."""
        stmt = select(SearchHistory).where(SearchHistory.user_id == user_id)
        count_stmt = select(func.count(SearchHistory.id)).where(SearchHistory.user_id == user_id)

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        stmt = stmt.order_by(SearchHistory.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    async def clear_user_history(self, user_id: int) -> int:
        """Clear all search history for a user."""
        stmt = select(SearchHistory).where(SearchHistory.user_id == user_id)
        result = await self._session.execute(stmt)
        history_items = list(result.scalars().all())
        count = len(history_items)
        for item in history_items:
            await self._session.delete(item)
        await self._session.flush()
        return count

    async def get_suggestions(self, query: str, department_id: int | None = None, limit: int = 10) -> Sequence[str]:
        """Get search suggestions based on query prefix."""
        conditions = [
            SearchHistory.query.ilike(f"%{query}%"),
            SearchHistory.created_at >= datetime.now(UTC) - timedelta(days=30),
        ]
        if department_id is not None:
            conditions.append(SearchHistory.department_id == department_id)

        stmt = (
            select(SearchHistory.query, func.count(SearchHistory.id).label("count"))
            .where(and_(*conditions))
            .group_by(SearchHistory.query)
            .order_by(func.count(SearchHistory.id).desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_popular_searches(self, department_id: int | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """Get popular search queries from the last 7 days."""
        conditions = [
            SearchHistory.created_at >= datetime.now(UTC) - timedelta(days=7),
        ]
        if department_id is not None:
            conditions.append(SearchHistory.department_id == department_id)

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
        result = await self._session.execute(stmt)
        return [
            {
                "query": row[0],
                "search_count": row[1],
                "avg_results": float(row[2]) if row[2] else 0,
            }
            for row in result.all()
        ]

    async def get_search_stats(self) -> dict[str, Any]:
        """Get aggregate search statistics."""
        total_stmt = select(func.count(SearchHistory.id))
        total_result = await self._session.execute(total_stmt)
        total_searches = total_result.scalar_one() or 0

        popular_stmt = (
            select(
                SearchHistory.query,
                func.count(SearchHistory.id).label("count"),
            )
            .group_by(SearchHistory.query)
            .order_by(func.count(SearchHistory.id).desc())
            .limit(10)
        )
        popular_result = await self._session.execute(popular_stmt)
        popular_queries = [{"query": row[0], "count": row[1]} for row in popular_result.all()]

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
        no_results_result = await self._session.execute(no_results_stmt)
        no_results_queries = [{"query": row[0], "count": row[1]} for row in no_results_result.all()]

        dept_stmt = (
            select(
                SearchHistory.department_id,
                func.count(SearchHistory.id).label("count"),
            )
            .where(SearchHistory.department_id.is_not(None))
            .group_by(SearchHistory.department_id)
        )
        dept_result = await self._session.execute(dept_stmt)
        searches_by_department = {row[0]: row[1] for row in dept_result.all()}

        avg_stmt = select(func.avg(SearchHistory.results_count))
        avg_result = await self._session.execute(avg_stmt)
        avg_results_per_search = float(avg_result.scalar_one() or 0)

        last_30_days_stmt = (
            select(
                func.date(SearchHistory.created_at).label("date"),
                func.count(SearchHistory.id).label("count"),
            )
            .where(SearchHistory.created_at >= datetime.now(UTC) - timedelta(days=30))
            .group_by(func.date(SearchHistory.created_at))
        )
        last_30_days_result = await self._session.execute(last_30_days_stmt)
        searches_last_30_days = [{"date": row[0].isoformat(), "count": row[1]} for row in last_30_days_result.all()]

        return {
            "total_searches": total_searches,
            "popular_queries": popular_queries,
            "no_results_queries": no_results_queries,
            "searches_by_department": searches_by_department,
            "avg_results_per_search": round(avg_results_per_search, 2),
            "searches_last_30_days": searches_last_30_days,
        }
