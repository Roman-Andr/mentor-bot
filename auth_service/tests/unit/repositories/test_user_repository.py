"""Unit tests for User repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.enums import UserRole
from auth_service.models import User
from auth_service.repositories.implementations.user import UserRepository


class TestUserRepository:
    """Tests for UserRepository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        return session

    @pytest.fixture
    def mock_result(self):
        """Create a mock SQLAlchemy result."""
        result = MagicMock()
        result.scalar_one_or_none = MagicMock()
        result.scalar_one = MagicMock()
        result.scalars = MagicMock()
        return result

    @pytest.fixture
    def sample_user(self):
        """Create a sample user."""
        return User(
            id=1,
            email="user@example.com",
            first_name="John",
            last_name="Doe",
            employee_id="EMP001",
            role=UserRole.NEWBIE,
            is_active=True,
            is_verified=True,
            created_at=datetime.now(UTC),
        )

    async def test_get_by_email_success(self, mock_session, mock_result, sample_user):
        """Test getting user by email."""
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_by_email("user@example.com")

        assert result == sample_user
        assert result.email == "user@example.com"

    async def test_get_by_email_not_found(self, mock_session, mock_result):
        """Test getting user by email when not found."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_by_email("nonexistent@example.com")

        assert result is None

    async def test_get_by_telegram_id_success(self, mock_session, mock_result, sample_user):
        """Test getting user by Telegram ID."""
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_by_telegram_id(123456789)

        assert result == sample_user

    async def test_get_by_telegram_id_not_found(self, mock_session, mock_result):
        """Test getting user by Telegram ID when not found."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_by_telegram_id(999999999)

        assert result is None

    async def test_get_by_employee_id_success(self, mock_session, mock_result, sample_user):
        """Test getting user by employee ID."""
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_by_employee_id("EMP001")

        assert result == sample_user
        assert result.employee_id == "EMP001"

    async def test_get_by_employee_id_not_found(self, mock_session, mock_result):
        """Test getting user by employee ID when not found."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_by_employee_id("NONEXISTENT")

        assert result is None

    async def test_create_reloads_with_relations(self, mock_session, mock_result, sample_user):
        """Test that create reloads user with department relationship."""
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()

        repo = UserRepository(mock_session)
        result = await repo.create(sample_user)

        mock_session.add.assert_called_once_with(sample_user)
        mock_session.flush.assert_awaited_once()
        assert result == sample_user

    async def test_update_reloads_with_relations(self, mock_session, mock_result, sample_user):
        """Test that update reloads user with department relationship."""
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()

        repo = UserRepository(mock_session)
        result = await repo.update(sample_user)

        mock_session.flush.assert_awaited_once()
        assert result == sample_user

    async def test_update_last_login_success(self, mock_session, mock_result, sample_user):
        """Test updating user's last login timestamp."""
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()

        repo = UserRepository(mock_session)
        login_time = datetime.now(UTC)
        await repo.update_last_login(1, login_time)

        assert sample_user.last_login_at == login_time
        mock_session.flush.assert_awaited_once()

    async def test_update_last_login_user_not_found(self, mock_session, mock_result):
        """Test updating last login when user not found."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        login_time = datetime.now(UTC)

        # Should not raise error
        await repo.update_last_login(999, login_time)
        mock_session.flush.assert_not_called()

    async def test_update_role_success(self, mock_session, mock_result, sample_user):
        """Test updating user's role."""
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()

        repo = UserRepository(mock_session)
        result = await repo.update_role(1, UserRole.MENTOR)

        assert result.role == UserRole.MENTOR
        mock_session.flush.assert_awaited_once()

    async def test_update_role_user_not_found(self, mock_session, mock_result):
        """Test updating role when user not found."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)

        with pytest.raises(ValueError, match="User with ID 999 not found"):
            await repo.update_role(999, UserRole.MENTOR)

    async def test_deactivate_user_success(self, mock_session, mock_result, sample_user):
        """Test deactivating user account."""
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()

        repo = UserRepository(mock_session)
        result = await repo.deactivate_user(1)

        assert result.is_active is False
        mock_session.flush.assert_awaited_once()

    async def test_deactivate_user_not_found(self, mock_session, mock_result):
        """Test deactivating user when not found."""
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)

        with pytest.raises(ValueError, match="User with ID 999 not found"):
            await repo.deactivate_user(999)

    async def test_find_users_without_filters(self, mock_session, mock_result, sample_user):
        """Test finding users without filters."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_user]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = UserRepository(mock_session)
        users, total = await repo.find_users(skip=0, limit=100)

        assert total == 1
        assert len(users) == 1
        assert users[0].email == "user@example.com"

    async def test_find_users_with_search(self, mock_session, mock_result, sample_user):
        """Test finding users with search filter."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_user]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = UserRepository(mock_session)
        users, total = await repo.find_users(skip=0, limit=100, search="John")

        assert total == 1
        assert len(users) == 1

    async def test_find_users_with_department_filter(self, mock_session, mock_result, sample_user):
        """Test finding users with department filter."""
        sample_user.department_id = 1
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_user]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = UserRepository(mock_session)
        users, total = await repo.find_users(skip=0, limit=100, department_id=1)

        assert total == 1
        assert len(users) == 1

    async def test_find_users_with_role_filter(self, mock_session, mock_result, sample_user):
        """Test finding users with role filter."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_user]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = UserRepository(mock_session)
        users, total = await repo.find_users(skip=0, limit=100, role=UserRole.NEWBIE)

        assert total == 1
        assert len(users) == 1

    async def test_find_users_with_active_filter(self, mock_session, mock_result, sample_user):
        """Test finding users with active filter."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_user]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = UserRepository(mock_session)
        users, total = await repo.find_users(skip=0, limit=100, is_active=True)

        assert total == 1
        assert len(users) == 1

    async def test_find_users_with_ascending_sort(self, mock_session, mock_result, sample_user):
        """Test finding users with ascending sort order (covers line 117)."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_user]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = UserRepository(mock_session)
        # Use sort_order="asc" to cover line 117
        users, total = await repo.find_users(skip=0, limit=100, sort_by="email", sort_order="asc")

        assert total == 1
        assert len(users) == 1

    async def test_find_users_with_descending_sort(self, mock_session, mock_result, sample_user):
        """Test finding users with descending sort order (covers line 119)."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_user]
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = UserRepository(mock_session)
        # Use sort_order="desc" to cover line 119
        users, total = await repo.find_users(skip=0, limit=100, sort_by="email", sort_order="desc")

        assert total == 1
        assert len(users) == 1

    async def test_find_users_empty_result(self, mock_session, mock_result):
        """Test finding users when no results match."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        mock_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, mock_result]

        repo = UserRepository(mock_session)
        users, total = await repo.find_users(skip=0, limit=100, search="XYZ")

        assert total == 0
        assert len(users) == 0

    async def test_get_by_id_reloads_with_relations(self, mock_session, mock_result, sample_user):
        """Test that get_by_id reloads with department and mentor relationships."""
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_by_id(1)

        assert result == sample_user
