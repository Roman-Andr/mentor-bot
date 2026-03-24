"""Tag management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from knowledge_service.api import AdminUser, CurrentUser, HRUser, TagServiceDep
from knowledge_service.core import NotFoundException, ValidationException
from knowledge_service.schemas import (
    MessageResponse,
    TagCreate,
    TagResponse,
    TagUpdate,
)

router = APIRouter()


@router.get("/")
@router.get("")
async def get_tags(
    tag_service: TagServiceDep,
    _current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    search: Annotated[str | None, Query()] = None,
    sort_by: Annotated[str, Query()] = "usage_count",
    *,
    sort_desc: Annotated[bool, Query()] = True,
) -> list[TagResponse]:
    """Get paginated list of tags."""
    tags, _ = await tag_service.get_tags(
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    return [TagResponse.model_validate(tag) for tag in tags]


@router.get("/popular")
async def get_popular_tags(
    tag_service: TagServiceDep,
    _current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> list[TagResponse]:
    """Get most popular tags."""
    tags = await tag_service.get_popular_tags(limit)
    return [TagResponse.model_validate(tag) for tag in tags]


@router.post("/")
@router.post("")
async def create_tag(
    tag_data: TagCreate,
    tag_service: TagServiceDep,
    _current_user: HRUser,
) -> TagResponse:
    """Create new tag (HR/admin only)."""
    try:
        tag = await tag_service.create_tag(tag_data)
        return TagResponse.model_validate(tag)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.get("/{tag_id_or_slug}")
async def get_tag(
    tag_id_or_slug: str,
    tag_service: TagServiceDep,
    _current_user: CurrentUser,
) -> TagResponse:
    """Get tag by ID or slug."""
    try:
        try:
            tag_id = int(tag_id_or_slug)
            tag = await tag_service.get_tag_by_id(tag_id)
        except ValueError:
            tag = await tag_service.get_tag_by_slug(tag_id_or_slug)

        return TagResponse.model_validate(tag)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.put("/{tag_id}")
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    tag_service: TagServiceDep,
    _current_user: HRUser,
) -> TagResponse:
    """Update tag (HR/admin only)."""
    try:
        tag = await tag_service.update_tag(tag_id, tag_data)
        return TagResponse.model_validate(tag)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    tag_service: TagServiceDep,
    _current_user: AdminUser,
) -> MessageResponse:
    """Delete tag (admin only)."""
    try:
        await tag_service.delete_tag(tag_id)
        return MessageResponse(message="Tag deleted successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.post("/{source_tag_id}/merge/{target_tag_id}")
async def merge_tags(
    source_tag_id: int,
    target_tag_id: int,
    tag_service: TagServiceDep,
    _current_user: AdminUser,
) -> TagResponse:
    """Merge two tags (admin only)."""
    try:
        merged_tag = await tag_service.merge_tags(source_tag_id, target_tag_id)
        return TagResponse.model_validate(merged_tag)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.get("/article/{article_id}")
async def get_article_tags(
    article_id: int,
    tag_service: TagServiceDep,
    _current_user: CurrentUser,
) -> list[TagResponse]:
    """Get tags for a specific article."""
    try:
        tags = await tag_service.get_tags_by_article(article_id)
        return [TagResponse.model_validate(tag) for tag in tags]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
