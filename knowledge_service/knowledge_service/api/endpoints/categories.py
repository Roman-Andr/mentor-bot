"""Category management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from knowledge_service.api import AdminUser, CategoryServiceDep, CurrentUser, HRUser
from knowledge_service.core import NotFoundException, ValidationException
from knowledge_service.core.enums import ArticleStatus
from knowledge_service.schemas import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
    CategoryWithArticles,
    MessageResponse,
)

router = APIRouter()


@router.get("/")
@router.get("")
async def get_categories(
    category_service: CategoryServiceDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    parent_id: Annotated[int | None, Query()] = None,
    department_id: Annotated[int | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    *,
    include_tree: Annotated[bool, Query()] = False,
    sort_by: Annotated[str | None, Query()] = None,
    sort_order: Annotated[str, Query()] = "asc",
) -> CategoryListResponse:
    """Get paginated list of categories."""
    user_department_id = current_user.department_id
    if current_user.role not in ["HR", "ADMIN"]:
        department_id = user_department_id

    if include_tree:
        tree, total = await category_service.get_category_tree(department_id)

        flattened_categories = [
            CategoryResponse(
                id=category_dict["id"],
                name=category_dict["name"],
                slug=category_dict["slug"],
                description=category_dict["description"],
                parent_id=category_dict["parent_id"],
                parent_name=category_dict["parent_name"],
                order=category_dict["order"],
                department_id=category_dict["department_id"],
                position=category_dict.get("position"),
                level=category_dict.get("level"),
                icon=category_dict.get("icon"),
                color=category_dict.get("color"),
                created_at=category_dict["created_at"],
                updated_at=category_dict["updated_at"],
                children_count=len(category_dict["children"]),
                articles_count=category_dict["articles_count"],
            )
            for category_dict in tree
        ]

        pages = (total + limit - 1) // limit if limit > 0 else 0

        return CategoryListResponse(
            total=total,
            categories=flattened_categories,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            pages=pages,
        )

    categories, total = await category_service.get_categories(
        skip=skip,
        limit=limit,
        parent_id=parent_id,
        department_id=department_id,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return CategoryListResponse(
        total=total,
        categories=[CategoryResponse.model_validate(category) for category in categories],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.post("/")
@router.post("")
async def create_category(
    category_data: CategoryCreate,
    category_service: CategoryServiceDep,
    _current_user: HRUser,
) -> CategoryResponse:
    """Create new category (HR/admin only)."""
    try:
        category = await category_service.create_category(category_data)
        return CategoryResponse.model_validate(category)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.get("/{category_id_or_slug}")
async def get_category(
    category_id_or_slug: str,
    category_service: CategoryServiceDep,
    current_user: CurrentUser,
    *,
    include_articles: Annotated[bool, Query()] = False,
) -> CategoryResponse | CategoryWithArticles:
    """Get category by ID or slug."""
    try:
        try:
            category_id = int(category_id_or_slug)
            category = await category_service.get_category_by_id(category_id)
        except ValueError:
            category = await category_service.get_category_by_slug(category_id_or_slug)

        if (
            category.department_id
            and current_user.department_id != category.department_id
            and current_user.role not in ["HR", "ADMIN"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other departments' categories",
            )

        if include_articles:
            filtered_articles = [
                article
                for article in category.articles
                if current_user.role in ["HR", "ADMIN"]
                or (article.status == ArticleStatus.PUBLISHED and article.department_id == current_user.department_id)
            ]

            return CategoryWithArticles(
                **CategoryResponse.model_validate(category).model_dump(),
                articles=[
                    {
                        "id": article.id,
                        "title": article.title,
                        "slug": article.slug,
                        "status": article.status,
                        "created_at": article.created_at,
                    }
                    for article in filtered_articles
                ],
            )

        return CategoryResponse.model_validate(category)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    category_service: CategoryServiceDep,
    _current_user: HRUser,
) -> CategoryResponse:
    """Update category (HR/admin only)."""
    try:
        category = await category_service.update_category(category_id, category_data)
        return CategoryResponse.model_validate(category)
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


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    category_service: CategoryServiceDep,
    _current_user: AdminUser,
) -> MessageResponse:
    """Delete category (admin only)."""
    try:
        await category_service.delete_category(category_id)
        return MessageResponse(message="Category deleted successfully")
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


@router.get("/department/{department_id}")
async def get_department_categories(
    department_id: int,
    category_service: CategoryServiceDep,
    current_user: CurrentUser,
) -> list[CategoryResponse]:
    """Get all categories for specific department."""
    if current_user.department_id != department_id and current_user.role not in ["HR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other departments' categories",
        )

    categories = await category_service.get_department_categories(department_id)
    return [CategoryResponse.model_validate(category) for category in categories]


@router.get("/tree/{department_id}")
async def get_category_tree(
    department_id: int,
    category_service: CategoryServiceDep,
    current_user: CurrentUser,
) -> list[dict]:
    """Get category tree for specific department."""
    if current_user.department_id != department_id and current_user.role not in ["HR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other departments' categories",
        )

    tree, _ = await category_service.get_category_tree(department_id)
    return tree
