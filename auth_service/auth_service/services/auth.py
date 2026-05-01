"""Authentication service with repository pattern."""

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Request
from loguru import logger

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
from auth_service.models import LoginHistory, RoleChangeHistory, User, UserMentor
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

    async def authenticate_user(
        self, login_data: LoginRequest, request: Request | None = None
    ) -> tuple[User, Token]:
        """Authenticate user with email and password."""
        logger.debug("Authenticating user by email: {}", login_data.email)
        # Find user by email
        user = await self._uow.users.get_by_email(login_data.email)

        if not user:
            # Record failed login attempt
            await self._record_login(
                user_id=0,  # Unknown user
                success=False,
                failure_reason="User not found",
                method="password",
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent") if request else None,
            )
            logger.warning("Authentication failed: user not found for email={}", login_data.email)
            msg = "Invalid email or password"
            raise AuthException(msg)

        if not user.is_active:
            # Record failed login attempt
            await self._record_login(
                user_id=user.id,
                success=False,
                failure_reason="User account is disabled",
                method="password",
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent") if request else None,
            )
            logger.warning("Authentication failed: user is disabled (user_id={})", user.id)
            msg = "User account is disabled"
            raise AuthException(msg)

        # Verify password
        if not user.password_hash or not verify_password(login_data.password, user.password_hash):
            # Record failed login attempt
            await self._record_login(
                user_id=user.id,
                success=False,
                failure_reason="Invalid password",
                method="password",
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent") if request else None,
            )
            logger.warning("Authentication failed: invalid password (user_id={})", user.id)
            msg = "Invalid email or password"
            raise AuthException(msg)

        # Update last login
        await self._uow.users.update_last_login(user.id, datetime.now(UTC))

        # Record successful login
        await self._record_login(
            user_id=user.id,
            success=True,
            method="password",
            ip_address=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent") if request else None,
        )

        # Generate tokens
        token = self.create_token_for_user(user)
        logger.info("User authenticated successfully (user_id={}, role={})", user.id, user.role)
        return user, token

    async def refresh_access_token(self, refresh_data: RefreshTokenRequest) -> Token:
        """Refresh access token using refresh token."""
        logger.debug("Refresh token requested")
        try:
            payload = decode_token(refresh_data.refresh_token, expected_type="refresh")
        except HTTPException as e:
            logger.warning("Refresh token decode failed: {}", e.detail)
            msg = e.detail or "Invalid refresh token"
            raise AuthException(msg) from e

        # Get user
        user = await self._uow.users.get_by_id(payload["user_id"])
        if not user or not user.is_active:
            logger.warning(
                "Refresh failed: user not found or inactive (user_id={})", payload.get("user_id")
            )
            msg = "User not found or inactive"
            raise AuthException(msg)

        # Generate new token
        logger.info("Access token refreshed (user_id={})", user.id)
        return self.create_token_for_user(user)

    async def authenticate_with_telegram(
        self, telegram_data: TelegramAuthRequest, request: Request | None = None
    ) -> tuple[User, Token]:
        """Authenticate user with Telegram data."""
        logger.debug("Authenticating via Telegram (telegram_id={})", telegram_data.telegram_id)
        # Find user by Telegram ID
        user = await self._uow.users.get_by_telegram_id(telegram_data.telegram_id)

        if not user:
            # Record failed login attempt
            await self._record_login(
                user_id=0,  # Unknown user
                success=False,
                failure_reason="User not found",
                method="telegram",
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent") if request else None,
            )
            logger.warning(
                "Telegram authentication failed: no user for telegram_id={}",
                telegram_data.telegram_id,
            )
            msg = "User"
            raise NotFoundException(msg)

        if not user.is_active:
            # Record failed login attempt
            await self._record_login(
                user_id=user.id,
                success=False,
                failure_reason="User account is disabled",
                method="telegram",
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent") if request else None,
            )
            logger.warning("Telegram authentication failed: user is disabled (user_id={})", user.id)
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

        # Record successful login
        await self._record_login(
            user_id=user.id,
            success=True,
            method="telegram",
            ip_address=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent") if request else None,
        )

        logger.info(
            "Telegram authentication successful (user_id={}, telegram_id={})",
            user.id,
            user.telegram_id,
        )
        return user, self.create_token_for_user(user)

    async def register_with_invitation_and_telegram(
        self, invitation_token: str, telegram_data: TelegramRegistrationRequest
    ) -> User:
        """Register new user using invitation token with Telegram data."""
        logger.debug(
            "Registering via invitation (telegram_id={})", telegram_data.telegram_id
        )
        # Find valid invitation
        invitation = await self._uow.invitations.get_valid_by_token(invitation_token)
        if not invitation:
            logger.warning("Registration failed: invalid or expired invitation token")
            msg = "Invalid or expired invitation"
            raise ValidationException(msg)

        # Check if user already exists
        existing_user = await self._uow.users.get_by_email(invitation.email)
        if existing_user:
            logger.warning(
                "Registration conflict: email already registered (email={})",
                invitation.email,
            )
            msg = "User already exists"
            raise ConflictException(msg)

        # Check if telegram_id is already linked
        existing_telegram_user = await self._uow.users.get_by_telegram_id(telegram_data.telegram_id)
        if existing_telegram_user:
            logger.warning(
                "Registration conflict: telegram_id already linked (telegram_id={}, user_id={})",
                telegram_data.telegram_id,
                existing_telegram_user.id,
            )
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
            logger.info(
                "Mentor relation created during registration (user_id={}, mentor_id={})",
                created_user.id,
                invitation.mentor_id,
            )

        logger.info(
            "User registered via invitation (user_id={}, invitation_id={}, role={})",
            created_user.id,
            invitation.id,
            created_user.role,
        )
        return created_user

    async def auto_create_user_checklists(self, user: User) -> None:
        """
        Auto-create checklists for a user from matching templates.

        Calls the checklists service to create checklists based on the user's
        department and position, with their assigned mentor if any.
        """
        if not user.department_id and not user.position:
            logger.debug(
                "Skipping auto-create checklists: no department/position (user_id={})", user.id
            )
            return

        # Find the user's active mentor
        mentor_relation = await self._uow.user_mentors.get_active_by_user_id(user.id)
        mentor_id = mentor_relation.mentor_id if mentor_relation else None

        logger.info(
            "Auto-creating checklists (user_id={}, department_id={}, position={}, mentor_id={})",
            user.id,
            user.department_id,
            user.position,
            mentor_id,
        )
        await checklists_service_client.auto_create_checklists(
            user_id=user.id,
            employee_id=user.employee_id,
            department_id=user.department_id,
            position=user.position,
            mentor_id=mentor_id,
        )

    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token."""
        payload = decode_token(token, expected_type="access")

        user = await self._uow.users.get_by_id(payload["user_id"])
        if not user:
            logger.warning(
                "Current user lookup failed: user not found (user_id={})",
                payload.get("user_id"),
            )
            msg = "User not found"
            raise AuthException(msg)

        if not user.is_active:
            logger.warning(
                "Current user lookup failed: user is disabled (user_id={})", user.id
            )
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

    async def _record_login(
        self,
        user_id: int,
        success: bool,
        method: str,
        failure_reason: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Record login attempt to audit log."""
        login_history = LoginHistory(
            user_id=user_id,
            success=success,
            method=method,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self._uow.login_history.create(login_history)

    def _get_client_ip(self, request: Request | None) -> str | None:
        """Extract client IP address from request."""
        if not request:
            return None
        # Check for forwarded headers (proxy/load balancer)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else None

    async def record_role_change(
        self,
        user_id: int,
        old_role: str | None,
        new_role: str,
        changed_by: int | None = None,
        reason: str | None = None,
    ) -> None:
        """Record role change to audit log."""
        role_change = RoleChangeHistory(
            user_id=user_id,
            old_role=old_role,
            new_role=new_role,
            changed_by=changed_by,
            reason=reason,
        )
        await self._uow.role_change_history.create(role_change)
