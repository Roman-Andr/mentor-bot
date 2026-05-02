"""Feedback API endpoints."""

import asyncio
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from feedback_service.api.deps import (
    CurrentUser,
    HRAdminUser,
    UOWDep,
    UserInfo,
    check_user_access,
    get_current_user_optional,
    verify_service_api_key,
)
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
from feedback_service.services.notification_client import NotificationClient

router = APIRouter()


# ============================================================================
# Pulse Survey Endpoints
# ============================================================================


@router.post("/pulse", status_code=status.HTTP_201_CREATED)
async def submit_pulse_survey(
    data: PulseSurveyCreate,
    uow: UOWDep,
    service_auth: Annotated[bool, Depends(verify_service_api_key)] = False,
    current_user: Annotated[UserInfo | None, Depends(get_current_user_optional)] = None,
) -> PulseSurveyResponse:
    """Submit a daily pulse survey rating. Can be anonymous."""
    try:
        # For service-to-service calls, use user_id from request body
        user_id = data.user_id if service_auth else (current_user.id if current_user else None)
        department_id = None if service_auth else (current_user.department_id if current_user else None)
        position_level = None if service_auth else (current_user.level if current_user else None)

        logger.debug(
            "Submitting pulse survey (user_id={}, anonymous={}, rating={}, service_call={})",
            user_id,
            data.is_anonymous,
            data.rating,
            service_auth,
        )
        if data.is_anonymous:
            # Store without user_id but keep department for analytics
            pulse_survey = PulseSurvey(
                user_id=None,
                is_anonymous=True,
                department_id=department_id,
                position_level=position_level,
                rating=data.rating,
            )
        else:
            # Normal attributed submission
            pulse_survey = PulseSurvey(
                user_id=user_id,
                is_anonymous=False,
                department_id=department_id,
                position_level=position_level,
                rating=data.rating,
            )

        result = await uow.pulse_surveys.create(pulse_survey)
        await uow.commit()
        logger.info(
            "Pulse survey submitted (survey_id={}, user_id={}, anonymous={})",
            result.id,
            user_id,
            data.is_anonymous,
        )
        return PulseSurveyResponse.model_validate(result)
    except Exception as e:
        logger.exception(f"Failed to submit pulse survey: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to submit pulse survey: {e!s}"
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
    sort_by: Annotated[str | None, Query(description="Sort by field")] = None,
    sort_order: Annotated[str | None, Query(description="Sort order: asc or desc")] = None,
) -> PulseSurveyListResponse:
    """
    Get pulse surveys.

    - Users can only see their own surveys
    - HR/Admin can see all surveys with user_id filter
    """
    effective_user_id = check_user_access(current_user, user_id, ["HR", "ADMIN"], "pulse surveys")

    try:
        logger.debug(
            "Fetching pulse surveys (current_user_id={}, effective_user_id={}, skip={}, limit={})",
            current_user.id,
            effective_user_id,
            skip,
            limit,
        )
        surveys, total = await uow.pulse_surveys.get_by_user(
            user_id=effective_user_id,
            from_date=from_date,
            to_date=to_date,
            search=search,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        logger.debug("Pulse surveys fetched (count={}, total={})", len(surveys), total)

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
        logger.debug(
            "Fetching pulse stats (current_user_id={}, effective_user_id={})",
            current_user.id,
            effective_user_id,
        )
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
        logger.debug(
            "Pulse stats fetched (current_user_id={}, effective_user_id={})", current_user.id, effective_user_id
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
        logger.debug(
            "Fetching pulse anonymity stats (current_user_id={}, department_id={})",
            current_user.id,
            department_id,
        )
        stats = await uow.pulse_surveys.get_anonymity_stats(
            department_id=department_id,
            from_date=from_date,
            to_date=to_date,
        )
        logger.debug("Pulse anonymity stats fetched (current_user_id={})", current_user.id)
    except Exception:
        logger.exception("Failed to get pulse anonymity stats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pulse anonymity stats",
        ) from None
    else:
        return stats


# ============================================================================
# Experience Rating Endpoints
# ============================================================================


@router.post("/experience", status_code=status.HTTP_201_CREATED)
async def submit_experience_rating(
    data: ExperienceRatingCreate,
    uow: UOWDep,
    service_auth: Annotated[bool, Depends(verify_service_api_key)] = False,
    current_user: Annotated[UserInfo | None, Depends(get_current_user_optional)] = None,
) -> ExperienceRatingResponse:
    """Submit an experience rating. Can be anonymous."""
    try:
        # For service-to-service calls, use user_id from request body
        user_id = data.user_id if service_auth else (current_user.id if current_user else None)
        department_id = None if service_auth else (current_user.department_id if current_user else None)

        logger.debug(
            "Submitting experience rating (user_id={}, anonymous={}, rating={}, service_call={})",
            user_id,
            data.is_anonymous,
            data.rating,
            service_auth,
        )
        if data.is_anonymous:
            # Store without user_id but keep department for analytics
            rating = ExperienceRating(
                user_id=None,
                is_anonymous=True,
                department_id=department_id,
                rating=data.rating,
            )
        else:
            # Normal attributed submission
            rating = ExperienceRating(
                user_id=user_id,
                is_anonymous=False,
                department_id=department_id,
                rating=data.rating,
            )

        result = await uow.experience_ratings.create(rating)
        await uow.commit()
        logger.info(
            "Experience rating submitted (rating_id={}, user_id={}, anonymous={})",
            result.id,
            user_id,
            data.is_anonymous,
        )
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
    sort_by: Annotated[str | None, Query(description="Sort by field")] = None,
    sort_order: Annotated[str | None, Query(description="Sort order: asc or desc")] = None,
) -> ExperienceRatingListResponse:
    """
    Get experience ratings with filters.

    - Users can only see their own ratings
    - HR/Admin can see all ratings with user_id filter
    """
    effective_user_id = check_user_access(current_user, user_id, ["HR", "ADMIN"], "experience ratings")

    try:
        logger.debug(
            "Fetching experience ratings (current_user_id={}, effective_user_id={}, skip={}, limit={})",
            current_user.id,
            effective_user_id,
            skip,
            limit,
        )
        ratings, total = await uow.experience_ratings.get_by_user(
            user_id=effective_user_id,
            from_date=from_date,
            to_date=to_date,
            min_rating=min_rating,
            max_rating=max_rating,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        logger.debug("Experience ratings fetched (count={}, total={})", len(ratings), total)

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
        logger.debug(
            "Fetching experience stats (current_user_id={}, effective_user_id={})",
            current_user.id,
            effective_user_id,
        )
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
        logger.debug(
            "Experience stats fetched (current_user_id={}, effective_user_id={})",
            current_user.id,
            effective_user_id,
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


@router.get("/experience/anonymity-stats")
async def get_experience_anonymity_stats(
    uow: UOWDep,
    current_user: HRAdminUser,
    department_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> dict:
    """Get anonymity stats for experience ratings (HR/Admin only)."""
    try:
        logger.debug(
            "Fetching experience anonymity stats (current_user_id={}, department_id={})",
            current_user.id,
            department_id,
        )
        stats = await uow.experience_ratings.get_anonymity_stats(
            department_id=department_id,
            from_date=from_date,
            to_date=to_date,
        )
        logger.debug("Experience anonymity stats fetched (current_user_id={})", current_user.id)
    except Exception:
        logger.exception("Failed to get experience anonymity stats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get experience anonymity stats",
        ) from None
    else:
        return stats


# ============================================================================
# Comment Endpoints
# ============================================================================


@router.post("/comments", status_code=status.HTTP_201_CREATED)
async def submit_comment(
    data: CommentCreate,
    uow: UOWDep,
    service_auth: Annotated[bool, Depends(verify_service_api_key)] = False,
    current_user: Annotated[UserInfo | None, Depends(get_current_user_optional)] = None,
) -> CommentResponse:
    """Submit a comment or suggestion. Can be anonymous."""
    try:
        # For service-to-service calls, use user_id from request body
        user_id = data.user_id if service_auth else (current_user.id if current_user else None)
        department_id = None if service_auth else (current_user.department_id if current_user else None)

        logger.debug(
            "Submitting comment (user_id={}, anonymous={}, allow_contact={}, service_call={})",
            user_id,
            data.is_anonymous,
            data.allow_contact,
            service_auth,
        )
        if data.is_anonymous:
            # Store without user_id but keep department for analytics
            comment = Comment(
                user_id=None,
                is_anonymous=True,
                department_id=department_id,
                comment=data.comment,
                allow_contact=data.allow_contact,
                contact_email=data.contact_email if data.allow_contact else None,
            )
        else:
            # Normal attributed submission
            comment = Comment(
                user_id=user_id,
                is_anonymous=False,
                department_id=department_id,
                comment=data.comment,
                allow_contact=False,
                contact_email=None,
            )

        result = await uow.comments.create(comment)
        await uow.commit()
        logger.info(
            "Comment submitted (comment_id={}, user_id={}, anonymous={})",
            result.id,
            user_id,
            data.is_anonymous,
        )
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
    sort_by: Annotated[str | None, Query(description="Sort by field")] = None,
    sort_order: Annotated[str | None, Query(description="Sort order: asc or desc")] = None,
) -> CommentListResponse:
    """
    Get comments with filters.

    - Users can only see their own comments
    - HR/Admin can see all comments with user_id filter
    """
    effective_user_id = check_user_access(current_user, user_id, ["HR", "ADMIN"], "comments")

    try:
        logger.debug(
            "Fetching comments (current_user_id={}, effective_user_id={}, skip={}, limit={})",
            current_user.id,
            effective_user_id,
            skip,
            limit,
        )
        comments, total = await uow.comments.get_by_user(
            user_id=effective_user_id,
            from_date=from_date,
            to_date=to_date,
            search=search,
            has_reply=has_reply,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        logger.debug("Comments fetched (count={}, total={})", len(comments), total)

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


@router.get("/comments/anonymity-stats")
async def get_comment_anonymity_stats(
    uow: UOWDep,
    current_user: HRAdminUser,
    department_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> dict:
    """Get anonymity stats for comments (HR/Admin only)."""
    try:
        logger.debug(
            "Fetching comment anonymity stats (current_user_id={}, department_id={})",
            current_user.id,
            department_id,
        )
        stats = await uow.comments.get_anonymity_stats(
            department_id=department_id,
            from_date=from_date,
            to_date=to_date,
        )
        logger.debug("Comment anonymity stats fetched (current_user_id={})", current_user.id)
    except Exception:
        logger.exception("Failed to get comment anonymity stats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get comment anonymity stats",
        ) from None
    else:
        return stats


@router.post("/comments/{comment_id}/reply")
async def reply_to_comment(
    comment_id: int,
    data: CommentReplyCreate,
    uow: UOWDep,
    current_user: HRAdminUser,
) -> CommentResponse:
    """HR/Admin can reply to comments. Cannot reply to anonymous comments unless contact email is provided."""
    try:
        logger.debug(
            "Replying to comment (comment_id={}, replied_by={})",
            comment_id,
            current_user.id,
        )
        # Check if comment exists and is not anonymous without contact info
        comment = await uow.comments.get_by_id(comment_id)
        if not comment:
            logger.warning("Reply to comment failed: not found (comment_id={})", comment_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )

        # Cannot reply to anonymous comments without contact info
        if comment.is_anonymous and not comment.allow_contact:
            logger.warning(
                "Reply to comment forbidden: anonymous without contact (comment_id={})",
                comment_id,
            )
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
        logger.info("Comment reply added (comment_id={}, replied_by={})", comment_id, current_user.id)

        # Send notification to comment author (fire-and-forget)
        notification_client = NotificationClient()
        _background_tasks = set()
        task = asyncio.create_task(
            notification_client.notify_comment_reply(
                comment_id=comment_id,
                original_comment_preview=comment.comment,
                reply_text=data.reply,
                replied_by_name=current_user.full_name or current_user.email,
                user_id=comment.user_id if not comment.is_anonymous else None,
            )
        )
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)

        return CommentResponse.model_validate(comment)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to reply to comment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reply to comment",
        ) from None
