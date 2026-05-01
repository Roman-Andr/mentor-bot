"""Knowledge analytics endpoints."""

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Query

from knowledge_service.api import HRUser, UOWDep
from knowledge_service.schemas import (
    CategoryStats,
    KnowledgeSummary,
    TagStats,
    TimeseriesPoint,
    TopArticleStats,
)

router = APIRouter()


@router.get("/top-articles")
async def get_top_articles(
    uow: UOWDep,
    _current_user: HRUser,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    department_id: Annotated[int | None, Query()] = None,
) -> list[TopArticleStats]:
    """Get top articles by view count (HR/admin only)."""
    results = await uow.article_views.get_top_articles(
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        department_id=department_id,
    )
    return [TopArticleStats(**r) for r in results]


@router.get("/views-timeseries")
async def get_views_timeseries(
    uow: UOWDep,
    _current_user: HRUser,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    granularity: Annotated[Literal["day", "week"], Query()] = "day",
    article_id: Annotated[int | None, Query()] = None,
) -> list[TimeseriesPoint]:
    """Get views timeseries data (HR/admin only)."""
    results = await uow.article_views.get_timeseries(
        from_date=from_date,
        to_date=to_date,
        granularity=granularity,
        article_id=article_id,
    )
    return [TimeseriesPoint(**r) for r in results]


@router.get("/views-by-category")
async def get_views_by_category(
    uow: UOWDep,
    _current_user: HRUser,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
) -> list[CategoryStats]:
    """Get view statistics by category (HR/admin only)."""
    results = await uow.article_views.get_by_category(
        from_date=from_date,
        to_date=to_date,
    )
    return [CategoryStats(**r) for r in results]


@router.get("/views-by-tag")
async def get_views_by_tag(
    uow: UOWDep,
    _current_user: HRUser,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
) -> list[TagStats]:
    """Get view statistics by tag (HR/admin only)."""
    results = await uow.article_views.get_by_tag(
        from_date=from_date,
        to_date=to_date,
    )
    return [TagStats(**r) for r in results]


@router.get("/summary")
async def get_knowledge_summary(
    uow: UOWDep,
    _current_user: HRUser,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
) -> KnowledgeSummary:
    """Get summary statistics for knowledge base (HR/admin only)."""
    results = await uow.article_views.get_summary_stats(
        from_date=from_date,
        to_date=to_date,
    )
    return KnowledgeSummary(**results)
