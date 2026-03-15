"""Template repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

from checklists_service.core.enums import TemplateStatus
from checklists_service.repositories.interfaces.base import BaseRepository

if TYPE_CHECKING:
    from checklists_service.models import TaskTemplate, Template


class ITemplateRepository(BaseRepository["Template", int]):
    """Template repository interface with template-specific queries."""

    @abstractmethod
    async def find_templates(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        department: str | None = None,
        status: TemplateStatus | None = None,
        is_default: bool | None = None,
    ) -> tuple[Sequence["Template"], int]:
        """Find templates with filtering and return results with total count."""

    @abstractmethod
    async def get_by_name_and_department(self, name: str, department: str | None) -> "Template | None":
        """Get template by name and department."""

    @abstractmethod
    async def clear_other_defaults(self, department: str | None, exclude_id: int) -> None:
        """Clear is_default flag on other templates in the same department."""

    @abstractmethod
    async def count_tasks(self, template_id: int) -> int:
        """Count task templates for a template."""

    @abstractmethod
    async def has_checklists(self, template_id: int) -> bool:
        """Check if template has associated checklists."""

    @abstractmethod
    async def get_department_stats(self, user_id: int | None = None) -> dict[str, int]:
        """Get checklist count grouped by department."""


class ITaskTemplateRepository(BaseRepository["TaskTemplate", int]):
    """Task template repository interface."""

    @abstractmethod
    async def find_by_template(self, template_id: int) -> Sequence["TaskTemplate"]:
        """Find task templates for a template, ordered by order field."""

    @abstractmethod
    async def find_existing_ids(self, template_id: int, ids: list[int]) -> set[int]:
        """Find which of the given IDs exist for a template."""

    @abstractmethod
    async def clone_tasks(self, source_template_id: int, target_template_id: int) -> None:
        """Clone all task templates from source to target template."""
