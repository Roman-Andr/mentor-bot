"""Tests for cleanup service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from knowledge_service.services.cleanup import cleanup_old_search_history


class TestCleanupOldSearchHistory:
    """Test cleanup_old_search_history function."""

    @pytest.mark.asyncio
    async def test_cleanup_old_search_history_default_retention(self):
        """Test cleanup with default retention days from config."""
        mock_uow = MagicMock()
        mock_uow.search_history = AsyncMock()
        mock_uow.search_history.delete_old_search_history = AsyncMock(return_value=10)
        mock_uow.commit = AsyncMock()

        with patch("knowledge_service.services.cleanup.SqlAlchemyUnitOfWork") as mock_uow_class:
            mock_uow_class.return_value.__aenter__.return_value = mock_uow
            mock_uow_class.return_value.__aexit__.return_value = None

            result = await cleanup_old_search_history()

            assert result == 10
            mock_uow.search_history.delete_old_search_history.assert_called_once()
            mock_uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_old_search_history_custom_retention(self):
        """Test cleanup with custom retention days."""
        mock_uow = MagicMock()
        mock_uow.search_history = AsyncMock()
        mock_uow.search_history.delete_old_search_history = AsyncMock(return_value=5)
        mock_uow.commit = AsyncMock()

        with patch("knowledge_service.services.cleanup.SqlAlchemyUnitOfWork") as mock_uow_class:
            mock_uow_class.return_value.__aenter__.return_value = mock_uow
            mock_uow_class.return_value.__aexit__.return_value = None

            result = await cleanup_old_search_history(retention_days=30)

            assert result == 5
            mock_uow.search_history.delete_old_search_history.assert_called_once_with(30)
            mock_uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_old_search_history_zero_deleted(self):
        """Test cleanup when no records are deleted."""
        mock_uow = MagicMock()
        mock_uow.search_history = AsyncMock()
        mock_uow.search_history.delete_old_search_history = AsyncMock(return_value=0)
        mock_uow.commit = AsyncMock()

        with patch("knowledge_service.services.cleanup.SqlAlchemyUnitOfWork") as mock_uow_class:
            mock_uow_class.return_value.__aenter__.return_value = mock_uow
            mock_uow_class.return_value.__aexit__.return_value = None

            result = await cleanup_old_search_history()

            assert result == 0
