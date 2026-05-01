"""Tests for category service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.core import NotFoundException, ValidationException
from knowledge_service.models import Article, Category
from knowledge_service.schemas import CategoryCreate, CategoryUpdate
from knowledge_service.services.category import CategoryService


@pytest.fixture
def mock_uow():
    """Create a mock Unit of Work."""
    uow = MagicMock()
    uow.categories = AsyncMock()
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def sample_category():
    """Create a sample category for testing."""
    cat = Category(
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
    cat.children = []
    cat.articles = []
    return cat


@pytest.fixture
def sample_child_category(sample_category):
    """Create a sample child category for testing."""
    child = Category(
        id=2,
        name="Child Category",
        slug="child-category",
        description="Child description",
        parent_id=1,
        order=1,
        department_id=1,
        position="Developer",
        level="JUNIOR",
        icon="folder-child",
        color="#111111",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    child.children = []
    child.articles = []
    return child


@pytest.fixture
def sample_parent_category():
    """Create a sample parent category with children."""
    cat = Category(
        id=3,
        name="Parent Category",
        slug="parent-category",
        description="Parent description",
        parent_id=None,
        order=0,
        department_id=1,
        position="Developer",
        level="JUNIOR",
        icon="folder",
        color="#222222",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    cat.children = []
    cat.articles = []
    return cat


class TestCreateCategory:
    """Tests for category creation."""

    async def test_create_category_basic(self, mock_uow, sample_category):
        """Test basic category creation."""
        mock_uow.categories.slug_exists.return_value = False
        mock_uow.categories.create.return_value = sample_category

        service = CategoryService(mock_uow)
        category_data = CategoryCreate(
            name="Test Category",
            slug="test-category",
            description="Test description",
        )

        result = await service.create_category(category_data)

        assert result == sample_category
        mock_uow.categories.create.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_create_category_slug_exists(self, mock_uow):
        """Test category creation with existing slug."""
        mock_uow.categories.slug_exists.return_value = True

        service = CategoryService(mock_uow)
        category_data = CategoryCreate(
            name="Test Category",
            slug="existing-slug",
            description="Test description",
        )

        with pytest.raises(ValidationException, match="already exists"):
            await service.create_category(category_data)

    async def test_create_category_with_parent(self, mock_uow, sample_category, sample_child_category):
        """Test category creation with valid parent."""
        mock_uow.categories.slug_exists.return_value = False
        mock_uow.categories.get_by_id_with_relations.return_value = sample_category
        mock_uow.categories.create.return_value = sample_child_category

        service = CategoryService(mock_uow)
        category_data = CategoryCreate(
            name="Child Category",
            slug="child-category",
            description="Child description",
            parent_id=1,
        )

        result = await service.create_category(category_data)

        assert result == sample_child_category

    async def test_create_category_nested_too_deep(self, mock_uow, sample_child_category):
        """Test category creation with parent that already has a parent (too deep nesting)."""
        mock_uow.categories.slug_exists.return_value = False
        mock_uow.categories.get_by_id_with_relations.return_value = sample_child_category

        service = CategoryService(mock_uow)
        category_data = CategoryCreate(
            name="Grandchild Category",
            slug="grandchild-category",
            description="Grandchild description",
            parent_id=2,
        )

        with pytest.raises(ValidationException, match="one level of nesting"):
            await service.create_category(category_data)


class TestGetCategory:
    """Tests for getting categories."""

    async def test_get_category_by_id_success(self, mock_uow, sample_category):
        """Test getting category by ID successfully."""
        mock_uow.categories.get_by_id_with_relations.return_value = sample_category

        service = CategoryService(mock_uow)
        result = await service.get_category_by_id(1)

        assert result == sample_category
        mock_uow.categories.get_by_id_with_relations.assert_called_once_with(1)

    async def test_get_category_by_id_not_found(self, mock_uow):
        """Test getting non-existent category by ID."""
        mock_uow.categories.get_by_id_with_relations.return_value = None

        service = CategoryService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.get_category_by_id(999)

    async def test_get_category_by_slug_success(self, mock_uow, sample_category):
        """Test getting category by slug successfully."""
        mock_uow.categories.get_by_slug.return_value = sample_category

        service = CategoryService(mock_uow)
        result = await service.get_category_by_slug("test-category")

        assert result == sample_category
        mock_uow.categories.get_by_slug.assert_called_once_with("test-category")

    async def test_get_category_by_slug_not_found(self, mock_uow):
        """Test getting non-existent category by slug."""
        mock_uow.categories.get_by_slug.return_value = None

        service = CategoryService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.get_category_by_slug("non-existent")

    async def test_get_categories(self, mock_uow, sample_category, sample_child_category):
        """Test getting paginated categories."""
        mock_uow.categories.find_categories.return_value = ([sample_category, sample_child_category], 2)

        service = CategoryService(mock_uow)
        result, total = await service.get_categories(skip=0, limit=10)

        assert len(result) == 2
        assert total == 2

    async def test_get_categories_with_filters(self, mock_uow, sample_category):
        """Test getting categories with filters."""
        mock_uow.categories.find_categories.return_value = ([sample_category], 1)

        service = CategoryService(mock_uow)
        result, total = await service.get_categories(
            skip=0,
            limit=10,
            parent_id=None,
            department_id=1,
            search="test",
        )

        assert len(result) == 1
        assert total == 1

    async def test_get_categories_include_tree(self, mock_uow, sample_category, sample_child_category):
        """Test getting categories with tree structure."""
        mock_uow.categories.find_all_for_tree.return_value = [sample_category, sample_child_category]

        service = CategoryService(mock_uow)
        result, total = await service.get_categories(include_tree=True)

        assert total == 2
        assert len(result) == 2


class TestUpdateCategory:
    """Tests for updating categories."""

    async def test_update_category_basic(self, mock_uow, sample_category):
        """Test basic category update."""
        mock_uow.categories.get_by_id_with_relations.return_value = sample_category
        mock_uow.categories.update.return_value = sample_category

        service = CategoryService(mock_uow)
        update_data = CategoryUpdate(name="Updated Category")

        result = await service.update_category(1, update_data)

        assert result.name == "Updated Category"
        mock_uow.commit.assert_called_once()

    async def test_update_category_circular_reference(self, mock_uow, sample_parent_category, sample_child_category):
        """Test category update with circular reference."""
        sample_parent_category.children = [sample_child_category]
        sample_child_category.parent_id = 3
        sample_child_category.children = []

        mock_uow.categories.get_by_id_with_relations.side_effect = [
            sample_child_category,
            sample_parent_category,
        ]
        mock_uow.categories.has_circular_reference.return_value = True

        service = CategoryService(mock_uow)
        update_data = CategoryUpdate(parent_id=2)

        with pytest.raises(ValidationException, match="Circular reference"):
            await service.update_category(1, update_data)

    async def test_update_category_self_parent(self, mock_uow, sample_category):
        """Test category update with self as parent."""
        mock_uow.categories.get_by_id_with_relations.return_value = sample_category

        service = CategoryService(mock_uow)
        update_data = CategoryUpdate(parent_id=1)

        with pytest.raises(ValidationException, match="own parent"):
            await service.update_category(1, update_data)

    async def test_update_category_valid_parent_change(self, mock_uow, sample_category, sample_parent_category):
        """Test category update with valid parent change."""
        sample_category.parent_id = None
        mock_uow.categories.get_by_id_with_relations.side_effect = [
            sample_category,
            sample_parent_category,
        ]
        mock_uow.categories.has_circular_reference.return_value = False
        mock_uow.categories.update.return_value = sample_category

        service = CategoryService(mock_uow)
        update_data = CategoryUpdate(parent_id=3)

        await service.update_category(1, update_data)

        assert sample_category.parent_id == 3
        mock_uow.commit.assert_called_once()


class TestDeleteCategory:
    """Tests for deleting categories."""

    async def test_delete_category(self, mock_uow, sample_category):
        """Test category deletion."""
        mock_uow.categories.get_by_id_with_relations.return_value = sample_category
        mock_uow.categories.delete.return_value = None

        service = CategoryService(mock_uow)
        await service.delete_category(1)

        mock_uow.categories.delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()

    async def test_delete_category_with_children(self, mock_uow, sample_parent_category, sample_child_category):
        """Test deleting category with children."""
        sample_parent_category.children = [sample_child_category]

        mock_uow.categories.get_by_id_with_relations.return_value = sample_parent_category

        service = CategoryService(mock_uow)

        with pytest.raises(ValidationException, match="child categories"):
            await service.delete_category(3)

    async def test_delete_category_with_articles(self, mock_uow, sample_category):
        """Test deleting category with articles."""
        article = Article(
            id=1,
            title="Test Article",
            slug="test-article",
            content="Content",
            excerpt="Excerpt",
            category_id=1,
            author_id=1,
            author_name="Author",
            status="published",
            view_count=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        sample_category.articles = [article]

        mock_uow.categories.get_by_id_with_relations.return_value = sample_category

        service = CategoryService(mock_uow)

        with pytest.raises(ValidationException, match="articles"):
            await service.delete_category(1)


class TestDepartmentCategories:
    """Tests for department-specific category operations."""

    async def test_get_department_categories(self, mock_uow, sample_category):
        """Test getting categories for a department."""
        mock_uow.categories.find_by_department.return_value = [sample_category]

        service = CategoryService(mock_uow)
        result = await service.get_department_categories(1)

        assert len(result) == 1
        mock_uow.categories.find_by_department.assert_called_once_with(1)


class TestCategoryTree:
    """Tests for category tree operations."""

    async def test_get_category_tree(self, mock_uow, sample_category, sample_child_category):
        """Test getting category tree."""
        mock_uow.categories.find_all_for_tree.return_value = [sample_category, sample_child_category]

        service = CategoryService(mock_uow)
        tree, total = await service.get_category_tree(department_id=1)

        assert total == 2
        assert len(tree) == 1  # Only root categories
        assert tree[0]["id"] == 1
        assert len(tree[0]["children"]) == 1
        assert tree[0]["children"][0]["id"] == 2

    async def test_get_category_tree_no_department(self, mock_uow, sample_category, sample_child_category):
        """Test getting category tree without department filter."""
        mock_uow.categories.find_all_for_tree.return_value = [sample_category, sample_child_category]

        service = CategoryService(mock_uow)
        tree, total = await service.get_category_tree()

        assert total == 2
        assert len(tree) == 1


class TestPrivateHelpers:
    """Tests for private helper methods."""

    async def test_category_to_dict(self, mock_uow, sample_category):
        """Test _category_to_dict helper."""
        category_map = {1: sample_category}

        service = CategoryService(mock_uow)
        result = await service._category_to_dict(sample_category, category_map)

        assert result["id"] == 1
        assert result["name"] == "Test Category"
        assert result["parent_name"] is None
        assert result["children"] == []

    async def test_category_to_dict_with_parent(self, mock_uow, sample_category, sample_child_category):
        """Test _category_to_dict with parent."""
        category_map = {1: sample_category, 2: sample_child_category}

        service = CategoryService(mock_uow)
        result = await service._category_to_dict(sample_child_category, category_map)

        assert result["id"] == 2
        assert result["parent_id"] == 1
        assert result["parent_name"] == "Test Category"

    async def test_flatten_tree(self, mock_uow):
        """Test _flatten_tree helper."""
        tree = [
            {
                "id": 1,
                "name": "Test Category",
                "children": [
                    {
                        "id": 2,
                        "name": "Child Category",
                        "children": [],
                    }
                ],
            }
        ]

        service = CategoryService(mock_uow)
        result = service._flatten_tree(tree)

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["depth"] == 0
        assert result[1]["id"] == 2
        assert result[1]["depth"] == 1
