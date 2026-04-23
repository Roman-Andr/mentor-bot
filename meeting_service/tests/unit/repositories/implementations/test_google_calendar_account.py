"""Unit tests for SQLAlchemyGoogleCalendarAccountRepository."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.models.google_calendar_account import GoogleCalendarAccount
from meeting_service.repositories.implementations.google_calendar_account import (
    SQLAlchemyGoogleCalendarAccountRepository,
)


@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Create a repository instance with mock session."""
    return SQLAlchemyGoogleCalendarAccountRepository(mock_session)


@pytest.fixture
def sample_account():
    """Create a sample Google Calendar account for testing."""
    return GoogleCalendarAccount(
        id=1,
        user_id=100,
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_expiry=datetime(2024, 12, 31, 23, 59, 59, tzinfo=UTC),
        calendar_id="primary",
        sync_enabled=True,
    )


class TestGetByUserId:
    """Tests for get_by_user_id method."""

    @pytest.mark.asyncio
    async def test_get_by_user_id_found(self, mock_session, repository, sample_account):
        """Test get_by_user_id returns account when found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_account
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_user_id(100)

        # Assert
        assert result == sample_account
        assert result.user_id == 100
        assert result.access_token == "test_access_token"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_user_id_not_found(self, mock_session, repository):
        """Test get_by_user_id returns None when account not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_user_id(999)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_user_id_zero_user_id(self, mock_session, repository):
        """Test get_by_user_id with user_id of 0."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_user_id(0)

        # Assert
        assert result is None


class TestGetByAccountEmail:
    """Tests for get_by_account_email method."""

    @pytest.mark.asyncio
    async def test_get_by_account_email_found(self, mock_session, repository, sample_account):
        """Test get_by_account_email returns account when found."""
        # Arrange - simulate the model having an account_email field
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_account
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_account_email("user@example.com")

        # Assert
        assert result == sample_account

    @pytest.mark.asyncio
    async def test_get_by_account_email_not_found(self, mock_session, repository):
        """Test get_by_account_email returns None when account not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_account_email("nonexistent@example.com")

        # Assert
        assert result is None


class TestGetActiveAccounts:
    """Tests for get_active_accounts method."""

    @pytest.mark.asyncio
    async def test_get_active_accounts_returns_list(self, mock_session, repository, sample_account):
        """Test get_active_accounts returns list of active accounts."""
        # Arrange
        accounts = [sample_account, GoogleCalendarAccount(id=2, user_id=101, access_token="token2")]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = accounts
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_active_accounts()

        # Assert
        assert len(result) == 2
        assert result[0].user_id == 100
        assert result[1].user_id == 101

    @pytest.mark.asyncio
    async def test_get_active_accounts_empty(self, mock_session, repository):
        """Test get_active_accounts returns empty list when no active accounts."""
        # Arrange
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_active_accounts()

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_active_accounts_with_limit(self, mock_session, repository, sample_account):
        """Test get_active_accounts with limit parameter."""
        # Arrange
        accounts = [sample_account]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = accounts
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_active_accounts(limit=1)

        # Assert
        assert len(result) == 1


class TestUpdateTokens:
    """Tests for update_tokens method."""

    @pytest.mark.asyncio
    async def test_update_tokens_success(self, mock_session, repository, sample_account):
        """Test update_tokens updates access token and refresh token."""
        # Arrange
        new_access_token = "new_access_token"
        new_refresh_token = "new_refresh_token"
        new_expiry = datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)

        # Act
        result = await repository.update_tokens(
            sample_account,
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_expiry=new_expiry,
        )

        # Assert
        assert result.access_token == new_access_token
        assert result.refresh_token == new_refresh_token
        assert result.token_expiry == new_expiry
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_account)

    @pytest.mark.asyncio
    async def test_update_tokens_only_access_token(self, mock_session, repository, sample_account):
        """Test update_tokens with only access token."""
        # Arrange
        original_refresh = sample_account.refresh_token
        original_expiry = sample_account.token_expiry
        new_access_token = "updated_access_token"

        # Act
        result = await repository.update_tokens(
            sample_account,
            access_token=new_access_token,
        )

        # Assert
        assert result.access_token == new_access_token
        assert result.refresh_token == original_refresh
        assert result.token_expiry == original_expiry


class TestMarkInactive:
    """Tests for mark_inactive method."""

    @pytest.mark.asyncio
    async def test_mark_inactive_success(self, mock_session, repository, sample_account):
        """Test mark_inactive disables sync for account."""
        # Arrange
        assert sample_account.sync_enabled is True

        # Act
        result = await repository.mark_inactive(sample_account)

        # Assert
        assert result.sync_enabled is False
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_account)

    @pytest.mark.asyncio
    async def test_mark_inactive_already_inactive(self, mock_session, repository):
        """Test mark_inactive on already inactive account."""
        # Arrange
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="token",
            sync_enabled=False,  # Already inactive
        )

        # Act
        result = await repository.mark_inactive(account)

        # Assert
        assert result.sync_enabled is False
        mock_session.commit.assert_called_once()


class TestCreate:
    """Tests for create method."""

    @pytest.mark.asyncio
    async def test_create_adds_account(self, mock_session, repository, sample_account):
        """Test create adds account to session and commits."""
        # Act
        result = await repository.create(sample_account)

        # Assert
        assert result == sample_account
        mock_session.add.assert_called_once_with(sample_account)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_account)

    @pytest.mark.asyncio
    async def test_create_without_refresh_token(self, mock_session, repository):
        """Test create with account that has no refresh token."""
        # Arrange
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="access_token_only",
            refresh_token=None,
        )

        # Act
        result = await repository.create(account)

        # Assert
        assert result.refresh_token is None
        mock_session.add.assert_called_once_with(account)


class TestUpdate:
    """Tests for update method."""

    @pytest.mark.asyncio
    async def test_update_commits_changes(self, mock_session, repository, sample_account):
        """Test update commits and refreshes account."""
        # Modify the account
        sample_account.calendar_id = "custom_calendar_id"

        # Act
        result = await repository.update(sample_account)

        # Assert
        assert result == sample_account
        assert result.calendar_id == "custom_calendar_id"
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_account)


class TestDelete:
    """Tests for delete method."""

    @pytest.mark.asyncio
    async def test_delete_existing_account(self, mock_session, repository, sample_account):
        """Test delete removes account by user_id."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_account
        mock_session.execute.return_value = mock_result

        # Act
        await repository.delete(100)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.delete.assert_called_once_with(sample_account)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_session, repository):
        """Test delete when account not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        await repository.delete(999)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()


class TestRepositoryInitialization:
    """Tests for repository initialization."""

    def test_repository_stores_session(self, mock_session):
        """Test repository stores session reference."""
        repo = SQLAlchemyGoogleCalendarAccountRepository(mock_session)
        assert repo._session == mock_session


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_get_by_user_id_negative_id(self, mock_session, repository):
        """Test get_by_user_id with negative user_id."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_user_id(-1)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_zero_user_id(self, mock_session, repository):
        """Test delete with user_id of 0."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        await repository.delete(0)

        # Assert
        mock_session.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_tokens_none_values(self, mock_session, repository, sample_account):
        """Test update_tokens with None values preserves existing tokens."""
        # Arrange
        original_refresh = sample_account.refresh_token
        original_expiry = sample_account.token_expiry

        # Act - passing None for refresh_token and token_expiry should preserve existing values
        result = await repository.update_tokens(
            sample_account,
            access_token="new_token",
            refresh_token=None,
            token_expiry=None,
        )

        # Assert - None values should preserve original values (not set to None)
        assert result.access_token == "new_token"
        assert result.refresh_token == original_refresh
        assert result.token_expiry == original_expiry

    @pytest.mark.asyncio
    async def test_create_with_expired_token(self, mock_session, repository):
        """Test create with expired token date."""
        # Arrange
        expired_account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="expired_token",
            token_expiry=datetime(2020, 1, 1, tzinfo=UTC),  # Past date
        )

        # Act
        result = await repository.create(expired_account)

        # Assert
        assert result.token_expiry.year == 2020
