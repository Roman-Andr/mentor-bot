"""Category management service with repository pattern."""

from typing import Any

from knowledge_service.core import NotFoundException, ValidationException
from knowledge_service.models import Category
from knowledge_service.repositories import IUnitOfWork
from knowledge_service.schemas import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service for category management operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize category service with Unit of Work."""
        self._uow = uow

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create new category."""
        if await self._uow.categories.slug_exists(category_data.slug):
            msg = "Category with this slug already exists"
            raise ValidationException(msg)

        if category_data.parent_id:
            parent = await self.get_category_by_id(category_data.parent_id)
            if parent.parent_id:
                msg = "Only one level of nesting is allowed"
                raise ValidationException(msg)

        category = Category(
            name=category_data.name,
            slug=category_data.slug,
            description=category_data.description,
            parent_id=category_data.parent_id,
            order=category_data.order,
            department_id=category_data.department_id,
            position=category_data.position,
            level=category_data.level,
            icon=category_data.icon,
            color=category_data.color,
        )

        created = await self._uow.categories.create(category)
        await self._uow.commit()
        return created

    async def get_category_by_id(self, category_id: int) -> Category:
        """Get category by ID."""
        category = await self._uow.categories.get_by_id_with_relations(category_id)
        if not category:
            msg = "Category"
            raise NotFoundException(msg)
        return category

    async def get_category_by_slug(self, slug: str) -> Category:
        """Get category by slug."""
        category = await self._uow.categories.get_by_slug(slug)
        if not category:
            msg = "Category"
            raise NotFoundException(msg)
        return category

    async def update_category(self, category_id: int, update_data: CategoryUpdate) -> Category:
        """Update category."""
        category = await self.get_category_by_id(category_id)

        if update_data.parent_id is not None:
            if update_data.parent_id == category_id:
                msg = "Category cannot be its own parent"
                raise ValidationException(msg)

            await self.get_category_by_id(update_data.parent_id)

            if await self._uow.categories.has_circular_reference(category_id, update_data.parent_id):
                msg = "Circular reference detected in category hierarchy"
                raise ValidationException(msg)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        updated = await self._uow.categories.update(category)
        await self._uow.commit()
        return updated

    async def delete_category(self, category_id: int) -> None:
        """Delete category."""
        category = await self.get_category_by_id(category_id)

        if category.children:
            msg = "Cannot delete category with child categories"
            raise ValidationException(msg)

        if category.articles:
            msg = "Cannot delete category with articles. Move or delete articles first."
            raise ValidationException(msg)

        await self._uow.categories.delete(category_id)
        await self._uow.commit()

    async def get_categories(
        self,
        skip: int = 0,
        limit: int = 50,
        parent_id: int | None = None,
        department_id: int | None = None,
        *,
        include_tree: bool = False,
    ) -> tuple[list[Category], int]:
        """Get paginated list of categories with filters."""
        if include_tree:
            return await self._get_category_tree(department_id)

        items, total = await self._uow.categories.find_categories(
            skip=skip,
            limit=limit,
            parent_id=parent_id,
            department_id=department_id,
        )
        return list(items), total

    async def get_department_categories(self, department_id: int) -> list[Category]:
        """Get all categories for a specific department."""
        items = await self._uow.categories.find_by_department(department_id)
        return list(items)

    async def get_category_tree(self, department_id: int | None = None) -> tuple[list[dict[str, Any]], int]:
        """Get category tree structure and total count."""
        all_categories = await self._uow.categories.find_all_for_tree(department_id)

        category_map = {cat.id: cat for cat in all_categories}
        tree = []

        for category in all_categories:
            if category.parent_id is None:
                category_dict = await self._category_to_dict(category, category_map)
                tree.append(category_dict)

        return tree, len(all_categories)

    async def _category_to_dict(self, category: Category, category_map: dict[int, Category]) -> dict[str, Any]:
        """Convert category to dictionary with children."""
        parent_name = None
        if category.parent_id and category.parent_id in category_map:
            parent_name = category_map[category.parent_id].name

        category_dict = {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "parent_id": category.parent_id,
            "parent_name": parent_name,
            "order": category.order,
            "department_id": category.department_id,
            "position": category.position,
            "level": category.level,
            "icon": category.icon,
            "color": category.color,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "articles_count": len(category.articles),
            "children": [],
        }

        for cat in category_map.values():
            if cat.parent_id == category.id:
                child_dict = await self._category_to_dict(cat, category_map)
                category_dict["children"].append(child_dict)

        return category_dict

    async def _get_category_tree(self, department_id: int | None = None) -> tuple[list[Category], int]:
        """Get category tree structure (legacy method)."""
        tree, total = await self.get_category_tree(department_id)
        flattened = self._flatten_tree(tree)
        return flattened, total

    def _flatten_tree(self, tree: list[dict], depth: int = 0) -> list:
        """Flatten category tree for list display."""
        flattened = []
        for node in tree:
            node_copy = node.copy()
            node_copy["depth"] = depth
            flattened.append(node_copy)

            if node["children"]:
                children = self._flatten_tree(node["children"], depth + 1)
                flattened.extend(children)

        return flattened
