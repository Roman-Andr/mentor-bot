"""Article management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from knowledge_service.api import CurrentUser, DatabaseSession, HRUser
from knowledge_service.core import NotFoundException, PermissionDenied
from knowledge_service.core.enums import ArticleStatus
from knowledge_service.schemas import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
    ArticleViewStats,
    MessageResponse,
)
from knowledge_service.services import ArticleService

router = APIRouter()


@router.get("/")
async def get_articles(  # noqa: PLR0913
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    category_id: Annotated[int | None, Query()] = None,
    tag_id: Annotated[int | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    *,
    featured_only: Annotated[bool, Query()] = False,
    pinned_only: Annotated[bool, Query()] = False,
) -> ArticleListResponse:
    """Get paginated list of articles."""
    article_service = ArticleService(db)

    # Apply user filters for non-admins
    user_filters = {}
    if current_user.role not in ["HR", "ADMIN"]:
        user_filters = {
            "department": current_user.department,
            "position": current_user.position,
            "level": current_user.level,
        }

    articles, total = await article_service.get_articles(
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

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return ArticleListResponse(
        total=total,
        articles=[ArticleResponse.model_validate(article) for article in articles],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.post("/")
async def create_article(
    article_data: ArticleCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ArticleResponse:
    """Create new article."""
    article_service = ArticleService(db)

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
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ArticleResponse:
    """Get article by ID or slug."""
    article_service = ArticleService(db)

    try:
        # Try to parse as ID first
        try:
            article_id = int(article_id_or_slug)
            article = await article_service.get_article_by_id(article_id)
        except ValueError:
            # If not a number, treat as slug
            article = await article_service.get_article_by_slug(article_id_or_slug)

        # Check permissions for draft articles
        if (
            article.status == ArticleStatus.DRAFT
            and current_user.id != article.author_id
            and current_user.role not in ["HR", "ADMIN"]
        ):
            msg = "Cannot view draft articles"
            raise PermissionDenied(msg)

        # Record view
        await article_service.record_view(article.id)

        return ArticleResponse.model_validate(article)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.put("/{article_id}")
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ArticleResponse:
    """Update article."""
    article_service = ArticleService(db)

    try:
        article = await article_service.get_article_by_id(article_id)

        # Check permissions
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
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MessageResponse:
    """Delete article."""
    article_service = ArticleService(db)

    try:
        article = await article_service.get_article_by_id(article_id)

        # Check permissions
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
    db: DatabaseSession,
    _current_user: HRUser,
) -> ArticleResponse:
    """Publish article (HR/admin only)."""
    article_service = ArticleService(db)

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
    db: DatabaseSession,
    _current_user: HRUser,
) -> ArticleViewStats:
    """Get article view statistics (HR/admin only)."""
    article_service = ArticleService(db)

    try:
        stats = await article_service.get_article_stats(article_id)
        return ArticleViewStats(**stats)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/department/{department}")
async def get_department_articles(
    department: str,
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ArticleListResponse:
    """Get articles for specific department."""
    article_service = ArticleService(db)

    # Check if user has access to this department
    if current_user.department != department and current_user.role not in ["HR", "ADMIN"]:
        msg = "Cannot view other departments' articles"
        raise PermissionDenied(msg)

    articles, total = await article_service.get_department_articles(department, skip, limit)

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return ArticleListResponse(
        total=total,
        articles=[ArticleResponse.model_validate(article) for article in articles],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )
