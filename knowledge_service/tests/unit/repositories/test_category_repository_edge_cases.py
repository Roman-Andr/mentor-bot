"""Tests for Category repository edge cases - covering line 117."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import Category
from knowledge_service.repositories.implementations.category import CategoryRepository


class TestCategoryRepositoryEdgeCases:
    """Test Category repository edge cases for missing coverage."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    async def test_has_circular_reference_category_not_found(self, mock_session):
        """
        Test has_circular_reference when category in chain is not found.

        This covers line 117 in category.py - when category is None, the loop breaks.
        """
        # First call returns a category, second call returns None (category not found)
        category_with_parent = Category(
            id=2,
            name="Level 2",
            slug="level-2",
            parent_id=999,  # Points to non-existent category
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # First execute returns category_with_parent, second returns None
        mock_results = [
            MagicMock(scalar_one_or_none=MagicMock(return_value=category_with_parent)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # This hits line 117
        ]
        mock_session.execute = AsyncMock(side_effect=mock_results)

        repo = CategoryRepository(mock_session)
        result = await repo.has_circular_reference(1, 2)

        # No cycle because the chain ends when category is None
        assert result is False
