"""Escalation request endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger

from escalation_service.api.deps import (
    AdminUser,
    CurrentUser,
    EscalationServiceDep,
    HRUser,
    UOWDep,
)
from escalation_service.core.enums import EscalationStatus, EscalationType
from escalation_service.core.exceptions import NotFoundException
from escalation_service.schemas import (
    EscalationRequestCreate,
    EscalationRequestListResponse,
    EscalationRequestResponse,
    EscalationRequestUpdate,
    MessageResponse,
)

router = APIRouter()


@router.get("/assigned-to-me")
async def get_my_assigned_escalations(
    escalation_service: EscalationServiceDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[EscalationRequestResponse]:
    """Get escalation requests assigned to the current user."""
    logger.debug(
        "Fetching assigned escalations (user_id={}, skip={}, limit={})",
        current_user.id,
        skip,
        limit,
    )
    requests, _ = await escalation_service.get_escalations(
        skip=skip,
        limit=limit,
        assigned_to=current_user.id,
    )
    return [EscalationRequestResponse.model_validate(req) for req in requests]


@router.get("/")
@router.get("")
async def get_escalations(
    escalation_service: EscalationServiceDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    user_id: Annotated[int | None, Query()] = None,
    assigned_to: Annotated[int | None, Query()] = None,
    escalation_type: Annotated[EscalationType | None, Query(alias="type")] = None,
    escalation_status: Annotated[EscalationStatus | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    sort_by: Annotated[str | None, Query()] = None,
    sort_order: Annotated[str, Query()] = "desc",
) -> EscalationRequestListResponse:
    """Get paginated list of escalation requests."""
    # Authorization: regular users can only see their own requests
    if not current_user.has_role(["HR", "ADMIN"]):
        if user_id is not None and user_id != current_user.id:
            logger.warning(
                "Escalation list forbidden: current_user_id={}, requested_user_id={}",
                current_user.id,
                user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users' requests",
            )
        user_id = current_user.id
        assigned_to = None  # cannot filter by assignee

    logger.debug(
        "Fetching escalations (current_user_id={}, user_id={}, assigned_to={}, skip={}, limit={})",
        current_user.id,
        user_id,
        assigned_to,
        skip,
        limit,
    )
    requests, total = await escalation_service.get_escalations(
        skip=skip,
        limit=limit,
        user_id=user_id,
        assigned_to=assigned_to,
        escalation_type=escalation_type,
        status=escalation_status,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return EscalationRequestListResponse(
        total=total,
        requests=[EscalationRequestResponse.model_validate(req) for req in requests],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.post("/")
@router.post("")
async def create_escalation(
    data: EscalationRequestCreate,
    escalation_service: EscalationServiceDep,
    current_user: CurrentUser,
) -> EscalationRequestResponse:
    """Create a new escalation request."""
    if data.user_id != current_user.id and not current_user.has_role(["HR", "ADMIN"]):
        logger.warning(
            "Create escalation forbidden (current_user_id={}, requested_user_id={})",
            current_user.id,
            data.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create requests for other users",
        )

    request = await escalation_service.create_escalation(data)
    logger.info("Escalation created via API (escalation_id={}, user_id={})", request.id, request.user_id)
    return EscalationRequestResponse.model_validate(request)


@router.get("/{escalation_id}")
async def get_escalation(
    escalation_id: int,
    escalation_service: EscalationServiceDep,
    current_user: CurrentUser,
) -> EscalationRequestResponse:
    """Get a specific escalation request by ID."""
    request = await escalation_service.get_escalation_by_id(escalation_id)

    # Check permission: user must be owner, assignee, or HR/Admin
    if current_user.id not in (request.user_id, request.assigned_to) and not current_user.has_role(["HR", "ADMIN"]):
        logger.warning(
            "Get escalation forbidden (current_user_id={}, escalation_id={})",
            current_user.id,
            escalation_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return EscalationRequestResponse.model_validate(request)


@router.patch("/{escalation_id}")
async def update_escalation(
    escalation_id: int,
    update_data: EscalationRequestUpdate,
    escalation_service: EscalationServiceDep,
    current_user: CurrentUser,
    uow: UOWDep,
) -> EscalationRequestResponse:
    """Update escalation request (status, assignee)."""
    # Fetch and check permissions
    request = await uow.escalations.get_by_id(escalation_id)
    if not request:
        logger.warning("Update escalation failed: not found (escalation_id={})", escalation_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation request not found",
        )

    if request.assigned_to != current_user.id and not current_user.has_role(["HR", "ADMIN"]):
        logger.warning(
            "Update escalation forbidden (current_user_id={}, escalation_id={}, assigned_to={})",
            current_user.id,
            escalation_id,
            request.assigned_to,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only assignee or HR can update this request",
        )

    updated = await escalation_service.update_escalation(escalation_id, update_data)
    logger.info("Escalation updated via API (escalation_id={}, user_id={})", escalation_id, current_user.id)
    return EscalationRequestResponse.model_validate(updated)


@router.post("/{escalation_id}/assign/{assignee_id}")
async def assign_escalation(
    escalation_id: int,
    assignee_id: int,
    escalation_service: EscalationServiceDep,
    _current_user: HRUser,  # Only HR/Admin can assign
) -> EscalationRequestResponse:
    """Assign escalation to a specific user (HR/Admin only)."""
    try:
        request = await escalation_service.assign_escalation(escalation_id, assignee_id)
    except NotFoundException as e:
        logger.warning("Assign escalation failed: not found (escalation_id={})", escalation_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    logger.info("Escalation assigned via API (escalation_id={}, assignee_id={})", escalation_id, assignee_id)
    return EscalationRequestResponse.model_validate(request)


@router.post("/{escalation_id}/resolve")
async def resolve_escalation(
    escalation_id: int,
    escalation_service: EscalationServiceDep,
    current_user: CurrentUser,
) -> EscalationRequestResponse:
    """Mark escalation as resolved. Can be done by assignee or HR/Admin."""
    # Permission check inside the endpoint
    request = await escalation_service.get_escalation_by_id(escalation_id)
    if request.assigned_to != current_user.id and not current_user.has_role(["HR", "ADMIN"]):
        logger.warning(
            "Resolve escalation forbidden (current_user_id={}, escalation_id={}, assigned_to={})",
            current_user.id,
            escalation_id,
            request.assigned_to,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only assignee or HR can resolve this request",
        )

    resolved = await escalation_service.resolve_escalation(escalation_id)
    logger.info("Escalation resolved via API (escalation_id={}, user_id={})", escalation_id, current_user.id)
    return EscalationRequestResponse.model_validate(resolved)


@router.get("/user/{user_id}")
async def get_user_escalations(
    user_id: int,
    escalation_service: EscalationServiceDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[EscalationRequestResponse]:
    """Get escalation requests for a specific user."""
    # Check permission: only that user or HR/Admin
    if user_id != current_user.id and not current_user.has_role(["HR", "ADMIN"]):
        logger.warning(
            "Get user escalations forbidden (current_user_id={}, requested_user_id={})",
            current_user.id,
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    requests, _ = await escalation_service.get_escalations(
        skip=skip,
        limit=limit,
        user_id=user_id,
    )
    return [EscalationRequestResponse.model_validate(req) for req in requests]


@router.delete("/{escalation_id}")
async def delete_escalation(
    escalation_id: int,
    uow: UOWDep,
    _current_user: AdminUser,  # Only admin can delete
) -> MessageResponse:
    """Delete an escalation request (admin only)."""
    deleted = await uow.escalations.delete(escalation_id)
    if not deleted:
        logger.warning("Delete escalation failed: not found (escalation_id={})", escalation_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation request not found",
        )
    await uow.commit()
    logger.info("Escalation deleted (escalation_id={})", escalation_id)
    return MessageResponse(message="Escalation request deleted successfully")
