"""Search endpoints for knowledge base."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from knowledge_service.api import CurrentUser, SearchServiceDep
from knowledge_service.schemas import (
    SearchQuery,
    SearchResponse,
    SearchStats,
)

router = APIRouter()


@router.post("/")
@router.post("")
async def search_articles(
    search_query: SearchQuery,
    search_service: SearchServiceDep,
    current_user: CurrentUser,
) -> SearchResponse:
    """Search articles in knowledge base."""
    user_filters = {
        "department_id": current_user.department_id,
        "position": current_user.position,
        "level": current_user.level,
    }

    # Authorization check: only HR/ADMIN can search other departments
    if search_query.department_id is not None and not current_user.has_role(["HR", "ADMIN"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to search other departments",
        )

    results, total, suggestions = await search_service.search_articles(
        query=search_query.query,
        filters={
            "category_id": search_query.category_id,
            "tag_ids": search_query.tag_ids,
            "department_id": (
                search_query.department_id
                if current_user.has_role(["HR", "ADMIN"])
                else current_user.department_id
            ),
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
    search_service: SearchServiceDep,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> list[str]:
    """Get search suggestions."""
    return await search_service.get_search_suggestions(
        query=query,
        department_id=current_user.department_id,
        limit=limit,
    )


@router.get("/popular")
async def popular_searches(
    search_service: SearchServiceDep,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[dict]:
    """Get popular searches."""
    return await search_service.get_popular_searches(
        department_id=current_user.department_id,
        limit=limit,
    )


@router.get("/history")
async def search_history(
    search_service: SearchServiceDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[dict]:
    """Get user's search history."""
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
    search_service: SearchServiceDep,
    current_user: CurrentUser,
) -> dict:
    """Clear user's search history."""
    await search_service.clear_user_search_history(current_user.id)
    return {"message": "Search history cleared"}


@router.get("/stats")
async def get_search_stats(
    search_service: SearchServiceDep,
    current_user: CurrentUser,
) -> SearchStats:
    """Get search statistics (admin only)."""
    if current_user.role not in ["HR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    stats = await search_service.get_search_stats()
    return SearchStats(**stats)
