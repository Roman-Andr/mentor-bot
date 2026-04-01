"""Dialogue scenario management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from knowledge_service.api import AdminUser, DialogueServiceDep, HRUser
from knowledge_service.core import NotFoundException
from knowledge_service.schemas import (
    DialogueScenarioCreate,
    DialogueScenarioListResponse,
    DialogueScenarioResponse,
    DialogueScenarioUpdate,
    DialogueStepCreate,
    DialogueStepReorderRequest,
    DialogueStepResponse,
    DialogueStepUpdate,
    MessageResponse,
)

router = APIRouter()


@router.get("/")
@router.get("")
async def get_scenarios(
    dialogue_service: DialogueServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    category: Annotated[str | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
) -> DialogueScenarioListResponse:
    """Get paginated list of dialogue scenarios."""
    scenarios, total = await dialogue_service.find_scenarios(
        skip=skip,
        limit=limit,
        category=category,
        is_active=is_active,
        search=search,
    )

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return DialogueScenarioListResponse(
        total=total,
        scenarios=[DialogueScenarioResponse.model_validate(s) for s in scenarios],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.post("/")
@router.post("")
async def create_scenario(
    scenario_data: DialogueScenarioCreate,
    dialogue_service: DialogueServiceDep,
    _current_user: HRUser,
) -> DialogueScenarioResponse:
    """Create new dialogue scenario (HR/admin only)."""
    scenario = await dialogue_service.create_scenario(scenario_data)
    return DialogueScenarioResponse.model_validate(scenario)


@router.get("/active")
async def get_active_scenarios(
    dialogue_service: DialogueServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> DialogueScenarioListResponse:
    """Get active scenarios for bot menu."""
    scenarios, total = await dialogue_service.get_active_scenarios(skip=skip, limit=limit)

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return DialogueScenarioListResponse(
        total=total,
        scenarios=[DialogueScenarioResponse.model_validate(s) for s in scenarios],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.get("/category/{category}")
async def get_scenarios_by_category(
    category: str,
    dialogue_service: DialogueServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> DialogueScenarioListResponse:
    """Get scenarios by category."""
    scenarios, total = await dialogue_service.get_scenarios_by_category(category, skip=skip, limit=limit)

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return DialogueScenarioListResponse(
        total=total,
        scenarios=[DialogueScenarioResponse.model_validate(s) for s in scenarios],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.get("/{scenario_id}")
async def get_scenario(
    scenario_id: int,
    dialogue_service: DialogueServiceDep,
) -> DialogueScenarioResponse:
    """Get dialogue scenario by ID."""
    try:
        scenario = await dialogue_service.get_scenario_by_id(scenario_id)
        return DialogueScenarioResponse.model_validate(scenario)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.put("/{scenario_id}")
async def update_scenario(
    scenario_id: int,
    scenario_data: DialogueScenarioUpdate,
    dialogue_service: DialogueServiceDep,
    _current_user: HRUser,
) -> DialogueScenarioResponse:
    """Update dialogue scenario (HR/admin only)."""
    try:
        scenario = await dialogue_service.update_scenario(scenario_id, scenario_data)
        return DialogueScenarioResponse.model_validate(scenario)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: int,
    dialogue_service: DialogueServiceDep,
    _current_user: AdminUser,
) -> MessageResponse:
    """Delete dialogue scenario (admin only)."""
    try:
        await dialogue_service.delete_scenario(scenario_id)
        return MessageResponse(message="Dialogue scenario deleted successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/{scenario_id}/steps/first")
async def get_first_step(
    scenario_id: int,
    dialogue_service: DialogueServiceDep,
) -> DialogueStepResponse:
    """Get first step of a scenario."""
    step = await dialogue_service.get_first_step(scenario_id)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No steps found in scenario",
        )
    return DialogueStepResponse.model_validate(step)


@router.post("/{scenario_id}/steps")
async def add_step(
    scenario_id: int,
    step_data: DialogueStepCreate,
    dialogue_service: DialogueServiceDep,
    _current_user: HRUser,
) -> DialogueStepResponse:
    """Add a step to a scenario (HR/admin only)."""
    try:
        step = await dialogue_service.add_step(scenario_id, step_data)
        return DialogueStepResponse.model_validate(step)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.put("/steps/{step_id}")
async def update_step(
    step_id: int,
    step_data: DialogueStepUpdate,
    dialogue_service: DialogueServiceDep,
    _current_user: HRUser,
) -> DialogueStepResponse:
    """Update a dialogue step (HR/admin only)."""
    try:
        step = await dialogue_service.update_step(step_id, step_data)
        return DialogueStepResponse.model_validate(step)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.delete("/steps/{step_id}")
async def delete_step(
    step_id: int,
    dialogue_service: DialogueServiceDep,
    _current_user: HRUser,
) -> MessageResponse:
    """Delete a dialogue step (HR/admin only)."""
    try:
        await dialogue_service.delete_step(step_id)
        return MessageResponse(message="Dialogue step deleted successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{scenario_id}/reorder")
async def reorder_steps(
    scenario_id: int,
    reorder_data: DialogueStepReorderRequest,
    dialogue_service: DialogueServiceDep,
    _current_user: HRUser,
) -> MessageResponse:
    """Reorder steps in a scenario (HR/admin only)."""
    try:
        await dialogue_service.reorder_steps(scenario_id, reorder_data.step_ids)
        return MessageResponse(message="Steps reordered successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
