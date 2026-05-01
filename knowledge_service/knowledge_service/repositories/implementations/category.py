"""SQLAlchemy implementation of Category repository."""

from collections.abc import Sequence
from typing import cast

from sqlalchemy import Column, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from knowledge_service.models import Category
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.category import ICategoryRepository


class CategoryRepository(SqlAlchemyBaseRepository[Category, int], ICategoryRepository):
    """SQLAlchemy implementation of Category repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize category repository."""
        super().__init__(session, Category)

    async def get_by_slug(self, slug: str) -> Category | None:
        """Retrieve category by slug with children and articles."""
        stmt = (
            select(Category)
            .where(Category.slug == slug)
            .options(selectinload(Category.children), selectinload(Category.articles))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(self, entity_id: int) -> Category | None:
        """Retrieve category by ID with children and articles."""
        stmt = (
            select(Category)
            .where(Category.id == entity_id)
            .options(selectinload(Category.children), selectinload(Category.articles))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def slug_exists(self, slug: str) -> bool:
        """Check if a category with the given slug exists."""
        stmt = select(Category).where(Category.slug == slug)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _get_sort_column(self, sort_by: str | None) -> Column:
        """Get SQLAlchemy column for sorting."""
        column_map = {
            "name": Category.name,
            "slug": Category.slug,
            "order": Category.order,
            "createdAt": Category.created_at,
            "updatedAt": Category.updated_at,
            "department": Category.department_id,
            "position": Category.position,
            "level": Category.level,
        }
        return column_map.get(sort_by, Category.order)

    async def find_categories(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        parent_id: int | None = None,
        department_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[Sequence[Category], int]:
        """Find categories with filters and return total count."""
        stmt = select(Category).options(selectinload(Category.articles), selectinload(Category.children))
        count_stmt = select(func.count(Category.id))

        if parent_id is not None:
            stmt = stmt.where(Category.parent_id == parent_id)
            count_stmt = count_stmt.where(Category.parent_id == parent_id)
        else:
            stmt = stmt.where(Category.parent_id.is_(None))
            count_stmt = count_stmt.where(Category.parent_id.is_(None))

        if department_id:
            stmt = stmt.where(Category.department_id == department_id)
            count_stmt = count_stmt.where(Category.department_id == department_id)

        if search:
            search_filter = or_(
                Category.name.ilike(f"%{search}%"),
                Category.description.ilike(f"%{search}%"),
                Category.slug.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        # Apply sorting
        if sort_by == "articlesCount":
            # Sort by articles count using subquery
            from knowledge_service.models import Article
            articles_count_subquery = (
                select(func.count(Article.id))
                .where(Article.category_id == Category.id)
                .correlate(Category)
                .scalar_subquery()
            )
            stmt = stmt.order_by(
                articles_count_subquery.asc() if sort_order.lower() == "asc" else articles_count_subquery.desc()
            )
        else:
            sort_column = self._get_sort_column(sort_by)
            stmt = stmt.order_by(sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        categories = result.scalars().all()

        # Add computed attributes for response
        for category in categories:
            # These are computed attributes that will be used by Pydantic
            category.articles_count = len(category.articles) if hasattr(category, "articles") else 0
            category.children_count = len(category.children) if hasattr(category, "children") else 0

        return categories, total

    async def find_by_department(self, department_id: int) -> Sequence[Category]:
        """Find all categories for a department."""
        stmt = (
            select(Category)
            .where(Category.department_id == department_id)
            .order_by(Category.parent_id, Category.order, Category.name)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_all_for_tree(self, department_id: int | None = None) -> Sequence[Category]:
        """Find all categories for building a tree structure."""
        stmt = select(Category).options(selectinload(Category.articles))
        if department_id:
            stmt = stmt.where(Category.department_id == department_id)
        stmt = stmt.order_by(Category.parent_id, Category.order, Category.name)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def has_circular_reference(self, category_id: int, potential_parent_id: int) -> bool:
        """Check if setting parent would create a circular reference."""
        if category_id == potential_parent_id:
            return True

        current_id = potential_parent_id
        while current_id is not None:
            stmt = select(Category).where(Category.id == current_id)
            result = await self._session.execute(stmt)
            category = result.scalar_one_or_none()
            if not category:
                break
            if category.parent_id == category_id:
                return True
            current_id = category.parent_id

        return False
