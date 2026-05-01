"""Search analytics endpoints for HR."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from knowledge_service.api.deps import CurrentUser, SearchHistoryRepositoryDep
from knowledge_service.schemas import (
    DepartmentSearchStats,
    SearchSummary,
    SearchTimeseriesPoint,
    TopQueryStats,
    ZeroResultQuery,
)
from knowledge_service.services.cleanup import cleanup_old_search_history

router = APIRouter()


@router.get("/top-queries")
async def get_top_queries(
    current_user: CurrentUser,
    search_history_repo: SearchHistoryRepositoryDep,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    department_id: Annotated[int | None, Query()] = None,
) -> list[TopQueryStats]:
    """Get top search queries with statistics (HR only)."""
    if not current_user.has_role(["HR", "ADMIN"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR access required",
        )

    results = await search_history_repo.get_top_queries(
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        department_id=department_id,
    )

    return [
        TopQueryStats(
            query=row["query"],
            count=row["count"],
            avg_results_count=row["avg_results_count"],
            zero_results_count=row["zero_results_count"],
        )
        for row in results
    ]


@router.get("/zero-results")
async def get_zero_results_queries(
    current_user: CurrentUser,
    search_history_repo: SearchHistoryRepositoryDep,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    department_id: Annotated[int | None, Query()] = None,
) -> list[ZeroResultQuery]:
    """Get queries that returned zero results (content gaps) (HR only)."""
    if not current_user.has_role(["HR", "ADMIN"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR access required",
        )

    results = await search_history_repo.get_zero_results_queries(
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        department_id=department_id,
    )

    return [
        ZeroResultQuery(
            query=row["query"],
            count=row["count"],
            last_searched_at=row["last_searched_at"],
        )
        for row in results
    ]


@router.get("/by-department")
async def get_search_by_department(
    current_user: CurrentUser,
    search_history_repo: SearchHistoryRepositoryDep,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
) -> list[DepartmentSearchStats]:
    """Get search statistics grouped by department (HR only)."""
    if not current_user.has_role(["HR", "ADMIN"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR access required",
        )

    results = await search_history_repo.get_by_department(
        from_date=from_date,
        to_date=to_date,
    )

    return [
        DepartmentSearchStats(
            department_id=row["department_id"],
            department_name=row["department_name"],
            search_count=row["search_count"],
            unique_users=row["unique_users"],
        )
        for row in results
    ]


@router.get("/timeseries")
async def get_search_timeseries(
    current_user: CurrentUser,
    search_history_repo: SearchHistoryRepositoryDep,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    granularity: Annotated[str, Query(pattern="day|week")] = "day",
) -> list[SearchTimeseriesPoint]:
    """Get search timeseries data with specified granularity (HR only)."""
    if not current_user.has_role(["HR", "ADMIN"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR access required",
        )

    results = await search_history_repo.get_search_timeseries(
        from_date=from_date,
        to_date=to_date,
        granularity=granularity,
    )

    return [
        SearchTimeseriesPoint(
            bucket=row["bucket"],
            search_count=row["search_count"],
            unique_users=row["unique_users"],
        )
        for row in results
    ]


@router.get("/summary")
async def get_search_summary(
    current_user: CurrentUser,
    search_history_repo: SearchHistoryRepositoryDep,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
) -> SearchSummary:
    """Get overall search summary statistics (HR only)."""
    if not current_user.has_role(["HR", "ADMIN"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR access required",
        )

    summary = await search_history_repo.get_search_summary(
        from_date=from_date,
        to_date=to_date,
    )

    return SearchSummary(**summary)


@router.post("/cleanup")
async def cleanup_search_history(
    current_user: CurrentUser,
) -> dict:
    """Trigger cleanup of old search history records (Admin only)."""
    if not current_user.has_role(["ADMIN"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    deleted_count = await cleanup_old_search_history()

    return {"message": f"Cleaned up {deleted_count} old search history records"}
