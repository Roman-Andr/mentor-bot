"""User management service with repository pattern."""

from datetime import UTC, datetime

from loguru import logger

from auth_service.core import (
    ConflictException,
    NotFoundException,
    UserRole,
    ValidationException,
    hash_password,
    verify_password,
)
from auth_service.models import User
from auth_service.repositories.unit_of_work import IUnitOfWork
from auth_service.schemas import UserCreate, UserPreferencesUpdate, UserUpdate


class UserService:
    """Service for user management operations with repository pattern."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize user service with database session."""
        self._uow = uow

    async def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID."""
        logger.debug("Fetching user by id={}", user_id)
        user = await self._uow.users.get_by_id(user_id)
        if not user:
            logger.warning("User not found (user_id={})", user_id)
            msg = "User"
            raise NotFoundException(msg)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return await self._uow.users.get_by_email(email)

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        return await self._uow.users.get_by_telegram_id(telegram_id)

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user with repository pattern."""
        logger.debug(
            "Creating user (email={}, employee_id={}, role={})",
            user_data.email,
            user_data.employee_id,
            user_data.role,
        )
        # Check if email already exists
        existing_user = await self._uow.users.get_by_email(user_data.email)
        if existing_user:
            logger.warning("Create user conflict: email already registered ({})", user_data.email)
            msg = "Email already registered"
            raise ConflictException(msg)

        # Check if employee_id already exists
        existing_employee = await self._uow.users.get_by_employee_id(user_data.employee_id)
        if existing_employee:
            logger.warning(
                "Create user conflict: employee_id already registered ({})",
                user_data.employee_id,
            )
            msg = "Employee ID already registered"
            raise ConflictException(msg)

        # Check if telegram_id is already linked to another user
        if user_data.telegram_id is not None:
            existing_user = await self._uow.users.get_by_telegram_id(user_data.telegram_id)
            if existing_user:
                logger.warning(
                    "Create user conflict: telegram_id already linked ({})",
                    user_data.telegram_id,
                )
                msg = "Telegram account already linked to another user"
                raise ConflictException(msg)

        # Create user entity
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            employee_id=user_data.employee_id,
            department_id=user_data.department_id,
            position=user_data.position,
            level=user_data.level,
            role=user_data.role,
            password_hash=hash_password(user_data.password),
            hire_date=datetime.now(UTC),
            telegram_id=user_data.telegram_id,
            is_verified=True,
        )

        created = await self._uow.users.create(user)
        await self._uow.commit()
        logger.info("User created (user_id={}, email={})", created.id, created.email)
        return created

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user information."""
        logger.debug("Updating user (user_id={})", user_id)
        user = await self.get_user_by_id(user_id)

        # Check if email is being changed and already exists
        if user_data.email and user_data.email != user.email:
            existing_user = await self._uow.users.get_by_email(user_data.email)
            if existing_user:
                logger.warning(
                    "Update user conflict: email already registered ({})", user_data.email
                )
                msg = "Email already registered"
                raise ConflictException(msg)
            user.email = user_data.email

        # Update other fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field) and field != "email":  # Already handled
                # Special handling for telegram_id to check for conflicts
                if field == "telegram_id" and value is not None:
                    existing_user = await self._uow.users.get_by_telegram_id(value)
                    if existing_user and existing_user.id != user_id:
                        logger.warning(
                            "Update user conflict: telegram_id already linked (telegram_id={}, owner_user_id={})",
                            value,
                            existing_user.id,
                        )
                        msg = "Telegram account already linked to another user"
                        raise ConflictException(msg)
                setattr(user, field, value)

        user.updated_at = datetime.now(UTC)

        updated = await self._uow.users.update(user)
        logger.info("User updated (user_id={})", updated.id)
        return updated

    async def deactivate_user(self, user_id: int) -> None:
        """Deactivate user account."""
        logger.info("Deactivating user (user_id={})", user_id)
        await self._uow.users.deactivate_user(user_id)

    async def delete_user(self, user_id: int) -> None:
        """Permanently delete user account."""
        logger.info("Deleting user (user_id={})", user_id)
        # Verify user exists before deleting
        await self.get_user_by_id(user_id)
        await self._uow.users.delete(user_id)

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        department_id: int | None = None,
        role: UserRole | None = None,
        *,
        is_active: bool | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[User], int]:
        """Get paginated list of users with filtering."""
        users, total = await self._uow.users.find_users(
            skip=skip,
            limit=limit,
            search=search,
            department_id=department_id,
            role=role,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return list(users), total

    async def update_user_role(self, user_id: int, role: UserRole) -> User:
        """Update user role."""
        logger.info("Updating user role (user_id={}, new_role={})", user_id, role)
        return await self._uow.users.update_role(user_id, role)

    async def link_telegram_account(self, user_id: int, telegram_id: int, username: str | None = None) -> User:
        """Link Telegram account to user."""
        logger.debug(
            "Linking telegram account (user_id={}, telegram_id={})", user_id, telegram_id
        )
        # Check if telegram_id is already linked to another user
        existing_user = await self._uow.users.get_by_telegram_id(telegram_id)
        if existing_user and existing_user.id != user_id:
            logger.warning(
                "Link telegram conflict (telegram_id={}, owner_user_id={})",
                telegram_id,
                existing_user.id,
            )
            msg = "Telegram account already linked to another user"
            raise ConflictException(msg)

        user = await self.get_user_by_id(user_id)
        user.telegram_id = telegram_id
        user.username = username
        user.updated_at = datetime.now(UTC)

        updated = await self._uow.users.update(user)
        logger.info(
            "Telegram account linked (user_id={}, telegram_id={})", updated.id, telegram_id
        )
        return updated

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """Change user password."""
        logger.debug("Password change requested (user_id={})", user_id)
        user = await self.get_user_by_id(user_id)

        if not user.password_hash:
            logger.warning("Password change failed: no password set (user_id={})", user_id)
            msg = "Password not set for this user"
            raise ValidationException(msg)

        if not verify_password(current_password, user.password_hash):
            logger.warning("Password change failed: invalid current password (user_id={})", user_id)
            msg = "Current password is incorrect"
            raise ValidationException(msg)

        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.now(UTC)

        await self._uow.users.update(user)
        logger.info("Password changed successfully (user_id={})", user_id)

    async def update_user_preferences(self, user_id: int, preferences_data: UserPreferencesUpdate) -> User:
        """Update user preferences (language, notification settings)."""
        logger.debug("Updating user preferences (user_id={})", user_id)
        user = await self.get_user_by_id(user_id)

        update_data = preferences_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        user.updated_at = datetime.now(UTC)

        updated = await self._uow.users.update(user)
        logger.info("User preferences updated (user_id={})", updated.id)
        return updated
