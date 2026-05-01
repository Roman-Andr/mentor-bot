"""SQLAlchemy implementation of SearchHistory repository."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from sqlalchemy import and_, case, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

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

    async def get_top_queries(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 20,
        department_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get top search queries with statistics."""
        conditions = []
        if from_date:
            conditions.append(SearchHistory.created_at >= from_date)
        if to_date:
            conditions.append(SearchHistory.created_at <= to_date)
        if department_id is not None:
            conditions.append(SearchHistory.department_id == department_id)

        stmt = (
            select(
                SearchHistory.query,
                func.count(SearchHistory.id).label("count"),
                func.avg(SearchHistory.results_count).label("avg_results_count"),
                func.sum(case((SearchHistory.results_count == 0, 1), else_=0)).label("zero_results_count"),
            )
            .where(and_(*conditions) if conditions else True)
            .group_by(SearchHistory.query)
            .order_by(func.count(SearchHistory.id).desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [
            {
                "query": row[0],
                "count": row[1],
                "avg_results_count": float(row[2]) if row[2] else 0,
                "zero_results_count": row[3] or 0,
            }
            for row in result.all()
        ]

    async def get_zero_results_queries(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 20,
        department_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get queries that returned zero results."""
        conditions = [SearchHistory.results_count == 0]
        if from_date:
            conditions.append(SearchHistory.created_at >= from_date)
        if to_date:
            conditions.append(SearchHistory.created_at <= to_date)
        if department_id is not None:
            conditions.append(SearchHistory.department_id == department_id)

        stmt = (
            select(
                SearchHistory.query,
                func.count(SearchHistory.id).label("count"),
                func.max(SearchHistory.created_at).label("last_searched_at"),
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
                "count": row[1],
                "last_searched_at": row[2],
            }
            for row in result.all()
        ]

    async def get_by_department(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Get search statistics grouped by department."""
        conditions = []
        if from_date:
            conditions.append(SearchHistory.created_at >= from_date)
        if to_date:
            conditions.append(SearchHistory.created_at <= to_date)

        stmt = (
            select(
                SearchHistory.department_id,
                func.count(SearchHistory.id).label("search_count"),
                func.count(func.distinct(SearchHistory.user_id)).label("unique_users"),
            )
            .where(and_(*conditions) if conditions else True)
            .group_by(SearchHistory.department_id)
            .order_by(func.count(SearchHistory.id).desc())
        )
        result = await self._session.execute(stmt)
        return [
            {
                "department_id": row[0],
                "department_name": f"Department {row[0]}" if row[0] else "Unknown",
                "search_count": row[1],
                "unique_users": row[2],
            }
            for row in result.all()
        ]

    async def get_search_timeseries(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        granularity: str = "day",
    ) -> list[dict[str, Any]]:
        """Get search timeseries data with specified granularity."""
        conditions = []
        if from_date:
            conditions.append(SearchHistory.created_at >= from_date)
        if to_date:
            conditions.append(SearchHistory.created_at <= to_date)

        # Map granularity to PostgreSQL date_trunc values
        trunc_func = {
            "day": func.date_trunc("day", SearchHistory.created_at),
            "week": func.date_trunc("week", SearchHistory.created_at),
        }.get(granularity, func.date_trunc("day", SearchHistory.created_at))

        stmt = (
            select(
                trunc_func.label("bucket"),
                func.count(SearchHistory.id).label("search_count"),
                func.count(func.distinct(SearchHistory.user_id)).label("unique_users"),
            )
            .where(and_(*conditions) if conditions else True)
            .group_by(trunc_func)
            .order_by(trunc_func)
        )
        result = await self._session.execute(stmt)
        return [
            {
                "bucket": row[0].isoformat() if row[0] else None,
                "search_count": row[1],
                "unique_users": row[2],
            }
            for row in result.all()
        ]

    async def get_search_summary(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Get overall search summary statistics."""
        conditions = []
        if from_date:
            conditions.append(SearchHistory.created_at >= from_date)
        if to_date:
            conditions.append(SearchHistory.created_at <= to_date)

        where_clause = and_(*conditions) if conditions else True

        # Total searches
        total_stmt = select(func.count(SearchHistory.id)).where(where_clause)
        total_result = await self._session.execute(total_stmt)
        total_searches = total_result.scalar_one() or 0

        # Unique users
        users_stmt = select(func.count(func.distinct(SearchHistory.user_id))).where(where_clause)
        users_result = await self._session.execute(users_stmt)
        unique_users = users_result.scalar_one() or 0

        # Unique queries
        queries_stmt = select(func.count(func.distinct(SearchHistory.query))).where(where_clause)
        queries_result = await self._session.execute(queries_stmt)
        unique_queries = queries_result.scalar_one() or 0

        # Average results per search
        avg_stmt = select(func.avg(SearchHistory.results_count)).where(where_clause)
        avg_result = await self._session.execute(avg_stmt)
        avg_results_per_search = float(avg_result.scalar_one() or 0)

        # Zero results percentage
        zero_total_stmt = select(func.count(SearchHistory.id)).where(
            and_(where_clause, SearchHistory.results_count == 0) if conditions else SearchHistory.results_count == 0
        )
        zero_total_result = await self._session.execute(zero_total_stmt)
        zero_results_count = zero_total_result.scalar_one() or 0
        zero_results_percentage = (zero_results_count / total_searches * 100) if total_searches > 0 else 0

        return {
            "total_searches": total_searches,
            "unique_users": unique_users,
            "unique_queries": unique_queries,
            "avg_results_per_search": round(avg_results_per_search, 2),
            "zero_results_percentage": round(zero_results_percentage, 2),
        }

    async def delete_old_search_history(self, retention_days: int) -> int:
        """Delete search history entries older than retention period."""
        cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)
        stmt = delete(SearchHistory).where(SearchHistory.created_at < cutoff_date)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount or 0
