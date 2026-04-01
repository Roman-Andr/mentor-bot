"""Article management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from knowledge_service.api import ArticleServiceDep, CurrentUser, HRUser, SearchServiceDep
from knowledge_service.core import NotFoundException, PermissionDenied
from knowledge_service.core.enums import ArticleStatus, SearchSortBy
from knowledge_service.schemas import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
    ArticleViewStats,
    MessageResponse,
)

router = APIRouter()


@router.get("/")
@router.get("")
async def get_articles(
    article_service: ArticleServiceDep,
    search_service: SearchServiceDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    category_id: Annotated[int | None, Query()] = None,
    tag_id: Annotated[int | None, Query()] = None,
    department_id: Annotated[int | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    *,
    featured_only: Annotated[bool, Query()] = False,
    pinned_only: Annotated[bool, Query()] = False,
    sort_by: Annotated[str | None, Query()] = None,
) -> ArticleListResponse:
    """Get paginated list of articles."""
    user_filters = {}
    if current_user.role not in ["HR", "ADMIN"]:
        user_filters = {
            "department_id": current_user.department_id,
            "position": current_user.position,
            "level": current_user.level,
        }

    if search and search.strip():
        sort_by_enum = SearchSortBy(sort_by) if sort_by else SearchSortBy.RELEVANCE
        page = skip // limit + 1 if limit > 0 else 1

        results, total, _suggestions = await search_service.search_articles(
            query=search,
            filters={
                "category_id": category_id,
                "tag_ids": [tag_id] if tag_id else None,
                "department_id": department_id,
                "status": status,
                "featured_only": featured_only,
                "pinned_only": pinned_only,
                "only_published": current_user.role in ["HR", "ADMIN"],
            },
            sort_by=sort_by_enum,
            page=page,
            size=limit,
            user_filters=user_filters,
            user_id=current_user.id,
        )

        if results:
            article_ids = [r["id"] for r in results]
            articles = await article_service.get_articles_by_ids(article_ids)
            articles_map = {a.id: a for a in articles}
            ordered_articles = [articles_map[id] for id in article_ids if id in articles_map]
        else:
            ordered_articles = []

        pages = (total + limit - 1) // limit if limit > 0 else 0

        return ArticleListResponse(
            total=total,
            articles=[ArticleResponse.model_validate(article) for article in ordered_articles],
            page=page,
            size=limit,
            pages=pages,
        )

    articles, total = await article_service.get_articles(
        skip=skip,
        limit=limit,
        category_id=category_id,
        tag_id=tag_id,
        department_id=department_id,
        status=status,
        search=search,
        featured_only=featured_only,
        pinned_only=pinned_only,
        user_filters=user_filters,
    )

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return ArticleListResponse(
        total=total,
        articles=[ArticleResponse.model_validate(article) for article in articles],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.post("/")
@router.post("")
async def create_article(
    article_data: ArticleCreate,
    article_service: ArticleServiceDep,
    current_user: CurrentUser,
) -> ArticleResponse:
    """Create new article."""
    try:
        article = await article_service.create_article(article_data, current_user.id, current_user.first_name)
        return ArticleResponse.model_validate(article)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{article_id_or_slug}")
async def get_article(
    article_id_or_slug: str,
    article_service: ArticleServiceDep,
    current_user: CurrentUser,
) -> ArticleResponse:
    """Get article by ID or slug."""
    try:
        try:
            article_id = int(article_id_or_slug)
            article = await article_service.get_article_by_id(article_id)
        except ValueError:
            article = await article_service.get_article_by_slug(article_id_or_slug)

        if (
            article.status == ArticleStatus.DRAFT
            and current_user.id != article.author_id
            and current_user.role not in ["HR", "ADMIN"]
        ):
            msg = "Cannot view draft articles"
            raise PermissionDenied(msg)

        if (
            current_user.role not in ["HR", "ADMIN"]
            and article.department_id
            and article.department_id != current_user.department_id
        ):
            msg = "Access to articles from other departments is not allowed"
            raise PermissionDenied(msg)

        response = ArticleResponse.model_validate(article)
        await article_service.record_view(article.id, user_id=current_user.id)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    else:
        return response


@router.put("/{article_id}")
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    article_service: ArticleServiceDep,
    current_user: CurrentUser,
) -> ArticleResponse:
    """Update article."""
    try:
        article = await article_service.get_article_by_id(article_id)

        if current_user.id != article.author_id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot update other users' articles"
            raise PermissionDenied(msg)

        updated_article = await article_service.update_article(article_id, article_data)
        return ArticleResponse.model_validate(updated_article)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    article_service: ArticleServiceDep,
    current_user: CurrentUser,
) -> MessageResponse:
    """Delete article."""
    try:
        article = await article_service.get_article_by_id(article_id)

        if current_user.id != article.author_id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot delete other users' articles"
            raise PermissionDenied(msg)

        await article_service.delete_article(article_id)
        return MessageResponse(message="Article deleted successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{article_id}/publish")
async def publish_article(
    article_id: int,
    article_service: ArticleServiceDep,
    _current_user: HRUser,
) -> ArticleResponse:
    """Publish article (HR/admin only)."""
    try:
        article = await article_service.publish_article(article_id)
        return ArticleResponse.model_validate(article)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/{article_id}/stats")
async def get_article_stats(
    article_id: int,
    article_service: ArticleServiceDep,
    _current_user: HRUser,
) -> ArticleViewStats:
    """Get article view statistics (HR/admin only)."""
    try:
        stats = await article_service.get_article_stats(article_id)
        return ArticleViewStats(**stats)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/department/{department_id}")
async def get_department_articles(
    department_id: int,
    article_service: ArticleServiceDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ArticleListResponse:
    """Get articles for specific department."""
    if current_user.department_id != department_id and current_user.role not in ["HR", "ADMIN"]:
        msg = "Cannot view other departments' articles"
        raise PermissionDenied(msg)

    articles, total = await article_service.get_department_articles(department_id, skip, limit)

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return ArticleListResponse(
        total=total,
        articles=[ArticleResponse.model_validate(article) for article in articles],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )
