"""Tests for API dependencies (api/deps.py)."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from knowledge_service.api.deps import (
    AdminUser,
    ArticleServiceDep,
    AttachmentServiceDep,
    AuthToken,
    CategoryServiceDep,
    CurrentUser,
    DialogueServiceDep,
    HRUser,
    KnowledgeServiceDep,
    MentorUser,
    SearchServiceDep,
    ServiceAuth,
    TagServiceDep,
    UserInfo,
    get_article_service,
    get_attachment_service,
    get_auth_token,
    get_category_service,
    get_current_active_user,
    get_current_user,
    get_dialogue_service,
    get_knowledge_service_dep,
    get_search_service,
    get_tag_service,
    get_uow,
    require_admin,
    require_hr,
    require_mentor_or_above,
    verify_service_api_key,
)
from knowledge_service.core import AuthException, PermissionDenied
from knowledge_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from knowledge_service.services import (
    ArticleService,
    AttachmentService,
    CategoryService,
    DialogueService,
    SearchService,
    TagService,
)


class TestUserInfo:
    """Test UserInfo class."""

    def test_user_info_initialization(self) -> None:
        """Test UserInfo initialization with complete data."""
        data = {
            "id": 1,
            "email": "user@example.com",
            "employee_id": "EMP001",
            "role": "MENTEE",
            "is_active": True,
            "is_verified": True,
            "department": {"id": 1, "name": "Engineering"},
            "position": "Developer",
            "level": "JUNIOR",
            "first_name": "John",
            "last_name": "Doe",
            "telegram_id": "123456",
        }
        user = UserInfo(data)

        assert user.id == 1
        assert user.email == "user@example.com"
        assert user.employee_id == "EMP001"
        assert user.role == "MENTEE"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.department == {"id": 1, "name": "Engineering"}
        assert user.department_id == 1
        assert user.position == "Developer"
        assert user.level == "JUNIOR"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.telegram_id == "123456"

    def test_user_info_no_department(self) -> None:
        """Test UserInfo with no department."""
        data = {
            "id": 1,
            "email": "user@example.com",
            "role": "MENTEE",
        }
        user = UserInfo(data)

        assert user.department is None
        assert user.department_id is None

    def test_user_info_defaults(self) -> None:
        """Test UserInfo default values."""
        data = {"id": 1, "email": "user@example.com"}
        user = UserInfo(data)

        assert user.is_active is True
        assert user.is_verified is False

    def test_has_role_with_matching_role(self) -> None:
        """Test has_role with matching role."""
        data = {"id": 1, "email": "user@example.com", "role": "ADMIN"}
        user = UserInfo(data)

        assert user.has_role(["ADMIN", "HR"]) is True

    def test_has_role_without_matching_role(self) -> None:
        """Test has_role without matching role."""
        data = {"id": 1, "email": "user@example.com", "role": "MENTEE"}
        user = UserInfo(data)

        assert user.has_role(["ADMIN", "HR"]) is False

    def test_has_role_with_none_role(self) -> None:
        """Test has_role when role is None."""
        data = {"id": 1, "email": "user@example.com", "role": None}
        user = UserInfo(data)

        assert user.has_role(["ADMIN"]) is False


class TestGetCurrentUser:
    """Test get_current_user dependency."""

    async def test_get_current_user_no_credentials(self) -> None:
        """Test get_current_user with no credentials raises AuthException."""
        mock_request = MagicMock(spec=Request)

        with pytest.raises(AuthException) as exc_info:
            await get_current_user(mock_request, None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in str(exc_info.value.detail)

    @patch("knowledge_service.api.deps.auth_service_circuit_breaker")
    @patch("knowledge_service.api.deps.httpx.AsyncClient")
    async def test_get_current_user_success(
        self,
        mock_client_class: Mock,
        mock_circuit_breaker: Mock,
    ) -> None:
        """Test successful authentication."""
        mock_request = MagicMock(spec=Request)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {
            "id": 1,
            "email": "user@example.com",
            "role": "MENTEE",
        }

        # Setup async context manager for client
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        # Setup circuit breaker to just call the function
        async def mock_call(func):
            return await func()

        mock_circuit_breaker.call = mock_call

        result = await get_current_user(mock_request, credentials)

        assert isinstance(result, UserInfo)
        assert result.id == 1
        assert result.email == "user@example.com"

    @patch("knowledge_service.api.deps.auth_service_circuit_breaker")
    @patch("knowledge_service.api.deps.httpx.AsyncClient")
    async def test_get_current_user_invalid_credentials(
        self,
        mock_client_class: Mock,
        mock_circuit_breaker: Mock,
    ) -> None:
        """Test authentication with invalid credentials."""
        mock_request = MagicMock(spec=Request)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_401_UNAUTHORIZED

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        async def mock_call(func):
            return await func()

        mock_circuit_breaker.call = mock_call

        with pytest.raises(AuthException) as exc_info:
            await get_current_user(mock_request, credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("knowledge_service.api.deps.auth_service_circuit_breaker")
    @patch("knowledge_service.api.deps.httpx.AsyncClient")
    async def test_get_current_user_circuit_breaker_open(
        self,
        mock_client_class: Mock,
        mock_circuit_breaker: Mock,
    ) -> None:
        """Test authentication when circuit breaker is open."""
        mock_request = MagicMock(spec=Request)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        async def mock_call(func):
            raise Exception("Circuit breaker is OPEN")

        mock_circuit_breaker.call = mock_call

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_request, credentials)

        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Auth service temporarily unavailable" in exc_info.value.detail

    @patch("knowledge_service.api.deps.auth_service_circuit_breaker")
    @patch("knowledge_service.api.deps.httpx.AsyncClient")
    async def test_get_current_user_exception(
        self,
        mock_client_class: Mock,
        mock_circuit_breaker: Mock,
    ) -> None:
        """Test authentication with generic exception."""
        mock_request = MagicMock(spec=Request)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        async def mock_call(func):
            raise Exception("Network error")

        mock_circuit_breaker.call = mock_call

        with pytest.raises(AuthException) as exc_info:
            await get_current_user(mock_request, credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentActiveUser:
    """Test get_current_active_user dependency."""

    async def test_get_current_active_user_success(self, mock_user: UserInfo) -> None:
        """Test getting active user."""
        result = await get_current_active_user(mock_user)

        assert result == mock_user
        assert result.is_active is True

    async def test_get_current_active_user_inactive(self) -> None:
        """Test getting inactive user raises exception."""
        inactive_user = UserInfo({
            "id": 1,
            "email": "inactive@example.com",
            "role": "MENTEE",
            "is_active": False,
        })

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(inactive_user)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Inactive user" in exc_info.value.detail


class TestRequireAdmin:
    """Test require_admin dependency."""

    async def test_require_admin_success(self, mock_admin_user: UserInfo) -> None:
        """Test admin requirement with admin user."""
        result = await require_admin(mock_admin_user)

        assert result == mock_admin_user

    async def test_require_admin_as_hr(self, mock_hr_user: UserInfo) -> None:
        """Test admin requirement with HR user (also allowed)."""
        result = await require_admin(mock_hr_user)

        assert result == mock_hr_user

    async def test_require_admin_as_regular_user(self, mock_user: UserInfo) -> None:
        """Test admin requirement with regular user raises PermissionDenied."""
        with pytest.raises(PermissionDenied) as exc_info:
            await require_admin(mock_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in str(exc_info.value.detail)


class TestRequireHR:
    """Test require_hr dependency."""

    async def test_require_hr_success(self, mock_hr_user: UserInfo) -> None:
        """Test HR requirement with HR user."""
        result = await require_hr(mock_hr_user)

        assert result == mock_hr_user

    async def test_require_hr_as_admin(self, mock_admin_user: UserInfo) -> None:
        """Test HR requirement with admin user (also allowed)."""
        result = await require_hr(mock_admin_user)

        assert result == mock_admin_user

    async def test_require_hr_as_regular_user(self, mock_user: UserInfo) -> None:
        """Test HR requirement with regular user raises PermissionDenied."""
        with pytest.raises(PermissionDenied) as exc_info:
            await require_hr(mock_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "HR access required" in str(exc_info.value.detail)


class TestRequireMentorOrAbove:
    """Test require_mentor_or_above dependency."""

    async def test_require_mentor_as_mentor(self) -> None:
        """Test mentor requirement with mentor user."""
        mentor_user = UserInfo({
            "id": 1,
            "email": "mentor@example.com",
            "role": "MENTOR",
            "is_active": True,
        })

        result = await require_mentor_or_above(mentor_user)
        assert result == mentor_user

    async def test_require_mentor_as_hr(self, mock_hr_user: UserInfo) -> None:
        """Test mentor requirement with HR user."""
        result = await require_mentor_or_above(mock_hr_user)
        assert result == mock_hr_user

    async def test_require_mentor_as_admin(self, mock_admin_user: UserInfo) -> None:
        """Test mentor requirement with admin user."""
        result = await require_mentor_or_above(mock_admin_user)
        assert result == mock_admin_user

    async def test_require_mentor_as_mentee(self, mock_user: UserInfo) -> None:
        """Test mentor requirement with mentee raises PermissionDenied."""
        with pytest.raises(PermissionDenied) as exc_info:
            await require_mentor_or_above(mock_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Mentor access required" in str(exc_info.value.detail)


class TestGetAuthToken:
    """Test get_auth_token dependency."""

    async def test_get_auth_token_from_request(self) -> None:
        """Test getting auth token from request state."""
        mock_request = MagicMock(spec=Request)
        mock_request.state.auth_token = "test_token_123"

        result = await get_auth_token(mock_request)

        assert result == "test_token_123"

    async def test_get_auth_token_not_set(self) -> None:
        """Test getting auth token when not set returns None."""
        mock_request = MagicMock(spec=Request)
        # Explicitly set side_effect for missing attributes to return None
        type(mock_request).state = MagicMock(spec_set=[])

        result = await get_auth_token(mock_request)

        assert result is None


class TestVerifyServiceApiKey:
    """Test verify_service_api_key dependency."""

    @patch("knowledge_service.api.deps.settings")
    async def test_verify_service_api_key_success(self, mock_settings: Mock) -> None:
        """Test successful service API key verification."""
        mock_settings.SERVICE_API_KEY = "valid_service_key"

        result = await verify_service_api_key("valid_service_key")

        assert result is True

    @patch("knowledge_service.api.deps.settings")
    async def test_verify_service_api_key_no_key_configured(self, mock_settings: Mock) -> None:
        """Test when SERVICE_API_KEY is not configured raises HTTPException."""
        mock_settings.SERVICE_API_KEY = ""

        with pytest.raises(HTTPException) as exc_info:
            await verify_service_api_key("any_key")

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Service API key not configured" in str(exc_info.value.detail)

    @patch("knowledge_service.api.deps.settings")
    async def test_verify_service_api_key_invalid_key(self, mock_settings: Mock) -> None:
        """Test with invalid service API key."""
        mock_settings.SERVICE_API_KEY = "valid_service_key"

        with pytest.raises(HTTPException) as exc_info:
            await verify_service_api_key("invalid_key")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid service API key" in exc_info.value.detail

    @patch("knowledge_service.api.deps.settings")
    async def test_verify_service_api_key_no_header(self, mock_settings: Mock) -> None:
        """Test with missing API key header."""
        mock_settings.SERVICE_API_KEY = "valid_service_key"

        with pytest.raises(HTTPException) as exc_info:
            await verify_service_api_key(None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestServiceAuth:
    """Test ServiceAuth type alias indirectly."""

    async def test_service_auth_type(self) -> None:
        """Test that ServiceAuth type alias exists and can be used."""
        # ServiceAuth is just a type alias, but we can verify it
        assert ServiceAuth is not None


class TestKnowledgeServiceDep:
    """Test KnowledgeServiceDep class."""

    async def test_knowledge_service_dep_class(self) -> None:
        """Test KnowledgeServiceDep marker class."""
        dep = KnowledgeServiceDep()
        assert isinstance(dep, KnowledgeServiceDep)

    async def test_get_knowledge_service_dep(self) -> None:
        """Test get_knowledge_service_dep function."""
        result = await get_knowledge_service_dep()
        assert isinstance(result, KnowledgeServiceDep)


class TestTypeAliases:
    """Test that type aliases are properly defined."""

    def test_current_user_type(self) -> None:
        """Test CurrentUser type alias."""
        assert CurrentUser is not None

    def test_admin_user_type(self) -> None:
        """Test AdminUser type alias."""
        assert AdminUser is not None

    def test_hr_user_type(self) -> None:
        """Test HRUser type alias."""
        assert HRUser is not None

    def test_mentor_user_type(self) -> None:
        """Test MentorUser type alias."""
        assert MentorUser is not None

    def test_auth_token_type(self) -> None:
        """Test AuthToken type alias."""
        assert AuthToken is not None

    def test_uow_dep_type(self) -> None:
        """Test UOWDep type alias - need to import it."""
        from knowledge_service.api.deps import UOWDep
        assert UOWDep is not None

    def test_article_service_dep_type(self) -> None:
        """Test ArticleServiceDep type alias."""
        assert ArticleServiceDep is not None

    def test_category_service_dep_type(self) -> None:
        """Test CategoryServiceDep type alias."""
        assert CategoryServiceDep is not None

    def test_tag_service_dep_type(self) -> None:
        """Test TagServiceDep type alias."""
        assert TagServiceDep is not None

    def test_attachment_service_dep_type(self) -> None:
        """Test AttachmentServiceDep type alias."""
        assert AttachmentServiceDep is not None

    def test_search_service_dep_type(self) -> None:
        """Test SearchServiceDep type alias."""
        assert SearchServiceDep is not None

    def test_dialogue_service_dep_type(self) -> None:
        """Test DialogueServiceDep type alias."""
        assert DialogueServiceDep is not None


class TestGetUow:
    """Test get_uow async generator dependency."""

    @patch("knowledge_service.api.deps.SqlAlchemyUnitOfWork")
    async def test_get_uow_yields_uow(
        self,
        mock_uow_class: Mock,
    ) -> None:
        """Test get_uow yields UnitOfWork."""
        mock_uow = AsyncMock(spec=SqlAlchemyUnitOfWork)
        mock_uow_class.return_value = mock_uow
        mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_uow.__aexit__ = AsyncMock(return_value=None)

        async for uow in get_uow():
            assert uow == mock_uow

        # Commit/rollback are handled by UOW context manager, not the dependency
        mock_uow.commit.assert_not_awaited()
        mock_uow.rollback.assert_not_awaited()

    @patch("knowledge_service.api.deps.SqlAlchemyUnitOfWork")
    async def test_get_uow_context_manager_exit(
        self,
        mock_uow_class: Mock,
    ) -> None:
        """Test get_uow properly exits context manager."""
        mock_uow = AsyncMock(spec=SqlAlchemyUnitOfWork)
        mock_uow_class.return_value = mock_uow
        mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_uow.__aexit__ = AsyncMock(return_value=None)

        async for uow in get_uow():
            assert uow == mock_uow

        # Verify __aexit__ is called when exiting the async context
        mock_uow.__aexit__.assert_awaited_once()


class TestServiceDependencies:
    """Test service dependency functions."""

    async def test_get_article_service(self) -> None:
        """Test get_article_service returns ArticleService."""
        mock_uow = AsyncMock(spec=SqlAlchemyUnitOfWork)

        result = await get_article_service(mock_uow)

        assert isinstance(result, ArticleService)
        assert result._uow == mock_uow

    async def test_get_category_service(self) -> None:
        """Test get_category_service returns CategoryService."""
        mock_uow = AsyncMock(spec=SqlAlchemyUnitOfWork)

        result = await get_category_service(mock_uow)

        assert isinstance(result, CategoryService)
        assert result._uow == mock_uow

    async def test_get_tag_service(self) -> None:
        """Test get_tag_service returns TagService."""
        mock_uow = AsyncMock(spec=SqlAlchemyUnitOfWork)

        result = await get_tag_service(mock_uow)

        assert isinstance(result, TagService)
        assert result._uow == mock_uow

    async def test_get_attachment_service(self) -> None:
        """Test get_attachment_service returns AttachmentService."""
        mock_uow = AsyncMock(spec=SqlAlchemyUnitOfWork)

        result = await get_attachment_service(mock_uow)

        assert isinstance(result, AttachmentService)
        assert result._uow == mock_uow

    async def test_get_search_service(self) -> None:
        """Test get_search_service returns SearchService."""
        mock_uow = AsyncMock(spec=SqlAlchemyUnitOfWork)

        result = await get_search_service(mock_uow)

        assert isinstance(result, SearchService)
        assert result._uow == mock_uow

    async def test_get_dialogue_service(self) -> None:
        """Test get_dialogue_service returns DialogueService."""
        mock_uow = AsyncMock(spec=SqlAlchemyUnitOfWork)

        result = await get_dialogue_service(mock_uow)

        assert isinstance(result, DialogueService)
        assert result._uow == mock_uow
