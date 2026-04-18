"""Common response schemas for feedback service."""

from typing import Any

from pydantic import BaseModel

from .comment import CommentResponse
from .experience_rating import ExperienceRatingResponse
from .pulse_survey import PulseSurveyResponse


class ServiceStatus(BaseModel):
    """Service status response schema."""

    service: str
    version: str
    status: str
    docs: str | None = None


class HealthCheck(BaseModel):
    """Health check response schema."""

    status: str
    service: str
    timestamp: str
    dependencies: dict[str, Any]


# List response schemas

class PulseSurveyListResponse(BaseModel):
    """Response schema for paginated pulse survey list."""

    items: list[PulseSurveyResponse]
    total: int
    skip: int
    limit: int


class ExperienceRatingListResponse(BaseModel):
    """Response schema for paginated experience rating list."""

    items: list[ExperienceRatingResponse]
    total: int
    skip: int
    limit: int


class CommentListResponse(BaseModel):
    """Response schema for paginated comment list."""

    items: list[CommentResponse]
    total: int
    skip: int
    limit: int


# Stats response schemas

class PulseStatsResponse(BaseModel):
    """Response schema for pulse survey statistics."""

    average_rating: float | None
    total_responses: int
    min_rating: int | None
    max_rating: int | None
    rating_distribution: dict[int, int]


class ExperienceStatsResponse(BaseModel):
    """Response schema for experience rating statistics."""

    average_rating: float | None
    total_ratings: int
    min_rating: int | None
    max_rating: int | None
    rating_distribution: dict[int, int]
