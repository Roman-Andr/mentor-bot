"""Audit endpoints for knowledge service."""

import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from knowledge_service.api.deps import CurrentUser, UnitOfWorkDep
from knowledge_service.core import UserRole

logger = logging.getLogger(__name__)

router = APIRouter()


# Schemas for audit responses
class ArticleChangeEntry(BaseModel):
    """Article change history entry schema."""

    model_config = {"from_attributes": True}

    id: int
    article_id: int
    user_id: int
    action: str
    old_title: str | None
    new_title: str | None
    old_content: str | None
    new_content: str | None
    changed_at: datetime
    changed_by: int | None
    change_summary: str | None


class ArticleViewEntry(BaseModel):
    """Article view history entry schema."""

    model_config = {"from_attributes": True}

    id: int
    article_id: int
    user_id: int | None
    viewed_at: datetime
    department_id: int | None
    position: str | None
    level: str | None
    referrer: str | None
    session_id: str | None


class CategoryChangeEntry(BaseModel):
    """Category change history entry schema."""

    model_config = {"from_attributes": True}

    id: int
    category_id: int
    user_id: int
    action: str
    old_name: str | None
    new_name: str | None
    changed_at: datetime
    changed_by: int | None


class DialogueScenarioChangeEntry(BaseModel):
    """Dialogue scenario change history entry schema."""

    model_config = {"from_attributes": True}

    id: int
    scenario_id: int
    user_id: int
    action: str
    old_name: str | None
    new_name: str | None
    changed_at: datetime
    changed_by: int | None
    change_summary: str | None


class AuditResponse(BaseModel):
    """Generic audit response with pagination."""

    items: Sequence[BaseModel]
    total: int


def require_hr_or_admin(current_user: CurrentUser) -> None:
    """Require HR or Admin role for audit access."""
    if current_user.role not in (UserRole.HR, UserRole.ADMIN):
        raise PermissionError("Access denied: HR or Admin role required")


@router.get("/article-change-history", response_model=AuditResponse)
async def get_article_change_history(
    current_user: Annotated[CurrentUser, Depends()],
    uow: UnitOfWorkDep,
    article_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get article change history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if article_id:
        items = await uow.article_change_history.get_by_article_id(
            article_id=article_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.article_change_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[ArticleChangeEntry.model_validate(item) for item in items],
        total=total,
    )


@router.get("/article-view-history", response_model=AuditResponse)
async def get_article_view_history(
    current_user: Annotated[CurrentUser, Depends()],
    uow: UnitOfWorkDep,
    article_id: Annotated[int | None, Query()] = None,
    user_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get article view history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if article_id:
        items = await uow.article_view_history.get_by_article_id(
            article_id=article_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    elif user_id:
        items = await uow.article_view_history.get_by_user_id(user_id=user_id, from_date=from_date, to_date=to_date)
        total = len(items)
    else:
        items, total = await uow.article_view_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[ArticleViewEntry.model_validate(item) for item in items],
        total=total,
    )


@router.get("/category-change-history", response_model=AuditResponse)
async def get_category_change_history(
    current_user: Annotated[CurrentUser, Depends()],
    uow: UnitOfWorkDep,
    category_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get category change history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if category_id:
        items = await uow.category_change_history.get_by_category_id(
            category_id=category_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.category_change_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[CategoryChangeEntry.model_validate(item) for item in items],
        total=total,
    )


@router.get("/dialogue-scenario-change-history", response_model=AuditResponse)
async def get_dialogue_scenario_change_history(
    current_user: Annotated[CurrentUser, Depends()],
    uow: UnitOfWorkDep,
    scenario_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get dialogue scenario change history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if scenario_id:
        items = await uow.dialogue_scenario_change_history.get_by_scenario_id(
            scenario_id=scenario_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.dialogue_scenario_change_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[DialogueScenarioChangeEntry.model_validate(item) for item in items],
        total=total,
    )
