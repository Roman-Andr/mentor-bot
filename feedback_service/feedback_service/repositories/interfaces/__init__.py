"""Repository interfaces following Interface Segregation Principle."""

from feedback_service.repositories.interfaces.base import BaseRepository
from feedback_service.repositories.interfaces.feedback import (
    ICommentRepository,
    IExperienceRatingRepository,
    IPulseSurveyRepository,
)

__all__ = [
    "BaseRepository",
    "ICommentRepository",
    "IExperienceRatingRepository",
    "IPulseSurveyRepository",
]
