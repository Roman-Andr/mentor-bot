"""Unit tests for knowledge_service internal maintenance endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.api.internal import cleanup_user_knowledge_data


def make_scalars(ids: list) -> MagicMock:
    r = MagicMock()
    r.scalars.return_value = ids
    return r


def make_result(count: int | None) -> MagicMock:
    r = MagicMock()
    r.rowcount = count
    return r


@pytest.fixture
def mock_uow() -> MagicMock:
    uow = MagicMock()
    uow._session = AsyncMock()
    uow.commit = AsyncMock()
    return uow


class TestCleanupUserKnowledgeData:
    async def test_cleanup_with_articles(self, mock_uow: MagicMock) -> None:
        """Returns correct counts when user has articles."""
        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_scalars([1, 2]),  # article_ids
                make_result(1),  # article_history (by user)
                make_result(2),  # category_history
                make_result(0),  # dialogue_history
                make_result(3),  # search_history
                make_result(4),  # article_views (by user)
                make_result(5),  # article_view_history (by user)
                make_result(0),  # department_documents
                make_result(6),  # article_history (by article_id)
                make_result(7),  # views_by_article
                make_result(8),  # view_history_by_article
                MagicMock(),  # delete article_tags
                make_result(9),  # articles deleted
                make_result(0),  # anonymized_articles
            ]
        )

        result = await cleanup_user_knowledge_data(user_id=42, uow=mock_uow, _service_auth=None)

        assert result["articles"] == 9
        assert result["anonymized_articles"] == 0
        assert result["article_history"] == 1 + 6
        assert result["category_history"] == 2
        assert result["search_history"] == 3
        assert result["article_views"] == 4 + 7
        assert result["article_view_history"] == 5 + 8
        assert result["department_documents"] == 0
        mock_uow.commit.assert_awaited_once()

    async def test_cleanup_without_articles(self, mock_uow: MagicMock) -> None:
        """Returns zero article counts when user has no articles."""
        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_scalars([]),  # no article_ids
                make_result(0),  # article_history
                make_result(0),  # category_history
                make_result(0),  # dialogue_history
                make_result(0),  # search_history
                make_result(0),  # article_views
                make_result(0),  # article_view_history
                make_result(0),  # department_documents
                make_result(1),  # anonymized_articles
            ]
        )

        result = await cleanup_user_knowledge_data(user_id=99, uow=mock_uow, _service_auth=None)

        assert result["articles"] == 0
        assert result["anonymized_articles"] == 1
        assert result["article_history"] == 0
        mock_uow.commit.assert_awaited_once()

    async def test_cleanup_handles_none_rowcount(self, mock_uow: MagicMock) -> None:
        """Returns 0 for None rowcount values."""
        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_scalars([]),
                make_result(None),
                make_result(None),
                make_result(None),
                make_result(None),
                make_result(None),
                make_result(None),
                make_result(None),
                make_result(None),
            ]
        )

        result = await cleanup_user_knowledge_data(user_id=1, uow=mock_uow, _service_auth=None)

        assert result["articles"] == 0
        assert result["anonymized_articles"] == 0
        assert result["search_history"] == 0

    async def test_cleanup_raises_if_session_none(self) -> None:
        """Raises RuntimeError when session is not initialized."""
        mock_uow = MagicMock()
        mock_uow._session = None

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await cleanup_user_knowledge_data(user_id=1, uow=mock_uow, _service_auth=None)
