"""Tests for search service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from knowledge_service.core import ArticleStatus, SearchSortBy
from knowledge_service.models import Article, Category, Tag
from knowledge_service.services.search import SearchService


@pytest.fixture
def mock_uow():
    """Create a mock Unit of Work."""
    uow = MagicMock()
    uow.articles = AsyncMock()
    uow.search_history = AsyncMock()
    uow.commit = AsyncMock()
    # session.execute needs to be awaitable
    session_mock = MagicMock()
    session_mock.execute = AsyncMock()
    uow.session = session_mock
    return uow


@pytest.fixture
def sample_category():
    """Create a sample category."""
    return Category(
        id=1,
        name="Test Category",
        slug="test-category",
        description="Test description",
        parent_id=None,
        order=0,
        department_id=1,
        position="Developer",
        level="JUNIOR",
        icon="folder",
        color="#000000",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_tag():
    """Create a sample tag."""
    return Tag(
        id=1,
        name="Python",
        slug="python",
        description="Python programming",
        usage_count=5,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_article(sample_category, sample_tag):
    """Create a sample article for testing."""
    article = Article(
        id=1,
        title="Test Article",
        slug="test-article",
        content="This is test content about Python",
        excerpt="Test excerpt about Python",
        category_id=1,
        author_id=1,
        author_name="Test Author",
        department_id=1,
        position="Developer",
        level="JUNIOR",
        status=ArticleStatus.PUBLISHED,
        is_pinned=False,
        is_featured=False,
        meta_title=None,
        meta_description=None,
        keywords=["python", "test"],
        view_count=10,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        published_at=datetime.now(UTC),
    )
    article.category = sample_category
    article.tags = [sample_tag]
    return article


class TestSearchArticles:
    """Tests for searching articles."""

    async def test_search_articles_cached(self, mock_uow):
        """Test searching articles with cached results."""
        cached_data = {
            "results": [{"id": 1, "title": "Cached"}],
            "total": 1,
            "suggestions": ["suggestion"],
        }

        with patch("knowledge_service.services.search.cache.get", return_value=cached_data):
            service = SearchService(mock_uow)
            filters = {}

            results, total, suggestions = await service.search_articles(
                query="python",
                filters=filters,
                sort_by=SearchSortBy.RELEVANCE,
                page=1,
                size=10,
            )

            assert results == cached_data["results"]
            assert total == 1
            assert suggestions == ["suggestion"]
            # Verify cache was checked
            assert mock_uow.session.execute.call_count == 0

    async def test_search_articles_no_results_with_user(self, mock_uow):
        """Test search with no results records history for user."""
        # Mock count query returning 0
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 0

        # Mock id query returning empty
        mock_id_result = MagicMock()
        mock_id_result.all.return_value = []

        mock_uow.session.execute.side_effect = [mock_count_result, mock_id_result]

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", new_callable=AsyncMock):
                service = SearchService(mock_uow)
                results, total, suggestions = await service.search_articles(
                    query="nonexistent",
                    filters={},
                    sort_by=SearchSortBy.RELEVANCE,
                    page=1,
                    size=10,
                    user_id=42,
                    user_filters={"department_id": 1},
                )

                assert results == []
                assert total == 0
                assert suggestions == []
                mock_uow.search_history.record_search.assert_called_once()
                mock_uow.commit.assert_called_once()

    async def test_search_articles_no_results_without_user(self, mock_uow):
        """Test search with no results without user (no history recorded)."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 0

        mock_id_result = MagicMock()
        mock_id_result.all.return_value = []

        mock_uow.session.execute.side_effect = [mock_count_result, mock_id_result]

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", new_callable=AsyncMock):
                service = SearchService(mock_uow)
                results, total, suggestions = await service.search_articles(
                    query="nonexistent",
                    filters={},
                    sort_by=SearchSortBy.RELEVANCE,
                    page=1,
                    size=10,
                )

                assert results == []
                assert total == 0
                assert suggestions == []
                mock_uow.search_history.record_search.assert_not_called()

    async def test_search_articles_with_filters(self, mock_uow, sample_article):
        """Test search with various filters applied."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_id_result = MagicMock()
        mock_id_result.all.return_value = [(1, 0.95)]

        mock_article_result = MagicMock()
        mock_article_result.scalars.return_value.unique.return_value.all.return_value = [sample_article]

        # Mock for title search in get_search_suggestions
        mock_title_result = MagicMock()
        mock_title_result.all.return_value = []

        mock_uow.session.execute.side_effect = [
            mock_count_result,
            mock_id_result,
            mock_article_result,
            mock_title_result,
        ]

        mock_uow.search_history.get_suggestions.return_value = []

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", new_callable=AsyncMock):
                service = SearchService(mock_uow)
                filters = {
                    "category_id": 1,
                    "tag_ids": [1, 2],
                    "department_id": 1,
                    "position": "Developer",
                    "level": "JUNIOR",
                    "only_published": True,
                }
                results, total, _suggestions = await service.search_articles(
                    query="python",
                    filters=filters,
                    sort_by=SearchSortBy.RELEVANCE,
                    page=1,
                    size=10,
                )

                assert total == 1
                assert len(results) == 1

    async def test_search_articles_with_user_filters(self, mock_uow, sample_article):
        """Test search with user-specific filters."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_id_result = MagicMock()
        mock_id_result.all.return_value = [(1, 0.95)]

        mock_article_result = MagicMock()
        mock_article_result.scalars.return_value.unique.return_value.all.return_value = [sample_article]

        # Mock for title search in get_search_suggestions
        mock_title_result = MagicMock()
        mock_title_result.all.return_value = []

        mock_uow.session.execute.side_effect = [
            mock_count_result,
            mock_id_result,
            mock_article_result,
            mock_title_result,
        ]

        mock_uow.search_history.get_suggestions.return_value = []

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", new_callable=AsyncMock):
                service = SearchService(mock_uow)
                _results, total, _ = await service.search_articles(
                    query="python",
                    filters={},
                    sort_by=SearchSortBy.RELEVANCE,
                    page=1,
                    size=10,
                    user_id=1,
                    user_filters={
                        "department_id": 1,
                        "position": "Developer",
                        "level": "JUNIOR",
                    },
                )

                assert total == 1

    async def test_search_articles_sort_by_date_newest(self, mock_uow, sample_article):
        """Test search sorted by date newest."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_id_result = MagicMock()
        mock_id_result.all.return_value = [(1, 1.0)]

        mock_article_result = MagicMock()
        mock_article_result.scalars.return_value.unique.return_value.all.return_value = [sample_article]

        mock_uow.session.execute.side_effect = [
            mock_count_result,
            mock_id_result,
            mock_article_result,
        ]

        mock_uow.search_history.get_suggestions.return_value = []

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", new_callable=AsyncMock):
                service = SearchService(mock_uow)
                _results, total, _ = await service.search_articles(
                    query="",
                    filters={},
                    sort_by=SearchSortBy.DATE_NEWEST,
                    page=1,
                    size=10,
                )

                assert total == 1

    async def test_search_articles_sort_by_date_oldest(self, mock_uow, sample_article):
        """Test search sorted by date oldest."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_id_result = MagicMock()
        mock_id_result.all.return_value = [(1, 1.0)]

        mock_article_result = MagicMock()
        mock_article_result.scalars.return_value.unique.return_value.all.return_value = [sample_article]

        mock_uow.session.execute.side_effect = [
            mock_count_result,
            mock_id_result,
            mock_article_result,
        ]

        mock_uow.search_history.get_suggestions.return_value = []

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", new_callable=AsyncMock):
                service = SearchService(mock_uow)
                _results, total, _ = await service.search_articles(
                    query="",
                    filters={},
                    sort_by=SearchSortBy.DATE_OLDEST,
                    page=1,
                    size=10,
                )

                assert total == 1

    async def test_search_articles_sort_by_views(self, mock_uow, sample_article):
        """Test search sorted by views."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_id_result = MagicMock()
        mock_id_result.all.return_value = [(1, 1.0)]

        mock_article_result = MagicMock()
        mock_article_result.scalars.return_value.unique.return_value.all.return_value = [sample_article]

        mock_uow.session.execute.side_effect = [
            mock_count_result,
            mock_id_result,
            mock_article_result,
        ]

        mock_uow.search_history.get_suggestions.return_value = []

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", new_callable=AsyncMock):
                service = SearchService(mock_uow)
                _results, total, _ = await service.search_articles(
                    query="",
                    filters={},
                    sort_by=SearchSortBy.VIEWS,
                    page=1,
                    size=10,
                )

                assert total == 1

    async def test_search_articles_sort_by_title(self, mock_uow, sample_article):
        """Test search sorted by title."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_id_result = MagicMock()
        mock_id_result.all.return_value = [(1, 1.0)]

        mock_article_result = MagicMock()
        mock_article_result.scalars.return_value.unique.return_value.all.return_value = [sample_article]

        mock_uow.session.execute.side_effect = [
            mock_count_result,
            mock_id_result,
            mock_article_result,
        ]

        mock_uow.search_history.get_suggestions.return_value = []

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", new_callable=AsyncMock):
                service = SearchService(mock_uow)
                _results, total, _ = await service.search_articles(
                    query="",
                    filters={},
                    sort_by=SearchSortBy.TITLE,
                    page=1,
                    size=10,
                )

                assert total == 1

    async def test_search_articles_pagination_page_2(self, mock_uow, sample_article):
        """Test search with pagination (page 2)."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 25

        mock_id_result = MagicMock()
        mock_id_result.all.return_value = [(1, 0.95)]

        mock_article_result = MagicMock()
        mock_article_result.scalars.return_value.unique.return_value.all.return_value = [sample_article]

        # Mock for title search in get_search_suggestions
        mock_title_result = MagicMock()
        mock_title_result.all.return_value = []

        mock_uow.session.execute.side_effect = [
            mock_count_result,
            mock_id_result,
            mock_article_result,
            mock_title_result,
        ]

        mock_uow.search_history.get_suggestions.return_value = []

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", new_callable=AsyncMock):
                service = SearchService(mock_uow)
                results, total, _ = await service.search_articles(
                    query="python",
                    filters={},
                    sort_by=SearchSortBy.RELEVANCE,
                    page=2,
                    size=10,
                )

                assert total == 25
                assert len(results) == 1


class TestGetSearchSuggestions:
    """Tests for search suggestions."""

    async def test_get_suggestions_short_query(self, mock_uow):
        """Test getting suggestions with short query."""
        service = SearchService(mock_uow)
        result = await service.get_search_suggestions(query="a")

        assert result == []

    async def test_get_suggestions_cached(self, mock_uow):
        """Test getting cached suggestions."""
        cached = ["suggestion1", "suggestion2"]

        with patch("knowledge_service.services.search.cache.get", return_value=cached):
            service = SearchService(mock_uow)
            result = await service.get_search_suggestions(query="python")

            assert result == cached

    async def test_get_suggestions_from_history(self, mock_uow):
        """Test getting suggestions from history."""
        mock_uow.search_history.get_suggestions.return_value = ["python tutorial"]
        # Mock session.execute to return empty result for title search
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_uow.session.execute.return_value = mock_result

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", return_value=None):
                service = SearchService(mock_uow)
                result = await service.get_search_suggestions(query="python")

                assert len(result) == 1
                assert result[0] == "python tutorial"

    async def test_get_suggestions_with_department(self, mock_uow):
        """Test getting suggestions filtered by department."""
        mock_uow.search_history.get_suggestions.return_value = ["python tutorial"]

        # Mock for title search
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_uow.session.execute.return_value = mock_result

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", return_value=None):
                service = SearchService(mock_uow)
                _result = await service.get_search_suggestions(query="python", department_id=1)

                mock_uow.search_history.get_suggestions.assert_called_once_with("python", 1, 10)

    async def test_get_suggestions_from_titles(self, mock_uow):
        """Test getting suggestions from article titles when history is insufficient."""
        mock_uow.search_history.get_suggestions.return_value = ["python tutorial"]

        # Mock for title search returning more suggestions
        mock_result = MagicMock()
        mock_result.all.return_value = [("Python Basics",), ("Python Advanced",)]
        mock_uow.session.execute.return_value = mock_result

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", return_value=None):
                service = SearchService(mock_uow)
                result = await service.get_search_suggestions(query="python", limit=5)

                assert len(result) >= 1


class TestGetPopularSearches:
    """Tests for popular searches."""

    async def test_get_popular_searches_cached(self, mock_uow):
        """Test getting cached popular searches."""
        cached = [{"query": "python", "count": 100}]

        with patch("knowledge_service.services.search.cache.get", return_value=cached):
            service = SearchService(mock_uow)
            result = await service.get_popular_searches()

            assert result == cached

    async def test_get_popular_searches_from_db(self, mock_uow):
        """Test getting popular searches from database."""
        db_result = [{"query": "python", "count": 100}]
        mock_uow.search_history.get_popular_searches.return_value = db_result

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", return_value=None):
                service = SearchService(mock_uow)
                result = await service.get_popular_searches(limit=10)

                assert len(result) == 1
                assert result[0]["query"] == "python"

    async def test_get_popular_searches_with_department(self, mock_uow):
        """Test getting popular searches filtered by department."""
        db_result = [{"query": "python", "count": 50}]
        mock_uow.search_history.get_popular_searches.return_value = db_result

        with patch("knowledge_service.services.search.cache.get", return_value=None):
            with patch("knowledge_service.services.search.cache.set", return_value=None):
                service = SearchService(mock_uow)
                _result = await service.get_popular_searches(department_id=1, limit=10)

                mock_uow.search_history.get_popular_searches.assert_called_once_with(1, 10)


class TestGetUserSearchHistory:
    """Tests for user search history."""

    async def test_get_user_search_history(self, mock_uow):
        """Test getting user search history."""
        history_item = MagicMock()
        history_item.query = "python"
        history_item.results_count = 10
        mock_uow.search_history.find_by_user.return_value = ([history_item], 1)

        service = SearchService(mock_uow)
        result, total = await service.get_user_search_history(user_id=1, skip=0, limit=50)

        assert len(result) == 1
        assert total == 1
        mock_uow.search_history.find_by_user.assert_called_once_with(1, skip=0, limit=50)


class TestClearUserSearchHistory:
    """Tests for clearing user search history."""

    async def test_clear_user_search_history(self, mock_uow):
        """Test clearing user search history."""
        mock_uow.search_history.clear_user_history.return_value = 5

        service = SearchService(mock_uow)
        await service.clear_user_search_history(user_id=1)

        mock_uow.search_history.clear_user_history.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()


class TestGetSearchStats:
    """Tests for search statistics."""

    async def test_get_search_stats(self, mock_uow):
        """Test getting search statistics."""
        stats = {
            "total_searches": 100,
            "popular_queries": [],
            "no_results_queries": [],
            "searches_by_department": {},
            "avg_results_per_search": 5.0,
        }
        mock_uow.search_history.get_search_stats.return_value = stats

        service = SearchService(mock_uow)
        result = await service.get_search_stats()

        assert result == stats
        mock_uow.search_history.get_search_stats.assert_called_once()


class TestHighlightText:
    """Tests for text highlighting."""

    def test_highlight_text_basic(self):
        """Test basic text highlighting."""
        service = SearchService(None)
        result = service._highlight_text("This is a test about Python", "python")

        assert "<mark>" in result.lower()
        assert "python" in result.lower()

    def test_highlight_text_multiple_words(self):
        """Test highlighting multiple words."""
        service = SearchService(None)
        result = service._highlight_text("Learn Python and JavaScript programming", "python javascript")

        # Should highlight both words if they're long enough
        assert "<mark>" in result

    def test_highlight_text_short_word(self):
        """Test that short words are not highlighted."""
        service = SearchService(None)
        # "a" has length 1, which is < MIN_WORD_LENGTH_HIGHLIGHT (2)
        result = service._highlight_text("This is a test", "a")

        # Words under MIN_WORD_LENGTH_HIGHLIGHT (2) won't be highlighted
        assert "<mark>a</mark>" not in result

    def test_highlight_text_empty_text(self):
        """Test highlighting with empty text."""
        service = SearchService(None)
        result = service._highlight_text("", "query")

        assert result == ""

    def test_highlight_text_empty_query(self):
        """Test highlighting with empty query."""
        service = SearchService(None)
        result = service._highlight_text("This is a test", "")

        assert result == "This is a test"

    def test_highlight_text_case_insensitive(self):
        """Test case-insensitive highlighting."""
        service = SearchService(None)
        result = service._highlight_text("Learn PYTHON programming", "python")

        # Highlights with the query term (lowercase), not the matched text
        assert "<mark>python</mark>" in result.lower()

    def test_highlight_text_finds_case_insensitive(self):
        """Test that highlighting finds text case-insensitively."""
        service = SearchService(None)
        result = service._highlight_text("Python is great", "python")

        # The pattern should be found case-insensitively
        assert "<mark>python</mark>" in result.lower()
        assert "is great" in result

    def test_highlight_text_long_words_only(self):
        """Test that only words >= MIN_WORD_LENGTH_HIGHLIGHT are highlighted."""
        service = SearchService(None)
        # Word "ab" is exactly at limit (2), "a" is below
        result = service._highlight_text("Test with word ab and a", "ab a")

        # "ab" should be highlighted (length >= MIN_WORD_LENGTH_HIGHLIGHT)
        assert "<mark>ab</mark>" in result
        # "a" should not be highlighted (length < MIN_WORD_LENGTH_HIGHLIGHT)
        assert "<mark>a</mark>" not in result

    def test_highlight_text_partial_matches(self):
        """Test highlighting partial word matches."""
        service = SearchService(None)
        result = service._highlight_text("Testing pythonic code in Python", "python")

        # Should highlight "Python" but not "pythonic" (partial match)
        assert "<mark>Python</mark>" in result or "<mark>python</mark>" in result.lower()

    def test_highlight_text_multiple_occurrences(self):
        """Test highlighting multiple occurrences of the same word."""
        service = SearchService(None)
        result = service._highlight_text("Python is great. I love Python!", "python")

        # Both occurrences should be highlighted
        assert result.count("<mark>") == 2
