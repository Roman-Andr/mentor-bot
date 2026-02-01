"""Category management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from knowledge_service.api import AdminUser, CurrentUser, DatabaseSession, HRUser
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
from knowledge_service.services import CategoryService

router = APIRouter()


@router.get("/")
async def get_categories(  # noqa: PLR0913
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    parent_id: Annotated[int | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    *,
    include_tree: Annotated[bool, Query()] = False,
) -> CategoryListResponse:
    """Get paginated list of categories."""
    category_service = CategoryService(db)

    # Apply user filters for non-admins
    user_department = current_user.department
    if current_user.role not in ["HR", "ADMIN"]:
        department = user_department

    if include_tree:
        # Get tree structure
        tree, total = await category_service.get_category_tree(department)

        # Convert tree to flat list for response
        flattened_categories = [
            CategoryResponse(
                id=category_dict["id"],
                name=category_dict["name"],
                slug=category_dict["slug"],
                description=category_dict["description"],
                parent_id=category_dict["parent_id"],
                parent_name=category_dict["parent_name"],
                order=category_dict["order"],
                department=category_dict["department"],
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
        department=department,
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
async def create_category(
    category_data: CategoryCreate,
    db: DatabaseSession,
    _current_user: HRUser,
) -> CategoryResponse:
    """Create new category (HR/admin only)."""
    category_service = CategoryService(db)

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
    db: DatabaseSession,
    current_user: CurrentUser,
    *,
    include_articles: Annotated[bool, Query()] = False,
) -> CategoryResponse | CategoryWithArticles:
    """Get category by ID or slug."""
    category_service = CategoryService(db)

    try:
        # Try to parse as ID first
        try:
            category_id = int(category_id_or_slug)
            category = await category_service.get_category_by_id(category_id)
        except ValueError:
            # If not a number, treat as slug
            category = await category_service.get_category_by_slug(category_id_or_slug)

        # Check if user has access to this department's categories
        if (
            category.department
            and current_user.department != category.department
            and current_user.role not in ["HR", "ADMIN"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other departments' categories",
            )

        if include_articles:
            # Filter articles based on user role and department
            filtered_articles = [
                article
                for article in category.articles
                if current_user.role in ["HR", "ADMIN"]
                or (article.status == ArticleStatus.PUBLISHED and article.department == current_user.department)
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
    db: DatabaseSession,
    _current_user: HRUser,
) -> CategoryResponse:
    """Update category (HR/admin only)."""
    category_service = CategoryService(db)

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
    db: DatabaseSession,
    _current_user: AdminUser,
) -> MessageResponse:
    """Delete category (admin only)."""
    category_service = CategoryService(db)

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


@router.get("/department/{department}")
async def get_department_categories(
    department: str,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> list[CategoryResponse]:
    """Get all categories for specific department."""
    # Check permissions
    if current_user.department != department and current_user.role not in ["HR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other departments' categories",
        )

    category_service = CategoryService(db)
    categories = await category_service.get_department_categories(department)

    return [CategoryResponse.model_validate(category) for category in categories]


@router.get("/tree/{department}")
async def get_category_tree(
    department: str,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> list[dict]:
    """Get category tree for specific department."""
    # Check permissions
    if current_user.department != department and current_user.role not in ["HR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other departments' categories",
        )

    category_service = CategoryService(db)
    return await category_service.get_category_tree(department)
