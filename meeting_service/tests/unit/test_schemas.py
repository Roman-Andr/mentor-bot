"""Unit tests for schemas."""

import pytest
from pydantic import ValidationError

from meeting_service.schemas.user_meeting import UserMeetingComplete


class TestUserMeetingCompleteRatingValidation:
    """Tests for UserMeetingComplete rating validation."""

    def test_valid_rating_minimum(self):
        """Test rating of 1 is valid."""
        data = UserMeetingComplete(rating=1)
        assert data.rating == 1

    def test_valid_rating_maximum(self):
        """Test rating of 5 is valid."""
        data = UserMeetingComplete(rating=5)
        assert data.rating == 5

    def test_valid_rating_middle(self):
        """Test rating of 3 is valid."""
        data = UserMeetingComplete(rating=3)
        assert data.rating == 3

    def test_rating_below_minimum(self):
        """Test rating below 1 raises validation error via Field(ge=1)."""
        with pytest.raises(ValidationError) as exc_info:
            UserMeetingComplete(rating=0)
        # Pydantic's Field validation produces this message
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_rating_above_maximum(self):
        """Test rating above 5 raises validation error via Field(le=5)."""
        with pytest.raises(ValidationError) as exc_info:
            UserMeetingComplete(rating=6)
        # Pydantic's Field validation produces this message
        assert "less than or equal to 5" in str(exc_info.value)

    def test_negative_rating(self):
        """Test negative rating raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            UserMeetingComplete(rating=-1)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_none_rating(self):
        """Test None rating is allowed."""
        data = UserMeetingComplete(rating=None)
        assert data.rating is None

    def test_no_rating(self):
        """Test omitting rating is allowed."""
        data = UserMeetingComplete()
        assert data.rating is None

    def test_feedback_only(self):
        """Test providing only feedback is valid."""
        data = UserMeetingComplete(feedback="Great meeting!")
        assert data.feedback == "Great meeting!"
        assert data.rating is None

    def test_validate_rating_called_for_edge_case(self):
        """
        Test that custom validator works for edge cases within range.

        Note: The @field_validator only runs when value passes Field(ge=1, le=5).
        The validator ensures 1-5 range but Field constraints catch outliers first.
        """
        # Valid boundary values pass both Field and validator
        assert UserMeetingComplete(rating=1).rating == 1
        assert UserMeetingComplete(rating=5).rating == 5

    def test_custom_validator_rating_error_message(self):
        """Test custom validator error message for out-of-range rating.

        This directly tests the @field_validator code path at lines 44-45.
        Field constraints usually catch these first, but we test the validator
        directly to ensure coverage of the error handling code.
        """
        from meeting_service.schemas.user_meeting import MIN_RATING, MAX_RATING

        # Directly call the validator to trigger lines 44-45
        # Note: In Pydantic v2, field validators receive (cls, value)
        with pytest.raises(ValueError) as exc_info:
            UserMeetingComplete.validate_rating(0)
        assert f"Rating must be between {MIN_RATING} and {MAX_RATING}" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            UserMeetingComplete.validate_rating(6)
        assert f"Rating must be between {MIN_RATING} and {MAX_RATING}" in str(exc_info.value)

    def test_custom_validator_allows_valid_ratings_directly(self):
        """Test that custom validator allows valid ratings when called directly."""
        # Valid ratings should pass through without error
        assert UserMeetingComplete.validate_rating(1) == 1
        assert UserMeetingComplete.validate_rating(3) == 3
        assert UserMeetingComplete.validate_rating(5) == 5
        assert UserMeetingComplete.validate_rating(None) is None
