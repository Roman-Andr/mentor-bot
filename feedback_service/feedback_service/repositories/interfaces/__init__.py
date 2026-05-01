"""Repository interfaces following Interface Segregation Principle."""

from feedback_service.repositories.interfaces.base import BaseRepository
from feedback_service.repositories.interfaces.feedback import (
    ICommentRepository,
    IExperienceRatingRepository,
    IPulseSurveyRepository,
)
from feedback_service.repositories.interfaces.feedback_status_change_history import IFeedbackStatusChangeHistoryRepository

__all__ = [
    "BaseRepository",
    "ICommentRepository",
    "IExperienceRatingRepository",
    "IFeedbackStatusChangeHistoryRepository",
    "IPulseSurveyRepository",
]
