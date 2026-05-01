"""Tests for audit API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.api.endpoints.audit import (
    get_article_change_history,
    get_article_view_history,
    get_category_change_history,
    get_dialogue_scenario_change_history,
    require_hr_or_admin,
)
from knowledge_service.core import UserRole


@pytest.fixture
def mock_uow():
    """Create a mock Unit of Work."""
    uow = MagicMock()
    uow.article_change_history = AsyncMock()
    uow.article_view_history = AsyncMock()
    uow.category_change_history = AsyncMock()
    uow.dialogue_scenario_change_history = AsyncMock()
    return uow


@pytest.fixture
def mock_hr_user():
    """Create a mock HR user."""
    user = MagicMock()
    user.role = UserRole.HR
    return user


@pytest.fixture
def mock_admin_user():
    """Create a mock Admin user."""
    user = MagicMock()
    user.role = UserRole.ADMIN
    return user


@pytest.fixture
def mock_regular_user():
    """Create a mock regular user."""
    user = MagicMock()
    user.role = UserRole.MENTOR
    return user


class TestRequireHrOrAdmin:
    """Test require_hr_or_admin function."""

    def test_hr_user_allowed(self, mock_hr_user):
        """Test HR user is allowed."""
        require_hr_or_admin(mock_hr_user)  # Should not raise

    def test_admin_user_allowed(self, mock_admin_user):
        """Test Admin user is allowed."""
        require_hr_or_admin(mock_admin_user)  # Should not raise

    def test_regular_user_denied(self, mock_regular_user):
        """Test regular user is denied."""
        with pytest.raises(PermissionError) as exc_info:
            require_hr_or_admin(mock_regular_user)
        assert "Access denied" in str(exc_info.value)


class TestGetArticleChangeHistory:
    """Test article change history endpoint."""

    async def test_get_all_history(self, mock_uow, mock_hr_user):
        """Test getting all article change history."""
        mock_uow.article_change_history.get_all.return_value = ([], 0)

        result = await get_article_change_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            article_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert result.total == 0
        assert len(result.items) == 0
        mock_uow.article_change_history.get_all.assert_called_once()

    async def test_get_history_by_article_id(self, mock_uow, mock_hr_user, mock_article_change_history):
        """Test getting history for specific article."""
        mock_uow.article_change_history.get_by_article_id.return_value = [mock_article_change_history]

        result = await get_article_change_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            article_id=1,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].id == 1
        assert result.items[0].article_id == 1
        assert result.items[0].action == "created"
        mock_uow.article_change_history.get_by_article_id.assert_called_once_with(
            article_id=1, from_date=None, to_date=None
        )

    async def test_get_history_with_date_filters(self, mock_uow, mock_hr_user):
        """Test getting history with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_uow.article_change_history.get_all.return_value = ([], 0)

        result = await get_article_change_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            article_id=None,
            from_date=from_date,
            to_date=to_date,
            limit=50,
            offset=0,
        )

        mock_uow.article_change_history.get_all.assert_called_once_with(
            from_date=from_date, to_date=to_date, limit=50, offset=0
        )

    async def test_regular_user_denied(self, mock_uow, mock_regular_user):
        """Test regular user is denied access."""
        with pytest.raises(PermissionError):
            await get_article_change_history(
                current_user=mock_regular_user,
                uow=mock_uow,
                article_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )


class TestGetArticleViewHistory:
    """Test article view history endpoint."""

    async def test_get_all_view_history(self, mock_uow, mock_hr_user):
        """Test getting all article view history."""
        mock_uow.article_view_history.get_all.return_value = ([], 0)

        result = await get_article_view_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            article_id=None,
            user_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert result.total == 0
        assert len(result.items) == 0
        mock_uow.article_view_history.get_all.assert_called_once()

    async def test_get_view_history_by_article_id(self, mock_uow, mock_hr_user, mock_article_view_history):
        """Test getting view history for specific article."""
        mock_uow.article_view_history.get_by_article_id.return_value = [mock_article_view_history]

        result = await get_article_view_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            article_id=1,
            user_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].id == 1
        assert result.items[0].article_id == 1
        assert result.items[0].user_id == 1
        mock_uow.article_view_history.get_by_article_id.assert_called_once_with(
            article_id=1, from_date=None, to_date=None
        )

    async def test_get_view_history_by_user_id(self, mock_uow, mock_hr_user, mock_article_view_history):
        """Test getting view history for specific user."""
        mock_uow.article_view_history.get_by_user_id.return_value = [mock_article_view_history]

        result = await get_article_view_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            article_id=None,
            user_id=1,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].id == 1
        assert result.items[0].user_id == 1
        mock_uow.article_view_history.get_by_user_id.assert_called_once_with(user_id=1, from_date=None, to_date=None)

    async def test_get_view_history_with_date_filters(self, mock_uow, mock_hr_user):
        """Test getting view history with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_uow.article_view_history.get_all.return_value = ([], 0)

        result = await get_article_view_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            article_id=None,
            user_id=None,
            from_date=from_date,
            to_date=to_date,
            limit=50,
            offset=0,
        )

        mock_uow.article_view_history.get_all.assert_called_once_with(
            from_date=from_date, to_date=to_date, limit=50, offset=0
        )

    async def test_regular_user_denied(self, mock_uow, mock_regular_user):
        """Test regular user is denied access."""
        with pytest.raises(PermissionError):
            await get_article_view_history(
                current_user=mock_regular_user,
                uow=mock_uow,
                article_id=None,
                user_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )


class TestGetCategoryChangeHistory:
    """Test category change history endpoint."""

    async def test_get_all_category_history(self, mock_uow, mock_hr_user):
        """Test getting all category change history."""
        mock_uow.category_change_history.get_all.return_value = ([], 0)

        result = await get_category_change_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            category_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert result.total == 0
        assert len(result.items) == 0
        mock_uow.category_change_history.get_all.assert_called_once()

    async def test_get_category_history_by_id(self, mock_uow, mock_hr_user, mock_category_change_history):
        """Test getting history for specific category."""
        mock_uow.category_change_history.get_by_category_id.return_value = [mock_category_change_history]

        result = await get_category_change_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            category_id=1,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].id == 1
        assert result.items[0].category_id == 1
        assert result.items[0].action == "created"
        mock_uow.category_change_history.get_by_category_id.assert_called_once_with(
            category_id=1, from_date=None, to_date=None
        )

    async def test_get_category_history_with_date_filters(self, mock_uow, mock_hr_user):
        """Test getting category history with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_uow.category_change_history.get_all.return_value = ([], 0)

        result = await get_category_change_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            category_id=None,
            from_date=from_date,
            to_date=to_date,
            limit=50,
            offset=0,
        )

        mock_uow.category_change_history.get_all.assert_called_once_with(
            from_date=from_date, to_date=to_date, limit=50, offset=0
        )

    async def test_regular_user_denied(self, mock_uow, mock_regular_user):
        """Test regular user is denied access."""
        with pytest.raises(PermissionError):
            await get_category_change_history(
                current_user=mock_regular_user,
                uow=mock_uow,
                category_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )


class TestGetDialogueScenarioChangeHistory:
    """Test dialogue scenario change history endpoint."""

    async def test_get_all_scenario_history(self, mock_uow, mock_hr_user):
        """Test getting all dialogue scenario change history."""
        mock_uow.dialogue_scenario_change_history.get_all.return_value = ([], 0)

        result = await get_dialogue_scenario_change_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            scenario_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert result.total == 0
        assert len(result.items) == 0
        mock_uow.dialogue_scenario_change_history.get_all.assert_called_once()

    async def test_get_scenario_history_by_id(self, mock_uow, mock_hr_user, mock_dialogue_scenario_change_history):
        """Test getting history for specific scenario."""
        mock_uow.dialogue_scenario_change_history.get_by_scenario_id.return_value = [
            mock_dialogue_scenario_change_history
        ]

        result = await get_dialogue_scenario_change_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            scenario_id=1,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].id == 1
        assert result.items[0].scenario_id == 1
        assert result.items[0].action == "created"
        mock_uow.dialogue_scenario_change_history.get_by_scenario_id.assert_called_once_with(
            scenario_id=1, from_date=None, to_date=None
        )

    async def test_get_scenario_history_with_date_filters(self, mock_uow, mock_hr_user):
        """Test getting scenario history with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_uow.dialogue_scenario_change_history.get_all.return_value = ([], 0)

        result = await get_dialogue_scenario_change_history(
            current_user=mock_hr_user,
            uow=mock_uow,
            scenario_id=None,
            from_date=from_date,
            to_date=to_date,
            limit=50,
            offset=0,
        )

        mock_uow.dialogue_scenario_change_history.get_all.assert_called_once_with(
            from_date=from_date, to_date=to_date, limit=50, offset=0
        )

    async def test_regular_user_denied(self, mock_uow, mock_regular_user):
        """Test regular user is denied access."""
        with pytest.raises(PermissionError):
            await get_dialogue_scenario_change_history(
                current_user=mock_regular_user,
                uow=mock_uow,
                scenario_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )
