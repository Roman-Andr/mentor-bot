"""Search endpoints for knowledge base."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from knowledge_service.api import CurrentUser, DatabaseSession
from knowledge_service.schemas import (
    SearchQuery,
    SearchResponse,
    SearchStats,
)
from knowledge_service.services import SearchService

router = APIRouter()


@router.post("/")
async def search_articles(
    search_query: SearchQuery,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> SearchResponse:
    """Search articles in knowledge base."""
    search_service = SearchService(db)

    # Apply user filters
    user_filters = {
        "department": current_user.department,
        "position": current_user.position,
        "level": current_user.level,
    }

    results, total, suggestions = await search_service.search_articles(
        query=search_query.query,
        filters={
            "category_id": search_query.category_id,
            "tag_ids": search_query.tag_ids,
            "department": search_query.department or current_user.department,
            "position": search_query.position,
            "level": search_query.level,
            "only_published": search_query.only_published,
        },
        sort_by=search_query.sort_by,
        page=search_query.page,
        size=search_query.size,
        user_filters=user_filters,
        user_id=current_user.id,
    )

    pages = (total + search_query.size - 1) // search_query.size if search_query.size > 0 else 0

    return SearchResponse(
        total=total,
        results=results,
        query=search_query.query,
        filters=search_query.model_dump(exclude={"query", "page", "size"}),
        suggestions=suggestions,
        page=search_query.page,
        size=search_query.size,
        pages=pages,
    )


@router.get("/suggest")
async def search_suggestions(
    query: Annotated[str, Query(min_length=1, max_length=100)],
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> list[str]:
    """Get search suggestions."""
    search_service = SearchService(db)

    return await search_service.get_search_suggestions(
        query=query,
        department=current_user.department,
        limit=limit,
    )


@router.get("/popular")
async def popular_searches(
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[dict]:
    """Get popular searches."""
    search_service = SearchService(db)

    return await search_service.get_popular_searches(
        department=current_user.department,
        limit=limit,
    )


@router.get("/history")
async def search_history(
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[dict]:
    """Get user's search history."""
    search_service = SearchService(db)

    history, _total = await search_service.get_user_search_history(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return [
        {
            "id": item.id,
            "query": item.query,
            "results_count": item.results_count,
            "created_at": item.created_at.isoformat(),
            "filters": item.filters,
        }
        for item in history
    ]


@router.delete("/history")
async def clear_search_history(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict:
    """Clear user's search history."""
    search_service = SearchService(db)

    await search_service.clear_user_search_history(current_user.id)

    return {"message": "Search history cleared"}


@router.get("/stats")
async def get_search_stats(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> SearchStats:
    """Get search statistics (admin only)."""
    search_service = SearchService(db)

    if current_user.role not in ["HR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    stats = await search_service.get_search_stats()

    return SearchStats(**stats)
