"""Tests for Category repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.core import EmployeeLevel
from knowledge_service.models import Category
from knowledge_service.repositories.implementations.category import CategoryRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TestCategoryRepository:
    """Test Category repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def sample_category(self):
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
            level=EmployeeLevel.JUNIOR,
            icon="folder",
            color="#000000",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    @pytest.fixture
    def sample_child_category(self):
        """Create a sample child category."""
        return Category(
            id=2,
            name="Child Category",
            slug="child-category",
            description="Child description",
            parent_id=1,
            order=1,
            department_id=1,
            position="Developer",
            level=EmployeeLevel.JUNIOR,
            icon="folder",
            color="#111111",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def test_get_by_slug(self, mock_session, sample_category):
        """Test getting category by slug."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_category
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result = await repo.get_by_slug("test-category")

        assert result == sample_category

    async def test_get_by_id_with_relations(self, mock_session, sample_category):
        """Test getting category by ID with relations."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_category
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result = await repo.get_by_id_with_relations(1)

        assert result == sample_category

    async def test_slug_exists_true(self, mock_session, sample_category):
        """Test checking if slug exists - exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_category
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result = await repo.slug_exists("test-category")

        assert result is True

    async def test_slug_exists_false(self, mock_session):
        """Test checking if slug exists - not exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result = await repo.slug_exists("nonexistent")

        assert result is False

    async def test_find_categories_with_parent_id(self, mock_session, sample_category):
        """Test finding categories with parent_id filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result, total = await repo.find_categories(parent_id=1)

        assert len(result) == 1
        assert total == 1

    async def test_find_categories_root_only(self, mock_session, sample_category):
        """Test finding root categories only."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result, _total = await repo.find_categories()

        assert len(result) == 1

    async def test_find_categories_with_department(self, mock_session, sample_category):
        """Test finding categories with department filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result, _total = await repo.find_categories(department_id=1)

        assert len(result) == 1

    async def test_find_categories_with_search(self, mock_session, sample_category):
        """Test finding categories with search."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result, _total = await repo.find_categories(search="test")

        assert len(result) == 1

    async def test_find_by_department(self, mock_session, sample_category, sample_child_category):
        """Test finding all categories for a department."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category, sample_child_category]
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result = await repo.find_by_department(1)

        assert len(result) == 2

    async def test_find_all_for_tree(self, mock_session, sample_category):
        """Test finding all categories for tree structure."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result = await repo.find_all_for_tree()

        assert len(result) == 1

    async def test_find_all_for_tree_with_department(self, mock_session, sample_category):
        """Test finding categories for tree with department filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result = await repo.find_all_for_tree(department_id=1)

        assert len(result) == 1

    async def test_has_circular_reference_same_id(self, mock_session):
        """Test circular reference when category_id equals potential_parent_id."""
        repo = CategoryRepository(mock_session)
        result = await repo.has_circular_reference(1, 1)

        assert result is True

    async def test_has_circular_reference_parent_is_child(self, mock_session):
        """Test circular reference when parent is a child of category."""
        parent = Category(
            id=2,
            name="Parent",
            slug="parent",
            parent_id=1,  # Points back to category 1
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = parent
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result = await repo.has_circular_reference(1, 2)

        assert result is True

    async def test_has_circular_reference_no_cycle(self, mock_session):
        """Test no circular reference."""
        parent = Category(
            id=2,
            name="Parent",
            slug="parent",
            parent_id=None,  # No parent
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = parent
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result = await repo.has_circular_reference(1, 2)

        assert result is False

    async def test_has_circular_reference_chain(self, mock_session):
        """Test circular reference through a chain."""
        # Category 3's parent is 2, 2's parent is 1
        # So setting 3 as parent of 1 would create a cycle
        level2 = Category(id=2, name="Level 2", slug="level-2", parent_id=1)
        level3 = Category(id=3, name="Level 3", slug="level-3", parent_id=2)

        mock_results = [
            MagicMock(scalar_one_or_none=MagicMock(return_value=level3)),  # First: potential_parent_id=3
            MagicMock(scalar_one_or_none=MagicMock(return_value=level2)),  # Second: parent of 3 is 2
            MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # Third: no more parents
        ]

        mock_session.execute = AsyncMock(side_effect=mock_results)

        repo = CategoryRepository(mock_session)
        result = await repo.has_circular_reference(1, 3)

        assert result is True

    async def test_find_categories_desc_sort_order(self, mock_session, sample_category):
        """Test finding categories with descending sort order."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result, total = await repo.find_categories(sort_by="name", sort_order="desc")

        assert len(result) == 1
        assert total == 1

    async def test_find_categories_sort_by_articles_count(self, mock_session, sample_category):
        """Test finding categories sorted by articles count."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = CategoryRepository(mock_session)
        result, total = await repo.find_categories(sort_by="articlesCount", sort_order="asc")

        assert len(result) == 1
        assert total == 1
