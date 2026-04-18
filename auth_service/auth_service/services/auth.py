"""Authentication service with repository pattern."""

from datetime import UTC, datetime, timedelta

from auth_service.config import settings
from auth_service.core import (
    AuthException,
    ConflictException,
    NotFoundException,
    ValidationException,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from auth_service.models import User, UserMentor
from auth_service.repositories.unit_of_work import IUnitOfWork
from auth_service.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TelegramAuthRequest,
    TelegramRegistrationRequest,
    Token,
)
from auth_service.utils.integrations import checklists_service_client


class AuthService:
    """Service for authentication operations with repository pattern."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize authentication service with database session."""
        self._uow = uow

    async def authenticate_user(self, login_data: LoginRequest) -> tuple[User, Token]:
        """Authenticate user with email and password."""
        # Find user by email
        user = await self._uow.users.get_by_email(login_data.email)

        if not user:
            msg = "Invalid email or password"
            raise AuthException(msg)

        if not user.is_active:
            msg = "User account is disabled"
            raise AuthException(msg)

        # Verify password
        if not user.password_hash or not verify_password(login_data.password, user.password_hash):
            msg = "Invalid email or password"
            raise AuthException(msg)

        # Update last login
        await self._uow.users.update_last_login(user.id, datetime.now(UTC))

        # Generate tokens
        token = self.create_token_for_user(user)
        return user, token

    async def refresh_access_token(self, refresh_data: RefreshTokenRequest) -> Token:
        """Refresh access token using refresh token."""
        try:
            payload = decode_token(refresh_data.refresh_token)
        except Exception as e:
            msg = "Invalid refresh token"
            raise AuthException(msg) from e

        # Verify token type
        if payload.get("type") != "refresh":
            msg = "Invalid token type"
            raise AuthException(msg)

        # Get user
        user = await self._uow.users.get_by_id(payload["user_id"])
        if not user or not user.is_active:
            msg = "User not found or inactive"
            raise AuthException(msg)

        # Generate new token
        return self.create_token_for_user(user)

    async def authenticate_with_telegram(self, telegram_data: TelegramAuthRequest) -> tuple[User, Token]:
        """Authenticate user with Telegram data."""
        # Find user by Telegram ID
        user = await self._uow.users.get_by_telegram_id(telegram_data.telegram_id)

        if not user:
            msg = "User"
            raise NotFoundException(msg)

        if not user.is_active:
            msg = "User account is disabled"
            raise AuthException(msg)

        # Update Telegram profile data if provided
        if telegram_data.username:
            user.username = telegram_data.username
        if telegram_data.first_name:
            user.first_name = telegram_data.first_name
        if telegram_data.last_name:
            user.last_name = telegram_data.last_name

        # Update last login
        user.last_login_at = datetime.now(UTC)

        await self._uow.users.update(user)

        return user, self.create_token_for_user(user)

    async def register_with_invitation_and_telegram(
        self, invitation_token: str, telegram_data: TelegramRegistrationRequest
    ) -> User:
        """Register new user using invitation token with Telegram data."""
        # Find valid invitation
        invitation = await self._uow.invitations.get_valid_by_token(invitation_token)
        if not invitation:
            msg = "Invalid or expired invitation"
            raise ValidationException(msg)

        # Check if user already exists
        existing_user = await self._uow.users.get_by_email(invitation.email)
        if existing_user:
            msg = "User already exists"
            raise ConflictException(msg)

        # Check if telegram_id is already linked
        existing_telegram_user = await self._uow.users.get_by_telegram_id(telegram_data.telegram_id)
        if existing_telegram_user:
            msg = "Telegram account already linked to another user"
            raise ConflictException(msg)

        # Create new user
        user = User(
            email=invitation.email,
            first_name=invitation.first_name or telegram_data.first_name or "Unknown",
            last_name=invitation.last_name or telegram_data.last_name,
            phone=telegram_data.phone,
            employee_id=invitation.employee_id,
            department_id=invitation.department_id,
            position=invitation.position,
            level=invitation.level,
            role=invitation.role,
            telegram_id=telegram_data.telegram_id,
            username=telegram_data.username,
            password_hash=None,  # Telegram users don't have password
            hire_date=datetime.now(UTC),
            is_verified=True,
        )

        # Save user and update invitation
        created_user = await self._uow.users.create(user)
        await self._uow.invitations.mark_as_used(invitation.id, created_user.id)

        # Create user-mentor relation if mentor was specified in invitation
        if invitation.mentor_id:
            user_mentor = UserMentor(
                user_id=created_user.id,
                mentor_id=invitation.mentor_id,
                is_active=True,
            )
            await self._uow.user_mentors.create(user_mentor)

        return created_user

    async def auto_create_user_checklists(self, user: User) -> None:
        """
        Auto-create checklists for a user from matching templates.

        Calls the checklists service to create checklists based on the user's
        department and position, with their assigned mentor if any.
        """
        if not user.department_id and not user.position:
            return

        # Find the user's active mentor
        mentor_relation = await self._uow.user_mentors.get_active_by_user_id(user.id)
        mentor_id = mentor_relation.mentor_id if mentor_relation else None

        await checklists_service_client.auto_create_checklists(
            user_id=user.id,
            employee_id=user.employee_id,
            department_id=user.department_id,
            position=user.position,
            mentor_id=mentor_id,
        )

    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token."""
        payload = decode_token(token)

        user = await self._uow.users.get_by_id(payload["user_id"])
        if not user:
            msg = "User not found"
            raise AuthException(msg)

        if not user.is_active:
            msg = "User account is disabled"
            raise AuthException(msg)

        return user

    def create_token_for_user(self, user: User) -> Token:
        """Create Token schema for a user."""
        token_data = {
            "sub": str(user.id),
            "user_id": user.id,
            "role": user.role,
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            user_id=user.id,
            role=user.role,
        )
