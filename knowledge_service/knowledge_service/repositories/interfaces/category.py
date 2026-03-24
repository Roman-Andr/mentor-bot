"""Category repository interface."""

from abc import abstractmethod
from collections.abc import Sequence

from knowledge_service.models import Category
from knowledge_service.repositories.interfaces.base import BaseRepository


class ICategoryRepository(BaseRepository["Category", int]):
    """Category repository interface with specific queries."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Category | None:
        """Get category by slug with eager-loaded children and articles."""

    @abstractmethod
    async def get_by_id_with_relations(self, entity_id: int) -> Category | None:
        """Get category by ID with eager-loaded children and articles."""

    @abstractmethod
    async def slug_exists(self, slug: str) -> bool:
        """Check if a category with the given slug exists."""

    @abstractmethod
    async def find_categories(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        parent_id: int | None = None,
        department_id: int | None = None,
    ) -> tuple[Sequence[Category], int]:
        """Find categories with filtering, return results + total count."""

    @abstractmethod
    async def find_by_department(self, department_id: int) -> Sequence[Category]:
        """Get all categories for a specific department."""

    @abstractmethod
    async def find_all_for_tree(self, department_id: int | None = None) -> Sequence[Category]:
        """Get all categories with articles loaded, for tree building."""

    @abstractmethod
    async def has_circular_reference(self, category_id: int, potential_parent_id: int) -> bool:
        """Check if setting parent would create a circular reference."""
