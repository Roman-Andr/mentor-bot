"""User-Mentor relationship management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from auth_service.api.deps import HRUser, UOWDep
from auth_service.models import UserMentor
from auth_service.schemas import (
    MessageResponse,
    UserMentorCreate,
    UserMentorListResponse,
    UserMentorResponse,
    UserMentorUpdate,
)

router = APIRouter()


@router.get("/")
@router.get("")
async def get_user_mentors(
    uow: UOWDep,
    _current_user: HRUser,
    user_id: Annotated[int | None, Query()] = None,
    mentor_id: Annotated[int | None, Query()] = None,
) -> UserMentorListResponse:
    """Get user-mentor relations (HR/admin only)."""
    if user_id:
        relations = await uow.user_mentors.get_by_user_id(user_id)
    elif mentor_id:
        relations = await uow.user_mentors.get_by_mentor_id(mentor_id)
    else:
        relations = list(await uow.user_mentors.get_all())

    return UserMentorListResponse(
        total=len(relations),
        relations=[UserMentorResponse.model_validate(r) for r in relations],
    )


@router.post("/")
@router.post("")
async def create_user_mentor(
    data: UserMentorCreate,
    uow: UOWDep,
    _current_user: HRUser,
) -> UserMentorResponse:
    """Create a user-mentor relation (HR/admin only)."""
    existing = await uow.user_mentors.get_by_user_and_mentor(data.user_id, data.mentor_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Relation already exists between this user and mentor",
        )

    active = await uow.user_mentors.get_active_by_user_id(data.user_id)
    if active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has an active mentor",
        )

    relation = UserMentor(
        user_id=data.user_id,
        mentor_id=data.mentor_id,
        notes=data.notes,
        is_active=True,
    )
    created = await uow.user_mentors.create(relation)
    return UserMentorResponse.model_validate(created)


@router.put("/{relation_id}")
async def update_user_mentor(
    relation_id: int,
    data: UserMentorUpdate,
    uow: UOWDep,
    _current_user: HRUser,
) -> UserMentorResponse:
    """Update a user-mentor relation (HR/admin only)."""
    relation = await uow.user_mentors.get_by_id(relation_id)
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation not found",
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(relation, field, value)

    updated = await uow.user_mentors.update(relation)
    return UserMentorResponse.model_validate(updated)


@router.delete("/{relation_id}")
async def delete_user_mentor(
    relation_id: int,
    uow: UOWDep,
    _current_user: HRUser,
) -> MessageResponse:
    """Delete a user-mentor relation (HR/admin only)."""
    deleted = await uow.user_mentors.delete(relation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation not found",
        )
    return MessageResponse(message="Relation deleted successfully")
