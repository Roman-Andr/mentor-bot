"""User schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from auth_service.core import EmployeeLevel, UserRole
from auth_service.schemas.department import DepartmentResponse


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    department_id: int | None = None
    position: str | None = Field(None, max_length=100)
    level: EmployeeLevel | None = Field(None, max_length=50)


class UserCreate(UserBase):
    """User creation schema."""

    employee_id: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8)
    role: UserRole = Field(default=UserRole.NEWBIE)
    telegram_id: int | None = None


class UserUpdate(BaseModel):
    """User update schema."""

    email: EmailStr | None = None
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    department_id: int | None = None
    position: str | None = Field(None, max_length=100)
    level: EmployeeLevel | None = Field(None, max_length=50)
    role: UserRole | None = None
    is_active: bool | None = None
    telegram_id: int | None = None


class UserResponse(UserBase):
    """User response schema."""

    id: int
    employee_id: str
    telegram_id: int | None = None
    username: str | None = None
    role: UserRole
    is_active: bool
    is_verified: bool
    hire_date: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    last_login_at: datetime | None = None
    department: DepartmentResponse | None = None
    mentor_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """User list response schema."""

    total: int
    users: list[UserResponse]
    page: int
    size: int
    pages: int
