"""Category management service."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from knowledge_service.core import NotFoundException, ValidationException
from knowledge_service.models import Category
from knowledge_service.schemas import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service for category management operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize category service with database session."""
        self.db = db

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create new category."""
        # Check for duplicate slug
        stmt = select(Category).where(Category.slug == category_data.slug)
        result = await self.db.execute(stmt)
        existing_category = result.scalar_one_or_none()

        if existing_category:
            msg = "Category with this slug already exists"
            raise ValidationException(msg)

        # Validate parent category if provided
        if category_data.parent_id:
            parent = await self.get_category_by_id(category_data.parent_id)
            # Check for circular reference
            if parent.parent_id:
                # For now, only allow one level of nesting
                msg = "Only one level of nesting is allowed"
                raise ValidationException(msg)

        category = Category(
            name=category_data.name,
            slug=category_data.slug,
            description=category_data.description,
            parent_id=category_data.parent_id,
            order=category_data.order,
            department=category_data.department,
            position=category_data.position,
            level=category_data.level,
            icon=category_data.icon,
            color=category_data.color,
        )

        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)

        return category

    async def get_category_by_id(self, category_id: int) -> Category:
        """Get category by ID."""
        stmt = (
            select(Category)
            .where(Category.id == category_id)
            .options(selectinload(Category.children), selectinload(Category.articles))
        )
        result = await self.db.execute(stmt)
        category = result.scalar_one_or_none()

        if not category:
            msg = "Category"
            raise NotFoundException(msg)

        return category

    async def get_category_by_slug(self, slug: str) -> Category:
        """Get category by slug."""
        stmt = (
            select(Category)
            .where(Category.slug == slug)
            .options(selectinload(Category.children), selectinload(Category.articles))
        )
        result = await self.db.execute(stmt)
        category = result.scalar_one_or_none()

        if not category:
            msg = "Category"
            raise NotFoundException(msg)

        return category

    async def update_category(self, category_id: int, update_data: CategoryUpdate) -> Category:
        """Update category."""
        category = await self.get_category_by_id(category_id)

        # Check for circular reference if updating parent
        if update_data.parent_id is not None:
            if update_data.parent_id == category_id:
                msg = "Category cannot be its own parent"
                raise ValidationException(msg)

            # Check if parent exists
            parent = await self.get_category_by_id(update_data.parent_id)

            # Check for circular reference in hierarchy
            if await self._has_circular_reference(category_id, parent.id):
                msg = "Circular reference detected in category hierarchy"
                raise ValidationException(msg)

        # Update fields
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        await self.db.commit()
        await self.db.refresh(category)

        return category

    async def delete_category(self, category_id: int) -> None:
        """Delete category."""
        category = await self.get_category_by_id(category_id)

        # Check if category has children
        if category.children:
            msg = "Cannot delete category with child categories"
            raise ValidationException(msg)

        # Check if category has articles
        if category.articles:
            msg = "Cannot delete category with articles. Move or delete articles first."
            raise ValidationException(msg)

        await self.db.delete(category)
        await self.db.commit()

    async def get_categories(
        self,
        skip: int = 0,
        limit: int = 50,
        parent_id: int | None = None,
        department: str | None = None,
        *,
        include_tree: bool = False,
    ) -> tuple[list[Category], int]:
        """Get paginated list of categories with filters."""
        if include_tree:
            # Get tree structure
            return await self._get_category_tree(department)

        stmt = select(Category)
        count_stmt = select(func.count(Category.id))

        if parent_id is not None:
            stmt = stmt.where(Category.parent_id == parent_id)
            count_stmt = count_stmt.where(Category.parent_id == parent_id)
        else:
            stmt = stmt.where(Category.parent_id.is_(None))
            count_stmt = count_stmt.where(Category.parent_id.is_(None))

        if department:
            stmt = stmt.where(Category.department == department)
            count_stmt = count_stmt.where(Category.department == department)

        result = await self.db.execute(count_stmt)
        total = result.scalar_one()

        stmt = stmt.order_by(Category.order, Category.name).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        categories = list(result.scalars().all())

        return categories, total

    async def get_department_categories(self, department: str) -> list[Category]:
        """Get all categories for a specific department."""
        stmt = (
            select(Category)
            .where(Category.department == department)
            .order_by(Category.parent_id, Category.order, Category.name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_category_tree(self, department: str | None = None) -> tuple[list[dict[str, Any]], int]:
        """Get category tree structure and total count."""
        # Get all categories with articles
        stmt = select(Category).options(selectinload(Category.articles))

        if department:
            stmt = stmt.where(Category.department == department)

        stmt = stmt.order_by(Category.parent_id, Category.order, Category.name)
        result = await self.db.execute(stmt)
        all_categories = list(result.scalars().all())

        # Build tree
        category_map = {cat.id: cat for cat in all_categories}
        tree = []

        for category in all_categories:
            if category.parent_id is None:
                # Root category
                category_dict = await self._category_to_dict(category, category_map)
                tree.append(category_dict)

        return tree, len(all_categories)

    async def _category_to_dict(self, category: Category, category_map: dict[int, Category]) -> dict[str, Any]:
        """Convert category to dictionary with children."""
        # Get parent name
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
            "department": category.department,
            "position": category.position,
            "level": category.level,
            "icon": category.icon,
            "color": category.color,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "articles_count": len(category.articles),
            "children": [],
        }

        # Find and add children
        for cat in category_map.values():
            if cat.parent_id == category.id:
                child_dict = await self._category_to_dict(cat, category_map)
                category_dict["children"].append(child_dict)

        return category_dict

    async def _has_circular_reference(self, category_id: int, potential_parent_id: int) -> bool:
        """Check if setting parent would create a circular reference."""
        if category_id == potential_parent_id:
            return True

        # Traverse up the hierarchy
        current_id = potential_parent_id
        while current_id is not None:
            stmt = select(Category).where(Category.id == current_id)
            result = await self.db.execute(stmt)
            category = result.scalar_one_or_none()

            if not category:
                break

            if category.parent_id == category_id:
                return True

            current_id = category.parent_id

        return False

    async def _get_category_tree(self, department: str | None = None) -> tuple[list[Category], int]:
        """Get category tree structure (legacy method)."""
        tree, total = await self.get_category_tree(department)
        # Flatten tree for compatibility
        flattened = self._flatten_tree(tree)
        return flattened, total

    def _flatten_tree(self, tree: list[dict], depth: int = 0) -> list:
        """Flatten category tree for list display."""
        flattened = []
        for node in tree:
            # Add current node with depth indicator
            node_copy = node.copy()
            node_copy["depth"] = depth
            flattened.append(node_copy)

            # Add children recursively
            if node["children"]:
                children = self._flatten_tree(node["children"], depth + 1)
                flattened.extend(children)

        return flattened
