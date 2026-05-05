"""Tests for tag API endpoints."""

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status
from knowledge_service.api.deps import UserInfo
from knowledge_service.api.endpoints.tags import (
    create_tag,
    delete_tag,
    get_article_tags,
    get_popular_tags,
    get_tag,
    get_tags,
    merge_tags,
    update_tag,
)
from knowledge_service.core import ConflictException, NotFoundException, ValidationException
from knowledge_service.schemas import TagCreate, TagResponse, TagUpdate

if TYPE_CHECKING:
    pass


class TestGetTags:
    """Test GET /tags endpoint."""

    async def test_get_tags_success(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful retrieval of tags."""
        result = await get_tags(
            tag_service=mock_tag_service,
            _current_user=mock_user,
        )

        assert len(result) == 1
        assert isinstance(result[0], TagResponse)
        mock_tag_service.get_tags.assert_called_once()

    async def test_get_tags_with_pagination(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting tags with pagination."""
        await get_tags(
            tag_service=mock_tag_service,
            _current_user=mock_user,
            skip=10,
            limit=20,
        )

        call_kwargs = mock_tag_service.get_tags.call_args[1]
        assert call_kwargs["skip"] == 10
        assert call_kwargs["limit"] == 20

    async def test_get_tags_with_search(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting tags with search."""
        await get_tags(
            tag_service=mock_tag_service,
            _current_user=mock_user,
            search="test",
        )

        call_kwargs = mock_tag_service.get_tags.call_args[1]
        assert call_kwargs["search"] == "test"

    async def test_get_tags_with_sorting(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting tags with custom sorting."""
        await get_tags(
            tag_service=mock_tag_service,
            _current_user=mock_user,
            sort_by="name",
            sort_desc=False,
        )

        call_kwargs = mock_tag_service.get_tags.call_args[1]
        assert call_kwargs["sort_by"] == "name"
        assert call_kwargs["sort_desc"] is False


class TestGetPopularTags:
    """Test GET /tags/popular endpoint."""

    async def test_get_popular_tags_success(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful retrieval of popular tags."""
        result = await get_popular_tags(
            tag_service=mock_tag_service,
            _current_user=mock_user,
        )

        assert len(result) == 1
        mock_tag_service.get_popular_tags.assert_called_once_with(20)

    async def test_get_popular_tags_with_limit(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting popular tags with custom limit."""
        await get_popular_tags(
            tag_service=mock_tag_service,
            _current_user=mock_user,
            limit=10,
        )

        mock_tag_service.get_popular_tags.assert_called_once_with(10)


class TestCreateTag:
    """Test POST /tags endpoint."""

    async def test_create_tag_success(
        self,
        mock_tag_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful tag creation by HR."""
        tag_data = TagCreate(
            name="New Tag",
            slug="new-tag",
            description="Description",
        )

        result = await create_tag(
            tag_data=tag_data,
            tag_service=mock_tag_service,
            _current_user=mock_hr_user,
        )

        assert isinstance(result, TagResponse)
        mock_tag_service.create_tag.assert_called_once_with(tag_data)

    async def test_create_tag_validation_error(
        self,
        mock_tag_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test tag creation with validation error."""
        mock_tag_service.create_tag.side_effect = ValidationException("Tag already exists")

        tag_data = TagCreate(
            name="Duplicate",
            slug="duplicate",
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_tag(
                tag_data=tag_data,
                tag_service=mock_tag_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_tag_conflict_error(
        self,
        mock_tag_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test tag creation with conflict error (duplicate slug)."""
        mock_tag_service.create_tag.side_effect = ConflictException("Tag already exists")

        tag_data = TagCreate(
            name="Duplicate",
            slug="duplicate",
        )

        with pytest.raises(ConflictException):
            await create_tag(
                tag_data=tag_data,
                tag_service=mock_tag_service,
                _current_user=mock_hr_user,
            )


class TestGetTag:
    """Test GET /tags/{tag_id_or_slug} endpoint."""

    async def test_get_tag_by_id(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting tag by ID."""
        result = await get_tag(
            tag_id_or_slug="1",
            tag_service=mock_tag_service,
            _current_user=mock_user,
        )

        assert isinstance(result, TagResponse)
        mock_tag_service.get_tag_by_id.assert_called_once_with(1)

    async def test_get_tag_by_slug(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting tag by slug."""
        mock_tag_service.get_tag_by_id.side_effect = ValueError("not an int")

        result = await get_tag(
            tag_id_or_slug="test-tag",
            tag_service=mock_tag_service,
            _current_user=mock_user,
        )

        assert isinstance(result, TagResponse)
        mock_tag_service.get_tag_by_slug.assert_called_once_with("test-tag")

    async def test_get_tag_not_found(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting non-existent tag."""
        mock_tag_service.get_tag_by_id.side_effect = NotFoundException("Tag")

        with pytest.raises(HTTPException) as exc_info:
            await get_tag(
                tag_id_or_slug="999",
                tag_service=mock_tag_service,
                _current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateTag:
    """Test PUT /tags/{tag_id} endpoint."""

    async def test_update_tag_success(
        self,
        mock_tag_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful tag update by HR."""
        update_data = TagUpdate(
            name="Updated Tag",
            description="Updated description",
        )

        result = await update_tag(
            tag_id=1,
            tag_data=update_data,
            tag_service=mock_tag_service,
            _current_user=mock_hr_user,
        )

        assert isinstance(result, TagResponse)
        mock_tag_service.update_tag.assert_called_once_with(1, update_data)

    async def test_update_tag_not_found(
        self,
        mock_tag_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test updating non-existent tag."""
        mock_tag_service.update_tag.side_effect = NotFoundException("Tag")

        with pytest.raises(HTTPException) as exc_info:
            await update_tag(
                tag_id=999,
                tag_data=TagUpdate(name="Test"),
                tag_service=mock_tag_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_tag_validation_error(
        self,
        mock_tag_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test tag update with validation error."""
        mock_tag_service.update_tag.side_effect = ValidationException("Duplicate slug")

        with pytest.raises(HTTPException) as exc_info:
            await update_tag(
                tag_id=1,
                tag_data=TagUpdate(name="Test"),
                tag_service=mock_tag_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestDeleteTag:
    """Test DELETE /tags/{tag_id} endpoint."""

    async def test_delete_tag_success(
        self,
        mock_tag_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test successful tag deletion by admin."""
        result = await delete_tag(
            tag_id=1,
            tag_service=mock_tag_service,
            _current_user=mock_admin_user,
        )

        assert result.message == "Tag deleted successfully"
        mock_tag_service.delete_tag.assert_called_once_with(1)

    async def test_delete_tag_not_found(
        self,
        mock_tag_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test deleting non-existent tag."""
        mock_tag_service.delete_tag.side_effect = NotFoundException("Tag")

        with pytest.raises(HTTPException) as exc_info:
            await delete_tag(
                tag_id=999,
                tag_service=mock_tag_service,
                _current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_tag_in_use(
        self,
        mock_tag_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test deleting tag that is in use."""
        mock_tag_service.delete_tag.side_effect = ValidationException("Cannot delete tag that is in use by articles")

        with pytest.raises(HTTPException) as exc_info:
            await delete_tag(
                tag_id=1,
                tag_service=mock_tag_service,
                _current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestMergeTags:
    """Test POST /tags/{source_tag_id}/merge/{target_tag_id} endpoint."""

    async def test_merge_tags_success(
        self,
        mock_tag_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test successful tag merge by admin."""
        result = await merge_tags(
            source_tag_id=1,
            target_tag_id=2,
            tag_service=mock_tag_service,
            _current_user=mock_admin_user,
        )

        assert isinstance(result, TagResponse)
        mock_tag_service.merge_tags.assert_called_once_with(1, 2)

    async def test_merge_tags_not_found(
        self,
        mock_tag_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test merging non-existent tag."""
        mock_tag_service.merge_tags.side_effect = NotFoundException("Tag")

        with pytest.raises(HTTPException) as exc_info:
            await merge_tags(
                source_tag_id=1,
                target_tag_id=999,
                tag_service=mock_tag_service,
                _current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_merge_tags_validation_error(
        self,
        mock_tag_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test tag merge with validation error."""
        mock_tag_service.merge_tags.side_effect = ValidationException("Cannot merge tag with itself")

        with pytest.raises(HTTPException) as exc_info:
            await merge_tags(
                source_tag_id=1,
                target_tag_id=2,
                tag_service=mock_tag_service,
                _current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestGetArticleTags:
    """Test GET /tags/article/{article_id} endpoint."""

    async def test_get_article_tags_success(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful retrieval of article tags."""
        result = await get_article_tags(
            article_id=1,
            tag_service=mock_tag_service,
            _current_user=mock_user,
        )

        assert len(result) == 1
        mock_tag_service.get_tags_by_article.assert_called_once_with(1)

    async def test_get_article_tags_error(
        self,
        mock_tag_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test error handling when getting article tags."""
        mock_tag_service.get_tags_by_article.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await get_article_tags(
                article_id=1,
                tag_service=mock_tag_service,
                _current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
