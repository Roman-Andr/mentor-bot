"""Feedback API endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from feedback_service.database import get_db
from feedback_service.repositories import CommentRepository, ExperienceRatingRepository, PulseSurveyRepository
from feedback_service.schemas import (
    CommentCreate,
    CommentResponse,
    ExperienceRatingCreate,
    ExperienceRatingResponse,
    PulseSurveyCreate,
    PulseSurveyResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/pulse", status_code=status.HTTP_201_CREATED)
async def submit_pulse_survey(
    data: PulseSurveyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PulseSurveyResponse:
    """Submit a daily pulse survey rating."""
    try:
        pulse_repo = PulseSurveyRepository(db)
        from feedback_service.models import PulseSurvey

        pulse_survey = PulseSurvey(user_id=data.user_id, rating=data.rating)
        result = await pulse_repo.create(pulse_survey)
        return PulseSurveyResponse.model_validate(result)
    except Exception as e:
        logger.exception(f"Failed to submit pulse survey: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit pulse survey")


@router.post("/experience", status_code=status.HTTP_201_CREATED)
async def submit_experience_rating(
    data: ExperienceRatingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExperienceRatingResponse:
    """Submit an experience rating."""
    try:
        rating_repo = ExperienceRatingRepository(db)
        from feedback_service.models import ExperienceRating

        rating = ExperienceRating(user_id=data.user_id, rating=data.rating)
        result = await rating_repo.create(rating)
        return ExperienceRatingResponse.model_validate(result)
    except Exception as e:
        logger.exception(f"Failed to submit experience rating: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit experience rating"
        )


@router.post("/comments", status_code=status.HTTP_201_CREATED)
async def submit_comment(
    data: CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CommentResponse:
    """Submit a comment or suggestion."""
    try:
        comment_repo = CommentRepository(db)
        from feedback_service.models import Comment

        comment = Comment(user_id=data.user_id, comment=data.comment)
        result = await comment_repo.create(comment)
        return CommentResponse.model_validate(result)
    except Exception as e:
        logger.exception(f"Failed to submit comment: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit comment")
