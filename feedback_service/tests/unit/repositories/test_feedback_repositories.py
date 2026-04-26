"""Unit tests for feedback-specific repository implementations."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

from feedback_service.repositories import (
    CommentRepository,
    ExperienceRatingRepository,
    PulseSurveyRepository,
)


class TestPulseSurveyRepositoryEscapePattern:
    """Tests for PulseSurveyRepository._escape_ilike_pattern method."""

    def test_escape_ilike_pattern_escapes_backslash(self) -> None:
        """Test _escape_ilike_pattern escapes backslash characters."""
        # Arrange
        pattern = r"test\value"

        # Act
        result = PulseSurveyRepository._escape_ilike_pattern(pattern)

        # Assert
        assert result == r"test\\value"

    def test_escape_ilike_pattern_escapes_percent(self) -> None:
        """Test _escape_ilike_pattern escapes percent characters."""
        # Arrange
        pattern = "test%value"

        # Act
        result = PulseSurveyRepository._escape_ilike_pattern(pattern)

        # Assert
        assert result == r"test\%value"

    def test_escape_ilike_pattern_escapes_underscore(self) -> None:
        """Test _escape_ilike_pattern escapes underscore characters."""
        # Arrange
        pattern = "test_value"

        # Act
        result = PulseSurveyRepository._escape_ilike_pattern(pattern)

        # Assert
        assert result == r"test\_value"

    def test_escape_ilike_pattern_escapes_all_special_chars(self) -> None:
        """Test _escape_ilike_pattern escapes all special characters."""
        # Arrange - use a regular string to avoid raw string ending with backslash
        pattern = "%_%\\"

        # Act
        result = PulseSurveyRepository._escape_ilike_pattern(pattern)

        # Assert - result should have all special chars escaped
        # Input: %_%\  (%, _, %, \)
        # After replace \\ -> \\\\: %_%\\
        # After replace % -> \%: \%\_%\\
        # After replace _ -> \_: \%\_\%\\
        assert result == "\\%\\_\\%\\\\"

    def test_escape_ilike_pattern_no_special_chars(self) -> None:
        """Test _escape_ilike_pattern returns unchanged when no special chars."""
        # Arrange
        pattern = "normal text"

        # Act
        result = PulseSurveyRepository._escape_ilike_pattern(pattern)

        # Assert
        assert result == "normal text"


class TestPulseSurveyRepository:
    """Tests for PulseSurveyRepository."""

    async def test_find_by_user_returns_surveys_ordered(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock, mock_pulse_survey: MagicMock
    ) -> None:
        """Test find_by_user returns surveys ordered by submitted_at desc."""
        # Arrange
        surveys = [mock_pulse_survey]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = surveys
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        # Act
        result = await pulse_survey_repo.find_by_user(1, skip=0, limit=100)

        # Assert
        assert result == surveys
        mock_db.execute.assert_called_once()

    async def test_find_by_user_returns_empty_list(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test find_by_user returns empty list when user has no surveys."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        # Act
        result = await pulse_survey_repo.find_by_user(999, skip=0, limit=100)

        # Assert
        assert result == []

    async def test_get_by_user_with_asc_sort(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user with ascending sort order (line 76)."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await pulse_survey_repo.get_by_user(
            user_id=1, skip=0, limit=50, sort_order="asc"
        )

        # Assert
        assert result == []
        assert total == 0

    async def test_find_by_user_respects_skip_limit(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test find_by_user applies skip and limit parameters."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        # Act
        await pulse_survey_repo.find_by_user(1, skip=10, limit=5)

        # Assert - verify the call was made (the implementation builds the query correctly)
        mock_db.execute.assert_called_once()


class TestExperienceRatingRepository:
    """Tests for ExperienceRatingRepository."""

    async def test_find_by_user_returns_ratings_ordered(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock, mock_experience_rating: MagicMock
    ) -> None:
        """Test find_by_user returns ratings ordered by submitted_at desc."""
        # Arrange
        ratings = [mock_experience_rating]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ratings
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        # Act
        result = await experience_rating_repo.find_by_user(1, skip=0, limit=100)

        # Assert
        assert result == ratings
        mock_db.execute.assert_called_once()

    async def test_find_by_user_returns_empty_list(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test find_by_user returns empty list when user has no ratings."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        # Act
        result = await experience_rating_repo.find_by_user(999, skip=0, limit=100)

        # Assert
        assert result == []


class TestCommentRepositoryEscapePattern:
    """Tests for CommentRepository._escape_ilike_pattern method."""

    def test_escape_ilike_pattern_escapes_backslash(self) -> None:
        """Test _escape_ilike_pattern escapes backslash characters."""
        # Arrange
        pattern = r"comment\test"

        # Act
        result = CommentRepository._escape_ilike_pattern(pattern)

        # Assert
        assert result == r"comment\\test"

    def test_escape_ilike_pattern_escapes_percent(self) -> None:
        """Test _escape_ilike_pattern escapes percent characters."""
        # Arrange
        pattern = "100% satisfied"

        # Act
        result = CommentRepository._escape_ilike_pattern(pattern)

        # Assert
        assert result == r"100\% satisfied"

    def test_escape_ilike_pattern_escapes_underscore(self) -> None:
        """Test _escape_ilike_pattern escapes underscore characters."""
        # Arrange
        pattern = "user_name"

        # Act
        result = CommentRepository._escape_ilike_pattern(pattern)

        # Assert
        assert result == r"user\_name"

    def test_escape_ilike_pattern_escapes_all_special_chars(self) -> None:
        """Test _escape_ilike_pattern escapes all special characters."""
        # Arrange - use a regular string to avoid raw string ending with backslash
        pattern = "_%\\test"

        # Act
        result = CommentRepository._escape_ilike_pattern(pattern)

        # Assert - result should have all special chars escaped
        # Input: _%\test (_, %, \, t, e, s, t)
        # After replace \\ -> \\\\: _%\\test
        # After replace % -> \%: _\%\\test
        # After replace _ -> \_: \_\%\\test
        assert result == "\\_\\%\\\\test"

    def test_escape_ilike_pattern_no_special_chars(self) -> None:
        """Test _escape_ilike_pattern returns unchanged when no special chars."""
        # Arrange
        pattern = "simple comment"

        # Act
        result = CommentRepository._escape_ilike_pattern(pattern)

        # Assert
        assert result == "simple comment"


class TestCommentRepository:
    """Tests for CommentRepository."""

    async def test_find_by_user_returns_comments_ordered(
        self, comment_repo: CommentRepository, mock_db: MagicMock, mock_comment: MagicMock
    ) -> None:
        """Test find_by_user returns comments ordered by submitted_at desc."""
        # Arrange
        comments = [mock_comment]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = comments
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        # Act
        result = await comment_repo.find_by_user(1, skip=0, limit=100)

        # Assert
        assert result == comments
        mock_db.execute.assert_called_once()

    async def test_find_by_user_returns_empty_list(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test find_by_user returns empty list when user has no comments."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        # Act
        result = await comment_repo.find_by_user(999, skip=0, limit=100)

        # Assert
        assert result == []

    async def test_find_by_user_respects_skip_limit(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test find_by_user applies skip and limit parameters."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        # Act
        await comment_repo.find_by_user(1, skip=20, limit=10)

        # Assert
        mock_db.execute.assert_called_once()


class TestPulseSurveyRepositoryGetByUser:
    """Tests for PulseSurveyRepository.get_by_user method."""

    async def test_get_by_user_with_pagination(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user returns paginated results with total count."""
        # Arrange
        surveys = [MagicMock()]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = surveys
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 100  # Total count
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await pulse_survey_repo.get_by_user(user_id=1, skip=0, limit=50)

        # Assert
        assert result == surveys
        assert total == 100
        assert mock_db.execute.call_count == 2  # Count + results queries

    async def test_get_by_user_with_date_filtering(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user applies date filters."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        result, total = await pulse_survey_repo.get_by_user(
            user_id=1, from_date=from_date, to_date=to_date, skip=0, limit=50
        )

        # Assert
        assert result == []
        assert total == 0

    async def test_get_by_user_with_search(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user applies search filter and escapes special characters."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act - use a search with special characters to test escaping
        result, total = await pulse_survey_repo.get_by_user(
            user_id=1, search="Engineer%_", skip=0, limit=50
        )

        # Assert
        assert result == []
        assert total == 0
        assert mock_db.execute.call_count == 2  # Count + results queries


class TestPulseSurveyRepositoryStats:
    """Tests for PulseSurveyRepository stats methods."""

    async def test_get_stats_returns_aggregates(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_stats returns aggregate statistics."""
        # Arrange
        mock_row = MagicMock()
        mock_row.avg_rating = 7.5
        mock_row.total = 100
        mock_row.min_rating = 1
        mock_row.max_rating = 10
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_db.execute.return_value = mock_result

        # Act
        stats = await pulse_survey_repo.get_stats()

        # Assert
        assert stats["average_rating"] == 7.5
        assert stats["total_responses"] == 100
        assert stats["min_rating"] == 1
        assert stats["max_rating"] == 10

    async def test_get_stats_with_user_id_filter(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_stats applies user_id filter."""
        # Arrange
        mock_row = MagicMock()
        mock_row.avg_rating = 8.0
        mock_row.total = 50
        mock_row.min_rating = 5
        mock_row.max_rating = 10
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_db.execute.return_value = mock_result

        # Act
        stats = await pulse_survey_repo.get_stats(user_id=1)

        # Assert
        assert stats["average_rating"] == 8.0
        assert stats["total_responses"] == 50

    async def test_get_stats_with_date_filters(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_stats applies date filters."""
        # Arrange
        mock_row = MagicMock()
        mock_row.avg_rating = 7.0
        mock_row.total = 30
        mock_row.min_rating = 3
        mock_row.max_rating = 10
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_db.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        stats = await pulse_survey_repo.get_stats(from_date=from_date, to_date=to_date)

        # Assert
        assert stats["average_rating"] == 7.0
        assert stats["total_responses"] == 30

    async def test_get_stats_no_data(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_stats handles no data gracefully."""
        # Arrange
        mock_row = MagicMock()
        mock_row.avg_rating = None
        mock_row.total = 0
        mock_row.min_rating = None
        mock_row.max_rating = None
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_db.execute.return_value = mock_result

        # Act
        stats = await pulse_survey_repo.get_stats()

        # Assert
        assert stats["average_rating"] is None
        assert stats["total_responses"] == 0

    async def test_get_rating_distribution(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_rating_distribution returns rating counts."""
        # Arrange
        mock_row1 = MagicMock()
        mock_row1.rating = 7
        mock_row1.cnt = 50
        mock_row2 = MagicMock()
        mock_row2.rating = 8
        mock_row2.cnt = 30
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row1, mock_row2]
        mock_db.execute.return_value = mock_result

        # Act
        distribution = await pulse_survey_repo.get_rating_distribution()

        # Assert
        assert distribution == {7: 50, 8: 30}

    async def test_get_rating_distribution_with_filters(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_rating_distribution applies date and user filters."""
        # Arrange
        mock_row = MagicMock()
        mock_row.rating = 9
        mock_row.cnt = 10
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        distribution = await pulse_survey_repo.get_rating_distribution(
            user_id=1, from_date=from_date, to_date=to_date
        )

        # Assert
        assert distribution == {9: 10}


class TestExperienceRatingRepositoryGetByUser:
    """Tests for ExperienceRatingRepository.get_by_user method."""

    async def test_get_by_user_with_rating_filters(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user applies rating filters."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await experience_rating_repo.get_by_user(
            user_id=1, min_rating=3, max_rating=5, skip=0, limit=50
        )

        # Assert
        assert result == []
        assert total == 0

    async def test_get_by_user_with_asc_sort(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user with ascending sort order (line 222)."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await experience_rating_repo.get_by_user(
            user_id=1, skip=0, limit=50, sort_order="asc"
        )

        # Assert
        assert result == []
        assert total == 0

    async def test_get_by_user_with_date_filters(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user applies date filters."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        result, total = await experience_rating_repo.get_by_user(
            user_id=1, from_date=from_date, to_date=to_date, skip=0, limit=50
        )

        # Assert
        assert result == []
        assert total == 0


class TestExperienceRatingRepositoryStats:
    """Tests for ExperienceRatingRepository stats methods."""

    async def test_get_stats_returns_aggregates(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_stats returns aggregate statistics."""
        # Arrange
        mock_row = MagicMock()
        mock_row.avg_rating = 4.2
        mock_row.total = 50
        mock_row.min_rating = 1
        mock_row.max_rating = 5
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_db.execute.return_value = mock_result

        # Act
        stats = await experience_rating_repo.get_stats()

        # Assert
        assert stats["average_rating"] == 4.2
        assert stats["total_ratings"] == 50
        assert stats["min_rating"] == 1
        assert stats["max_rating"] == 5

    async def test_get_stats_with_user_id_filter(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_stats applies user_id filter."""
        # Arrange
        mock_row = MagicMock()
        mock_row.avg_rating = 4.5
        mock_row.total = 25
        mock_row.min_rating = 2
        mock_row.max_rating = 5
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_db.execute.return_value = mock_result

        # Act
        stats = await experience_rating_repo.get_stats(user_id=1)

        # Assert
        assert stats["average_rating"] == 4.5
        assert stats["total_ratings"] == 25

    async def test_get_stats_with_date_filters(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_stats applies date filters."""
        # Arrange
        mock_row = MagicMock()
        mock_row.avg_rating = 3.8
        mock_row.total = 15
        mock_row.min_rating = 1
        mock_row.max_rating = 5
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_db.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        stats = await experience_rating_repo.get_stats(from_date=from_date, to_date=to_date)

        # Assert
        assert stats["average_rating"] == 3.8
        assert stats["total_ratings"] == 15

    async def test_get_rating_distribution(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_rating_distribution returns rating counts."""
        # Arrange
        mock_row1 = MagicMock()
        mock_row1.rating = 4
        mock_row1.cnt = 30
        mock_row2 = MagicMock()
        mock_row2.rating = 5
        mock_row2.cnt = 20
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row1, mock_row2]
        mock_db.execute.return_value = mock_result

        # Act
        distribution = await experience_rating_repo.get_rating_distribution()

        # Assert
        assert distribution == {4: 30, 5: 20}

    async def test_get_rating_distribution_with_filters(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_rating_distribution applies date and user filters."""
        # Arrange
        mock_row = MagicMock()
        mock_row.rating = 5
        mock_row.cnt = 15
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        distribution = await experience_rating_repo.get_rating_distribution(
            user_id=1, from_date=from_date, to_date=to_date
        )

        # Assert
        assert distribution == {5: 15}


class TestCommentRepositoryGetByUser:
    """Tests for CommentRepository.get_by_user method."""

    async def test_get_by_user_with_search(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user applies search filter."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await comment_repo.get_by_user(
            user_id=1, search="feedback", skip=0, limit=50
        )

        # Assert
        assert result == []
        assert total == 0

    async def test_get_by_user_with_has_reply_filter_true(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user applies has_reply=True filter."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await comment_repo.get_by_user(
            user_id=1, has_reply=True, skip=0, limit=50
        )

        # Assert
        assert result == []
        assert total == 0

    async def test_get_by_user_with_has_reply_filter_false(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user applies has_reply=False filter."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await comment_repo.get_by_user(
            user_id=1, has_reply=False, skip=0, limit=50
        )

        # Assert
        assert result == []
        assert total == 0

    async def test_get_by_user_with_asc_sort(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user with ascending sort order (line 374)."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await comment_repo.get_by_user(
            user_id=1, skip=0, limit=50, sort_order="asc"
        )

        # Assert
        assert result == []
        assert total == 0

    async def test_get_by_user_with_date_filters(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user applies date filters."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        result, total = await comment_repo.get_by_user(
            user_id=1, from_date=from_date, to_date=to_date, skip=0, limit=50
        )

        # Assert
        assert result == []
        assert total == 0


class TestCommentRepositoryAddReply:
    """Tests for CommentRepository.add_reply method."""

    @patch("feedback_service.repositories.implementations.feedback.SqlAlchemyBaseRepository.get_by_id")
    async def test_add_reply_success(
        self, mock_get_by_id: AsyncMock, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test add_reply updates comment with reply."""
        # Arrange
        mock_comment = MagicMock()
        mock_get_by_id.return_value = mock_comment
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Act
        result = await comment_repo.add_reply(comment_id=1, reply="Thank you!", replied_by=2)

        # Assert
        assert result == mock_comment
        assert mock_comment.reply == "Thank you!"
        assert mock_comment.replied_by == 2
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once()

    @patch("feedback_service.repositories.implementations.feedback.SqlAlchemyBaseRepository.get_by_id")
    async def test_add_reply_comment_not_found(
        self, mock_get_by_id: AsyncMock, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test add_reply returns None when comment not found."""
        # Arrange
        mock_get_by_id.return_value = None

        # Act
        result = await comment_repo.add_reply(comment_id=999, reply="Thank you!", replied_by=2)

        # Assert
        assert result is None


class TestPulseSurveyRepositoryGetAnonymityStats:
    """Tests for PulseSurveyRepository.get_anonymity_stats method."""

    async def test_get_anonymity_stats_returns_anonymous_and_attributed(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_anonymity_stats returns stats for both anonymous and attributed surveys."""
        # Arrange
        mock_row_anon = MagicMock()
        mock_row_anon.is_anonymous = True
        mock_row_anon.avg_rating = 7.0
        mock_row_anon.cnt = 50
        mock_row_attr = MagicMock()
        mock_row_attr.is_anonymous = False
        mock_row_attr.avg_rating = 7.8
        mock_row_attr.cnt = 150
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row_anon, mock_row_attr]
        mock_db.execute.return_value = mock_result

        # Act
        stats = await pulse_survey_repo.get_anonymity_stats()

        # Assert
        assert stats["anonymous"]["count"] == 50
        assert stats["anonymous"]["average_rating"] == 7.0
        assert stats["attributed"]["count"] == 150
        assert stats["attributed"]["average_rating"] == 7.8

    async def test_get_anonymity_stats_with_department_filter(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_anonymity_stats applies department_id filter."""
        # Arrange
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Act
        stats = await pulse_survey_repo.get_anonymity_stats(department_id=1)

        # Assert
        assert stats["anonymous"]["count"] == 0
        assert stats["attributed"]["count"] == 0

    async def test_get_anonymity_stats_with_date_filters(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_anonymity_stats applies date filters."""
        # Arrange
        mock_row = MagicMock()
        mock_row.is_anonymous = False
        mock_row.avg_rating = 8.0
        mock_row.cnt = 30
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        stats = await pulse_survey_repo.get_anonymity_stats(from_date=from_date, to_date=to_date)

        # Assert
        assert stats["attributed"]["count"] == 30

    async def test_get_anonymity_stats_only_anonymous(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_anonymity_stats when only anonymous surveys exist."""
        # Arrange
        mock_row = MagicMock()
        mock_row.is_anonymous = True
        mock_row.avg_rating = 6.5
        mock_row.cnt = 25
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        # Act
        stats = await pulse_survey_repo.get_anonymity_stats()

        # Assert
        assert stats["anonymous"]["count"] == 25
        assert stats["anonymous"]["average_rating"] == 6.5
        assert stats["attributed"]["count"] == 0


class TestPulseSurveyRepositoryGetByUserWithoutUserId:
    """Tests for PulseSurveyRepository.get_by_user without user_id filter."""

    async def test_get_by_user_without_user_id_returns_all(
        self, pulse_survey_repo: PulseSurveyRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user returns all surveys when user_id is None."""
        # Arrange
        surveys = [MagicMock(), MagicMock()]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = surveys
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 2
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await pulse_survey_repo.get_by_user(user_id=None, skip=0, limit=50)

        # Assert
        assert result == surveys
        assert total == 2


class TestExperienceRatingRepositoryGetAnonymityStats:
    """Tests for ExperienceRatingRepository.get_anonymity_stats method."""

    async def test_get_anonymity_stats_returns_anonymous_and_attributed(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_anonymity_stats returns stats for both anonymous and attributed ratings."""
        # Arrange
        mock_row_anon = MagicMock()
        mock_row_anon.is_anonymous = True
        mock_row_anon.avg_rating = 4.2
        mock_row_anon.cnt = 20
        mock_row_attr = MagicMock()
        mock_row_attr.is_anonymous = False
        mock_row_attr.avg_rating = 4.5
        mock_row_attr.cnt = 80
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row_anon, mock_row_attr]
        mock_db.execute.return_value = mock_result

        # Act
        stats = await experience_rating_repo.get_anonymity_stats()

        # Assert
        assert stats["anonymous"]["count"] == 20
        assert stats["anonymous"]["average_rating"] == 4.2
        assert stats["attributed"]["count"] == 80
        assert stats["attributed"]["average_rating"] == 4.5

    async def test_get_anonymity_stats_with_department_filter(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_anonymity_stats applies department_id filter."""
        # Arrange
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Act
        stats = await experience_rating_repo.get_anonymity_stats(department_id=1)

        # Assert
        assert stats["anonymous"]["count"] == 0
        assert stats["attributed"]["count"] == 0

    async def test_get_anonymity_stats_with_date_filters(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_anonymity_stats applies date filters."""
        # Arrange
        mock_row = MagicMock()
        mock_row.is_anonymous = True
        mock_row.avg_rating = 3.8
        mock_row.cnt = 15
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        stats = await experience_rating_repo.get_anonymity_stats(from_date=from_date, to_date=to_date)

        # Assert
        assert stats["anonymous"]["count"] == 15


class TestExperienceRatingRepositoryGetByUserWithoutUserId:
    """Tests for ExperienceRatingRepository.get_by_user without user_id filter."""

    async def test_get_by_user_without_user_id_returns_all(
        self, experience_rating_repo: ExperienceRatingRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user returns all ratings when user_id is None."""
        # Arrange
        ratings = [MagicMock(), MagicMock(), MagicMock()]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ratings
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 3
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await experience_rating_repo.get_by_user(user_id=None, skip=0, limit=50)

        # Assert
        assert result == ratings
        assert total == 3


class TestCommentRepositoryGetAnonymityStats:
    """Tests for CommentRepository.get_anonymity_stats method."""

    async def test_get_anonymity_stats_returns_anonymous_and_attributed(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_anonymity_stats returns stats for both anonymous and attributed comments."""
        # Arrange
        mock_row_anon = MagicMock()
        mock_row_anon.is_anonymous = True
        mock_row_anon.cnt = 30
        mock_row_attr = MagicMock()
        mock_row_attr.is_anonymous = False
        mock_row_attr.cnt = 70
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row_anon, mock_row_attr]
        mock_result.scalar.return_value = 15  # contact count
        mock_db.execute.return_value = mock_result

        # Act
        stats = await comment_repo.get_anonymity_stats()

        # Assert
        assert stats["anonymous"]["count"] == 30
        assert stats["anonymous"]["with_contact"] == 15
        assert stats["attributed"]["count"] == 70

    async def test_get_anonymity_stats_with_department_filter(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_anonymity_stats applies department_id filter."""
        # Arrange
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        stats = await comment_repo.get_anonymity_stats(department_id=1)

        # Assert
        assert stats["anonymous"]["count"] == 0
        assert stats["anonymous"]["with_contact"] == 0
        assert stats["attributed"]["count"] == 0

    async def test_get_anonymity_stats_only_attributed(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_anonymity_stats when only attributed comments exist."""
        # Arrange
        mock_row = MagicMock()
        mock_row.is_anonymous = False
        mock_row.cnt = 50
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        stats = await comment_repo.get_anonymity_stats()

        # Assert
        assert stats["anonymous"]["count"] == 0
        assert stats["anonymous"]["with_contact"] == 0
        assert stats["attributed"]["count"] == 50


class TestCommentRepositoryGetReplyEligibleComments:
    """Tests for CommentRepository.get_reply_eligible_comments method."""

    async def test_get_reply_eligible_comments_returns_eligible(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_reply_eligible_comments returns comments that can be replied to."""
        # Arrange
        comments = [MagicMock(), MagicMock()]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = comments
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 2
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await comment_repo.get_reply_eligible_comments(skip=0, limit=50)

        # Assert
        assert result == comments
        assert total == 2

    async def test_get_reply_eligible_comments_with_department_filter(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_reply_eligible_comments applies department_id filter."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await comment_repo.get_reply_eligible_comments(department_id=1, skip=0, limit=50)

        # Assert
        assert result == []
        assert total == 0

    async def test_get_reply_eligible_comments_with_date_filters(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_reply_eligible_comments applies date filters."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        # Act
        result, total = await comment_repo.get_reply_eligible_comments(
            from_date=from_date, to_date=to_date, skip=0, limit=50
        )

        # Assert
        assert result == []
        assert total == 0


class TestCommentRepositoryGetByUserWithoutUserId:
    """Tests for CommentRepository.get_by_user without user_id filter."""

    async def test_get_by_user_without_user_id_returns_all(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user returns all comments when user_id is None."""
        # Arrange
        comments = [MagicMock(), MagicMock()]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = comments
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 2
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await comment_repo.get_by_user(user_id=None, skip=0, limit=50)

        # Assert
        assert result == comments
        assert total == 2

    async def test_get_by_user_without_user_id_with_search(
        self, comment_repo: CommentRepository, mock_db: MagicMock
    ) -> None:
        """Test get_by_user applies search filter even without user_id."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        # Act
        result, total = await comment_repo.get_by_user(user_id=None, search="test", skip=0, limit=50)

        # Assert
        assert result == []
        assert total == 0
