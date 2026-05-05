"""Tests for category API endpoints."""

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status
from knowledge_service.api.deps import UserInfo
from knowledge_service.api.endpoints.categories import (
    create_category,
    delete_category,
    get_categories,
    get_category,
    get_category_tree,
    get_department_categories,
    update_category,
)
from knowledge_service.core import ConflictException, NotFoundException, ValidationException
from knowledge_service.models import Category
from knowledge_service.schemas import CategoryCreate, CategoryResponse, CategoryUpdate

if TYPE_CHECKING:
    pass


class TestGetCategories:
    """Test GET /categories endpoint."""

    async def test_get_categories_success(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful retrieval of categories."""
        result = await get_categories(
            category_service=mock_category_service,
            current_user=mock_user,
        )

        assert result.total == 1
        assert len(result.categories) == 1
        mock_category_service.get_categories.assert_called_once()

    async def test_get_categories_with_tree(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting categories with tree structure."""
        result = await get_categories(
            category_service=mock_category_service,
            current_user=mock_user,
            include_tree=True,
        )

        assert result.total == 2
        mock_category_service.get_category_tree.assert_called_once()

    async def test_get_categories_non_admin_filters(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test that non-admin users get department filtering."""
        await get_categories(
            category_service=mock_category_service,
            current_user=mock_user,
        )

        call_kwargs = mock_category_service.get_categories.call_args[1]
        assert call_kwargs.get("department_id") == mock_user.department_id

    async def test_get_categories_admin_no_auto_filter(
        self,
        mock_category_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test that admin users can see all categories."""
        await get_categories(
            category_service=mock_category_service,
            current_user=mock_admin_user,
            department_id=5,
        )

        call_kwargs = mock_category_service.get_categories.call_args[1]
        assert call_kwargs.get("department_id") == 5

    async def test_get_categories_with_filters(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting categories with various filters."""
        await get_categories(
            category_service=mock_category_service,
            current_user=mock_user,
            skip=10,
            limit=20,
            parent_id=1,
            search="test",
        )

        call_kwargs = mock_category_service.get_categories.call_args[1]
        assert call_kwargs["skip"] == 10
        assert call_kwargs["limit"] == 20
        assert call_kwargs["parent_id"] == 1
        assert call_kwargs["search"] == "test"


class TestCreateCategory:
    """Test POST /categories endpoint."""

    async def test_create_category_success(
        self,
        mock_category_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful category creation by HR."""
        category_data = CategoryCreate(
            name="New Category",
            slug="new-category",
            description="Description",
        )

        result = await create_category(
            category_data=category_data,
            category_service=mock_category_service,
            _current_user=mock_hr_user,
        )

        assert isinstance(result, CategoryResponse)
        mock_category_service.create_category.assert_called_once_with(category_data)

    async def test_create_category_validation_error(
        self,
        mock_category_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test category creation with validation error."""
        mock_category_service.create_category.side_effect = ValidationException("Invalid data")

        category_data = CategoryCreate(
            name="Invalid",
            slug="invalid",
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_category(
                category_data=category_data,
                category_service=mock_category_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_category_conflict_error(
        self,
        mock_category_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test category creation with conflict error (duplicate slug)."""
        mock_category_service.create_category.side_effect = ConflictException("Category already exists")

        category_data = CategoryCreate(
            name="Duplicate",
            slug="duplicate",
        )

        with pytest.raises(ConflictException):
            await create_category(
                category_data=category_data,
                category_service=mock_category_service,
                _current_user=mock_hr_user,
            )


class TestGetCategory:
    """Test GET /categories/{category_id_or_slug} endpoint."""

    async def test_get_category_by_id(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting category by ID."""
        result = await get_category(
            category_id_or_slug="1",
            category_service=mock_category_service,
            current_user=mock_user,
        )

        assert isinstance(result, CategoryResponse)
        mock_category_service.get_category_by_id.assert_called_once_with(1)

    async def test_get_category_by_slug(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting category by slug."""
        mock_category_service.get_category_by_id.side_effect = ValueError("not an int")

        result = await get_category(
            category_id_or_slug="test-category",
            category_service=mock_category_service,
            current_user=mock_user,
        )

        assert isinstance(result, CategoryResponse)
        mock_category_service.get_category_by_slug.assert_called_once_with("test-category")

    async def test_get_category_not_found(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting non-existent category."""
        mock_category_service.get_category_by_id.side_effect = NotFoundException("Category")

        with pytest.raises(HTTPException) as exc_info:
            await get_category(
                category_id_or_slug="999",
                category_service=mock_category_service,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_category_with_articles(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
        mock_category: Category,
    ) -> None:
        """Test getting category with articles included."""
        mock_category.department_id = mock_user.department_id
        mock_category.articles = []
        mock_category_service.get_category_by_id.return_value = mock_category

        result = await get_category(
            category_id_or_slug="1",
            category_service=mock_category_service,
            current_user=mock_user,
            include_articles=True,
        )

        assert isinstance(result, CategoryResponse)

    async def test_get_category_other_department_denied(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
        mock_category: Category,
    ) -> None:
        """Test user cannot access categories from other departments."""
        mock_category.department_id = 999  # Different department
        mock_category_service.get_category_by_id.return_value = mock_category

        with pytest.raises(HTTPException) as exc_info:
            await get_category(
                category_id_or_slug="1",
                category_service=mock_category_service,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateCategory:
    """Test PUT /categories/{category_id} endpoint."""

    async def test_update_category_success(
        self,
        mock_category_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful category update by HR."""
        update_data = CategoryUpdate(name="Updated Category")

        result = await update_category(
            category_id=1,
            category_data=update_data,
            category_service=mock_category_service,
            _current_user=mock_hr_user,
        )

        assert isinstance(result, CategoryResponse)
        mock_category_service.update_category.assert_called_once_with(1, update_data)

    async def test_update_category_not_found(
        self,
        mock_category_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test updating non-existent category."""
        mock_category_service.update_category.side_effect = NotFoundException("Category")

        with pytest.raises(HTTPException) as exc_info:
            await update_category(
                category_id=999,
                category_data=CategoryUpdate(name="Test"),
                category_service=mock_category_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_category_validation_error(
        self,
        mock_category_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test category update with validation error."""
        mock_category_service.update_category.side_effect = ValidationException("Invalid data")

        with pytest.raises(HTTPException) as exc_info:
            await update_category(
                category_id=1,
                category_data=CategoryUpdate(name="Test"),
                category_service=mock_category_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestDeleteCategory:
    """Test DELETE /categories/{category_id} endpoint."""

    async def test_delete_category_success(
        self,
        mock_category_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test successful category deletion by admin."""
        result = await delete_category(
            category_id=1,
            category_service=mock_category_service,
            _current_user=mock_admin_user,
        )

        assert result.message == "Category deleted successfully"
        mock_category_service.delete_category.assert_called_once_with(1)

    async def test_delete_category_not_found(
        self,
        mock_category_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test deleting non-existent category."""
        mock_category_service.delete_category.side_effect = NotFoundException("Category")

        with pytest.raises(HTTPException) as exc_info:
            await delete_category(
                category_id=999,
                category_service=mock_category_service,
                _current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_category_validation_error(
        self,
        mock_category_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test deleting category with articles (validation error)."""
        mock_category_service.delete_category.side_effect = ValidationException("Cannot delete category with articles")

        with pytest.raises(HTTPException) as exc_info:
            await delete_category(
                category_id=1,
                category_service=mock_category_service,
                _current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestGetDepartmentCategories:
    """Test GET /categories/department/{department_id} endpoint."""

    async def test_get_department_categories_success(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting categories for user's department."""
        result = await get_department_categories(
            department_id=mock_user.department_id,
            category_service=mock_category_service,
            current_user=mock_user,
        )

        assert len(result) == 2  # mock_category and mock_child_category
        mock_category_service.get_department_categories.assert_called_once_with(mock_user.department_id)

    async def test_get_other_department_categories_as_admin(
        self,
        mock_category_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test admin can view any department's categories."""
        result = await get_department_categories(
            department_id=999,
            category_service=mock_category_service,
            current_user=mock_admin_user,
        )

        assert len(result) == 2

    async def test_get_other_department_categories_denied(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test user cannot view other department's categories."""
        with pytest.raises(HTTPException) as exc_info:
            await get_department_categories(
                department_id=999,
                category_service=mock_category_service,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestGetCategoryTree:
    """Test GET /categories/tree/{department_id} endpoint."""

    async def test_get_category_tree_success(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting category tree for user's department."""
        result = await get_category_tree(
            department_id=mock_user.department_id,
            category_service=mock_category_service,
            current_user=mock_user,
        )

        assert len(result) == 1
        assert result[0]["id"] == 1
        assert len(result[0]["children"]) == 1
        mock_category_service.get_category_tree.assert_called_once_with(mock_user.department_id)

    async def test_get_category_tree_as_admin(
        self,
        mock_category_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test admin can view any department's category tree."""
        result = await get_category_tree(
            department_id=999,
            category_service=mock_category_service,
            current_user=mock_admin_user,
        )

        assert len(result) == 1

    async def test_get_category_tree_other_department_denied(
        self,
        mock_category_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test user cannot view other department's category tree."""
        with pytest.raises(HTTPException) as exc_info:
            await get_category_tree(
                department_id=999,
                category_service=mock_category_service,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
