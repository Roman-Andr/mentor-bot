"""Tests for article API endpoints."""

from typing import TYPE_CHECKING

import pytest
from fastapi import HTTPException, status

from knowledge_service.api.endpoints.articles import (
    create_article,
    delete_article,
    get_article,
    get_article_stats,
    get_articles,
    get_department_articles,
    publish_article,
    update_article,
)
from knowledge_service.core import ArticleStatus, NotFoundException, PermissionDenied
from knowledge_service.models import Article
from knowledge_service.schemas import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
)

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from knowledge_service.api.deps import UserInfo


class TestGetArticles:
    """Test GET /articles endpoint."""

    async def test_get_articles_success(
        self,
        mock_article_service: AsyncMock,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful retrieval of articles."""
        result = await get_articles(
            article_service=mock_article_service,
            search_service=mock_search_service,
            current_user=mock_user,
        )

        assert isinstance(result, ArticleListResponse)
        assert result.total == 1
        assert len(result.articles) == 1
        mock_article_service.get_articles.assert_called_once()

    async def test_get_articles_with_search(
        self,
        mock_article_service: AsyncMock,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test article search functionality."""
        result = await get_articles(
            article_service=mock_article_service,
            search_service=mock_search_service,
            current_user=mock_user,
            search="test query",
        )

        assert isinstance(result, ArticleListResponse)
        mock_search_service.search_articles.assert_called_once()

    async def test_get_articles_with_filters(
        self,
        mock_article_service: AsyncMock,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test retrieving articles with various filters."""
        result = await get_articles(
            article_service=mock_article_service,
            search_service=mock_search_service,
            current_user=mock_user,
            skip=10,
            limit=20,
            category_id=1,
            tag_id=2,
            department_id=1,
            status="published",
            featured_only=True,
            pinned_only=False,
        )

        assert isinstance(result, ArticleListResponse)
        mock_article_service.get_articles.assert_called_once()
        call_kwargs = mock_article_service.get_articles.call_args[1]
        assert call_kwargs["skip"] == 10
        assert call_kwargs["limit"] == 20
        assert call_kwargs["category_id"] == 1
        assert call_kwargs["tag_id"] == 2

    async def test_get_articles_non_admin_user_filters(
        self,
        mock_article_service: AsyncMock,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test that non-admin users get department filtering applied."""
        await get_articles(
            article_service=mock_article_service,
            search_service=mock_search_service,
            current_user=mock_user,
        )

        call_kwargs = mock_article_service.get_articles.call_args[1]
        assert "user_filters" in call_kwargs
        assert call_kwargs["user_filters"]["department_id"] == mock_user.department_id

    async def test_get_articles_admin_no_user_filters(
        self,
        mock_article_service: AsyncMock,
        mock_search_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test that admin users don't get automatic department filtering."""
        await get_articles(
            article_service=mock_article_service,
            search_service=mock_search_service,
            current_user=mock_admin_user,
        )

        call_kwargs = mock_article_service.get_articles.call_args[1]
        assert call_kwargs.get("user_filters") == {}


class TestCreateArticle:
    """Test POST /articles endpoint."""

    async def test_create_article_success(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful article creation."""
        article_data = ArticleCreate(
            title="New Article",
            content="Article content",
            category_id=1,
        )

        result = await create_article(
            article_data=article_data,
            article_service=mock_article_service,
            current_user=mock_user,
        )

        assert isinstance(result, ArticleResponse)
        mock_article_service.create_article.assert_called_once_with(article_data, mock_user.id, mock_user.first_name)

    async def test_create_article_validation_error(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test article creation with validation error."""
        mock_article_service.create_article.side_effect = ValueError("Invalid data")

        article_data = ArticleCreate(
            title="New Article",
            content="Content",
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_article(
                article_data=article_data,
                article_service=mock_article_service,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestGetArticle:
    """Test GET /articles/{article_id_or_slug} endpoint."""

    async def test_get_article_by_id(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting article by ID."""
        result = await get_article(
            article_id_or_slug="1",
            article_service=mock_article_service,
            current_user=mock_user,
        )

        assert isinstance(result, ArticleResponse)
        mock_article_service.get_article_by_id.assert_called_once_with(1)
        mock_article_service.record_view.assert_called_once()

    async def test_get_article_by_slug(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting article by slug."""
        mock_article_service.get_article_by_id.side_effect = ValueError("not an int")

        result = await get_article(
            article_id_or_slug="test-article",
            article_service=mock_article_service,
            current_user=mock_user,
        )

        assert isinstance(result, ArticleResponse)
        mock_article_service.get_article_by_slug.assert_called_once_with("test-article")

    async def test_get_article_not_found(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting non-existent article."""
        mock_article_service.get_article_by_id.side_effect = NotFoundException(Article)

        with pytest.raises(HTTPException) as exc_info:
            await get_article(
                article_id_or_slug="999",
                article_service=mock_article_service,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_draft_article_as_author(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_draft_article: Article,
    ) -> None:
        """Test author can view their own draft article."""
        mock_draft_article.status = ArticleStatus.DRAFT
        mock_draft_article.author_id = mock_user.id
        mock_draft_article.department_id = mock_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_draft_article

        result = await get_article(
            article_id_or_slug="1",
            article_service=mock_article_service,
            current_user=mock_user,
        )

        assert result is not None

    async def test_get_draft_article_as_other_user_denied(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_draft_article: Article,
    ) -> None:
        """Test non-author cannot view draft article."""
        mock_draft_article.status = ArticleStatus.DRAFT
        mock_draft_article.author_id = 999  # Different user
        mock_draft_article.department_id = mock_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_draft_article

        with pytest.raises(PermissionDenied):
            await get_article(
                article_id_or_slug="1",
                article_service=mock_article_service,
                current_user=mock_user,
            )

    async def test_get_article_other_department_denied(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test user cannot access articles from other departments."""
        mock_article.status = ArticleStatus.PUBLISHED
        mock_article.department_id = 999  # Different department
        mock_article_service.get_article_by_id.return_value = mock_article

        with pytest.raises(PermissionDenied):
            await get_article(
                article_id_or_slug="1",
                article_service=mock_article_service,
                current_user=mock_user,
            )


class TestUpdateArticle:
    """Test PUT /articles/{article_id} endpoint."""

    async def test_update_article_success(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test successful article update by author."""
        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        update_data = ArticleUpdate(title="Updated Title")

        result = await update_article(
            article_id=1,
            article_data=update_data,
            article_service=mock_article_service,
            current_user=mock_user,
        )

        assert isinstance(result, ArticleResponse)
        mock_article_service.update_article.assert_called_once_with(1, update_data)

    async def test_update_article_as_admin(
        self,
        mock_article_service: AsyncMock,
        mock_admin_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test admin can update any article."""
        mock_article.author_id = 999  # Different user
        mock_article_service.get_article_by_id.return_value = mock_article

        update_data = ArticleUpdate(title="Admin Updated")

        result = await update_article(
            article_id=1,
            article_data=update_data,
            article_service=mock_article_service,
            current_user=mock_admin_user,
        )

        assert isinstance(result, ArticleResponse)

    async def test_update_other_user_article_denied(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test non-author cannot update others' articles."""
        mock_article.author_id = 999  # Different user
        mock_article_service.get_article_by_id.return_value = mock_article

        update_data = ArticleUpdate(title="Hacked Title")

        with pytest.raises(PermissionDenied):
            await update_article(
                article_id=1,
                article_data=update_data,
                article_service=mock_article_service,
                current_user=mock_user,
            )

    async def test_update_article_not_found(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test updating non-existent article."""
        mock_article_service.get_article_by_id.side_effect = NotFoundException(Article)

        with pytest.raises(HTTPException) as exc_info:
            await update_article(
                article_id=999,
                article_data=ArticleUpdate(title="Test"),
                article_service=mock_article_service,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteArticle:
    """Test DELETE /articles/{article_id} endpoint."""

    async def test_delete_article_success(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test successful article deletion by author."""
        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        result = await delete_article(
            article_id=1,
            article_service=mock_article_service,
            current_user=mock_user,
        )

        assert result.message == "Article deleted successfully"
        mock_article_service.delete_article.assert_called_once_with(1)

    async def test_delete_article_as_admin(
        self,
        mock_article_service: AsyncMock,
        mock_admin_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test admin can delete any article."""
        mock_article.author_id = 999
        mock_article_service.get_article_by_id.return_value = mock_article

        result = await delete_article(
            article_id=1,
            article_service=mock_article_service,
            current_user=mock_admin_user,
        )

        assert result.message == "Article deleted successfully"

    async def test_delete_other_user_article_denied(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test non-author cannot delete others' articles."""
        mock_article.author_id = 999
        mock_article_service.get_article_by_id.return_value = mock_article

        with pytest.raises(PermissionDenied):
            await delete_article(
                article_id=1,
                article_service=mock_article_service,
                current_user=mock_user,
            )


class TestPublishArticle:
    """Test POST /articles/{article_id}/publish endpoint."""

    async def test_publish_article_success(
        self,
        mock_article_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful article publishing by HR."""
        result = await publish_article(
            article_id=1,
            article_service=mock_article_service,
            _current_user=mock_hr_user,
        )

        assert isinstance(result, ArticleResponse)
        mock_article_service.publish_article.assert_called_once_with(1)

    async def test_publish_article_not_found(
        self,
        mock_article_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test publishing non-existent article."""
        mock_article_service.publish_article.side_effect = NotFoundException(Article)

        with pytest.raises(HTTPException) as exc_info:
            await publish_article(
                article_id=999,
                article_service=mock_article_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestGetArticleStats:
    """Test GET /articles/{article_id}/stats endpoint."""

    async def test_get_article_stats_success(
        self,
        mock_article_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful retrieval of article statistics."""
        result = await get_article_stats(
            article_id=1,
            article_service=mock_article_service,
            _current_user=mock_hr_user,
        )

        assert result.article_id == 1
        assert result.title == "Test Article"
        mock_article_service.get_article_stats.assert_called_once_with(1)

    async def test_get_article_stats_not_found(
        self,
        mock_article_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test getting stats for non-existent article."""
        mock_article_service.get_article_stats.side_effect = NotFoundException(Article)

        with pytest.raises(HTTPException) as exc_info:
            await get_article_stats(
                article_id=999,
                article_service=mock_article_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestGetDepartmentArticles:
    """Test GET /articles/department/{department_id} endpoint."""

    async def test_get_department_articles_success(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test getting articles for user's department."""
        result = await get_department_articles(
            department_id=mock_user.department_id,
            article_service=mock_article_service,
            current_user=mock_user,
        )

        assert isinstance(result, ArticleListResponse)
        mock_article_service.get_department_articles.assert_called_once_with(mock_user.department_id, 0, 50)

    async def test_get_other_department_articles_as_admin(
        self,
        mock_article_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test admin can view any department's articles."""
        result = await get_department_articles(
            department_id=999,
            article_service=mock_article_service,
            current_user=mock_admin_user,
        )

        assert isinstance(result, ArticleListResponse)

    async def test_get_other_department_articles_denied(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test user cannot view other department's articles."""
        with pytest.raises(PermissionDenied):
            await get_department_articles(
                department_id=999,
                article_service=mock_article_service,
                current_user=mock_user,
            )


class TestGetArticlesSearchEdgeCases:
    """Test search functionality edge cases."""

    async def test_get_articles_empty_search_results(
        self,
        mock_article_service: AsyncMock,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test handling of empty search results."""
        # Return empty results from search
        mock_search_service.search_articles.return_value = ([], 0, [])
        mock_article_service.get_articles_by_ids.return_value = []

        result = await get_articles(
            article_service=mock_article_service,
            search_service=mock_search_service,
            current_user=mock_user,
            search="nonexistent query",
        )

        assert isinstance(result, ArticleListResponse)
        assert result.total == 0
        assert len(result.articles) == 0
        mock_article_service.get_articles_by_ids.assert_not_called()


class TestDeleteArticleNotFound:
    """Test delete article error handling."""

    async def test_delete_article_not_found(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test deleting non-existent article returns 404."""
        mock_article_service.get_article_by_id.side_effect = NotFoundException(Article)

        with pytest.raises(HTTPException) as exc_info:
            await delete_article(
                article_id=999,
                article_service=mock_article_service,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
