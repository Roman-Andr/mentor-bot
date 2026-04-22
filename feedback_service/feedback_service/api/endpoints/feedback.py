"""Feedback API endpoints."""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from feedback_service.api.deps import CurrentUser, HRAdminUser, UOWDep, check_user_access
from feedback_service.models import Comment, ExperienceRating, PulseSurvey
from feedback_service.schemas import (
    CommentCreate,
    CommentListResponse,
    CommentReplyCreate,
    CommentResponse,
    ExperienceRatingCreate,
    ExperienceRatingListResponse,
    ExperienceRatingResponse,
    ExperienceStatsResponse,
    PulseStatsResponse,
    PulseSurveyCreate,
    PulseSurveyListResponse,
    PulseSurveyResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# Pulse Survey Endpoints
# ============================================================================

@router.post("/pulse", status_code=status.HTTP_201_CREATED)
async def submit_pulse_survey(
    data: PulseSurveyCreate,
    uow: UOWDep,
    current_user: CurrentUser,
) -> PulseSurveyResponse:
    """Submit a daily pulse survey rating. Can be anonymous."""
    try:
        if data.is_anonymous:
            # Store without user_id but keep department for analytics
            pulse_survey = PulseSurvey(
                user_id=None,
                is_anonymous=True,
                department_id=current_user.department_id,
                position_level=current_user.level,
                rating=data.rating,
            )
        else:
            # Normal attributed submission
            pulse_survey = PulseSurvey(
                user_id=current_user.id,
                is_anonymous=False,
                department_id=current_user.department_id,
                position_level=current_user.level,
                rating=data.rating,
            )

        result = await uow.pulse_surveys.create(pulse_survey)
        await uow.commit()
        return PulseSurveyResponse.model_validate(result)
    except Exception:
        logger.exception("Failed to submit pulse survey")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit pulse survey"
        ) from None


@router.get("/pulse")
async def get_pulse_surveys(
    uow: UOWDep,
    current_user: CurrentUser,
    user_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    search: Annotated[str | None, Query(description="Search in position level")] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> PulseSurveyListResponse:
    """
    Get pulse surveys.

    - Users can only see their own surveys
    - HR/Admin can see all surveys with user_id filter
    """
    effective_user_id = check_user_access(current_user, user_id, ["HR", "ADMIN"], "pulse surveys")

    try:
        surveys, total = await uow.pulse_surveys.get_by_user(
            user_id=effective_user_id,
            from_date=from_date,
            to_date=to_date,
            search=search,
            skip=skip,
            limit=limit,
        )

        return PulseSurveyListResponse(
            items=[PulseSurveyResponse.model_validate(s) for s in surveys],
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception:
        logger.exception("Failed to get pulse surveys")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pulse surveys",
        ) from None


@router.get("/pulse/stats")
async def get_pulse_stats(
    uow: UOWDep,
    current_user: CurrentUser,
    user_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> PulseStatsResponse:
    """
    Get pulse survey statistics.

    - Users can only see their own stats
    - HR/Admin can see all stats with user_id filter
    """
    effective_user_id = check_user_access(current_user, user_id, ["HR", "ADMIN"], "pulse stats")

    try:
        stats = await uow.pulse_surveys.get_stats(
            user_id=effective_user_id,
            from_date=from_date,
            to_date=to_date,
        )
        distribution = await uow.pulse_surveys.get_rating_distribution(
            user_id=effective_user_id,
            from_date=from_date,
            to_date=to_date,
        )

        return PulseStatsResponse(
            **stats,
            rating_distribution=distribution,
        )
    except Exception:
        logger.exception("Failed to get pulse stats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pulse stats",
        ) from None


@router.get("/pulse/anonymity-stats")
async def get_pulse_anonymity_stats(
    uow: UOWDep,
    current_user: HRAdminUser,
    department_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> dict:
    """Get anonymity stats for pulse surveys (HR/Admin only)."""
    try:
        stats = await uow.pulse_surveys.get_anonymity_stats(
            department_id=department_id,
            from_date=from_date,
            to_date=to_date,
        )
        return stats
    except Exception:
        logger.exception("Failed to get pulse anonymity stats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get anonymity stats",
        ) from None


# ============================================================================
# Experience Rating Endpoints
# ============================================================================

@router.post("/experience", status_code=status.HTTP_201_CREATED)
async def submit_experience_rating(
    data: ExperienceRatingCreate,
    uow: UOWDep,
    current_user: CurrentUser,
) -> ExperienceRatingResponse:
    """Submit an experience rating. Can be anonymous."""
    try:
        if data.is_anonymous:
            # Store without user_id but keep department for analytics
            rating = ExperienceRating(
                user_id=None,
                is_anonymous=True,
                department_id=current_user.department_id,
                rating=data.rating,
            )
        else:
            # Normal attributed submission
            rating = ExperienceRating(
                user_id=current_user.id,
                is_anonymous=False,
                department_id=current_user.department_id,
                rating=data.rating,
            )

        result = await uow.experience_ratings.create(rating)
        await uow.commit()
        return ExperienceRatingResponse.model_validate(result)
    except Exception:
        logger.exception("Failed to submit experience rating")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit experience rating"
        ) from None


@router.get("/experience")
async def get_experience_ratings(
    uow: UOWDep,
    current_user: CurrentUser,
    user_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    min_rating: Annotated[int | None, Query(ge=1, le=5)] = None,
    max_rating: Annotated[int | None, Query(ge=1, le=5)] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ExperienceRatingListResponse:
    """
    Get experience ratings with filters.

    - Users can only see their own ratings
    - HR/Admin can see all ratings with user_id filter
    """
    effective_user_id = check_user_access(current_user, user_id, ["HR", "ADMIN"], "experience ratings")

    try:
        ratings, total = await uow.experience_ratings.get_by_user(
            user_id=effective_user_id,
            from_date=from_date,
            to_date=to_date,
            min_rating=min_rating,
            max_rating=max_rating,
            skip=skip,
            limit=limit,
        )

        return ExperienceRatingListResponse(
            items=[ExperienceRatingResponse.model_validate(r) for r in ratings],
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception:
        logger.exception("Failed to get experience ratings")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get experience ratings",
        ) from None


@router.get("/experience/stats")
async def get_experience_stats(
    uow: UOWDep,
    current_user: CurrentUser,
    user_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> ExperienceStatsResponse:
    """
    Get experience rating statistics.

    - Users can only see their own stats
    - HR/Admin can see all stats with user_id filter
    """
    effective_user_id = check_user_access(current_user, user_id, ["HR", "ADMIN"], "experience stats")

    try:
        stats = await uow.experience_ratings.get_stats(
            user_id=effective_user_id,
            from_date=from_date,
            to_date=to_date,
        )
        distribution = await uow.experience_ratings.get_rating_distribution(
            user_id=effective_user_id,
            from_date=from_date,
            to_date=to_date,
        )

        return ExperienceStatsResponse(
            **stats,
            rating_distribution=distribution,
        )
    except Exception:
        logger.exception("Failed to get experience stats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get experience stats",
        ) from None


# ============================================================================
# Comment Endpoints
# ============================================================================

@router.post("/comments", status_code=status.HTTP_201_CREATED)
async def submit_comment(
    data: CommentCreate,
    uow: UOWDep,
    current_user: CurrentUser,
) -> CommentResponse:
    """Submit a comment or suggestion. Can be anonymous."""
    try:
        if data.is_anonymous:
            # Store without user_id but keep department for analytics
            comment = Comment(
                user_id=None,
                is_anonymous=True,
                department_id=current_user.department_id,
                comment=data.comment,
                allow_contact=data.allow_contact,
                contact_email=data.contact_email if data.allow_contact else None,
            )
        else:
            # Normal attributed submission
            comment = Comment(
                user_id=current_user.id,
                is_anonymous=False,
                department_id=current_user.department_id,
                comment=data.comment,
                allow_contact=False,
                contact_email=None,
            )

        result = await uow.comments.create(comment)
        await uow.commit()
        return CommentResponse.model_validate(result)
    except Exception:
        logger.exception("Failed to submit comment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit comment"
        ) from None


@router.get("/comments")
async def get_comments(
    uow: UOWDep,
    current_user: CurrentUser,
    user_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    search: Annotated[str | None, Query(description="Search in comment text")] = None,
    has_reply: Annotated[bool | None, Query(description="Filter by reply status")] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> CommentListResponse:
    """
    Get comments with filters.

    - Users can only see their own comments
    - HR/Admin can see all comments with user_id filter
    """
    effective_user_id = check_user_access(current_user, user_id, ["HR", "ADMIN"], "comments")

    try:
        comments, total = await uow.comments.get_by_user(
            user_id=effective_user_id,
            from_date=from_date,
            to_date=to_date,
            search=search,
            has_reply=has_reply,
            skip=skip,
            limit=limit,
        )

        return CommentListResponse(
            items=[CommentResponse.model_validate(c) for c in comments],
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception:
        logger.exception("Failed to get comments")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get comments",
        ) from None


@router.post("/comments/{comment_id}/reply")
async def reply_to_comment(
    comment_id: int,
    data: CommentReplyCreate,
    uow: UOWDep,
    current_user: HRAdminUser,
) -> CommentResponse:
    """HR/Admin can reply to comments. Cannot reply to anonymous comments unless contact email is provided."""
    try:
        # Check if comment exists and is not anonymous without contact info
        comment = await uow.comments.get_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )

        # Cannot reply to anonymous comments without contact info
        if comment.is_anonymous and not comment.allow_contact:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot reply to anonymous comments without contact information",
            )

        comment = await uow.comments.add_reply(
            comment_id=comment_id,
            reply=data.reply,
            replied_by=current_user.id,
        )

        await uow.commit()
        return CommentResponse.model_validate(comment)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to reply to comment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reply to comment",
        ) from None
