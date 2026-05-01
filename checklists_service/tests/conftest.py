"""Pytest configuration for checklists_service tests."""

import os

# Clear proxy environment variables to prevent httpx errors with unsupported socks:// scheme
for proxy_var in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"]:
    os.environ.pop(proxy_var, None)

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

# Set required environment variables BEFORE any imports that read them
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/checklists_db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("SERVICE_API_KEY", "test-api-key")

from checklists_service.core.enums import (
    ChecklistStatus,
    EmployeeLevel,
    TaskCategory,
    TaskStatus,
    TemplateStatus,
)
from checklists_service.models import Checklist, Task, TaskTemplate, Template


class Department:
    """Simple test class for Department (not a real model in checklists_service)."""

    def __init__(self, id: int, name: str, description: str, created_at: datetime, updated_at: datetime | None = None):
        """Initialize Department test class."""
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
from checklists_service.repositories.unit_of_work import IUnitOfWork
from checklists_service.schemas import (
    ChecklistCreate,
    ChecklistUpdate,
    TaskProgress,
    TaskTemplateCreate,
    TaskUpdate,
    TemplateCreate,
    TemplateUpdate,
)


@pytest.fixture
def mock_uow() -> MagicMock:
    """Create a mock Unit of Work with all repositories."""
    uow = MagicMock(spec=IUnitOfWork)

    # Setup mock repositories
    uow.checklists = AsyncMock()
    uow.tasks = AsyncMock()
    uow.templates = AsyncMock()
    uow.task_templates = AsyncMock()
    uow.certificates = AsyncMock()

    # Setup commit/rollback as async mocks
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()

    return uow


@pytest.fixture
def sample_datetime() -> datetime:
    """Return a sample datetime for testing."""
    return datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)


@pytest.fixture
def sample_template(sample_datetime: datetime) -> Template:
    """Create a sample template for testing."""
    return Template(
        id=1,
        name="Onboarding Template",
        description="Standard onboarding template",
        department_id=1,
        position="Developer",
        level=EmployeeLevel.JUNIOR,
        duration_days=30,
        task_categories=[TaskCategory.DOCUMENTATION, TaskCategory.TRAINING],
        default_assignee_role="MENTOR",
        status=TemplateStatus.ACTIVE,
        version=1,
        is_default=False,
        created_at=sample_datetime,
        updated_at=None,
    )


@pytest.fixture
def sample_template_draft(sample_datetime: datetime) -> Template:
    """Create a sample draft template for testing."""
    return Template(
        id=2,
        name="Draft Template",
        description="Draft template for testing",
        department_id=None,
        position=None,
        level=None,
        duration_days=14,
        task_categories=[],
        default_assignee_role=None,
        status=TemplateStatus.DRAFT,
        version=1,
        is_default=False,
        created_at=sample_datetime,
        updated_at=None,
    )


@pytest.fixture
def sample_task_template(sample_datetime: datetime) -> TaskTemplate:
    """Create a sample task template for testing."""
    return TaskTemplate(
        id=1,
        template_id=1,
        title="Complete Documentation",
        description="Read and sign all documentation",
        instructions="Go through the employee handbook",
        category=TaskCategory.DOCUMENTATION,
        order=0,
        due_days=3,
        estimated_minutes=60,
        resources=[{"title": "Handbook", "url": "https://example.com/handbook"}],
        required_documents=["signed_contract"],
        assignee_role="MENTOR",
        auto_assign=True,
        depends_on=[],
        created_at=sample_datetime,
        updated_at=None,
    )


@pytest.fixture
def sample_task_template_with_depends(sample_datetime: datetime) -> TaskTemplate:
    """Create a sample task template with dependencies for testing."""
    return TaskTemplate(
        id=2,
        template_id=1,
        title="Setup Development Environment",
        description="Install required tools and software",
        instructions="Follow the setup guide",
        category=TaskCategory.TECHNICAL,
        order=1,
        due_days=5,
        estimated_minutes=120,
        resources=[],
        required_documents=[],
        assignee_role="MENTOR",
        auto_assign=True,
        depends_on=[1],
        created_at=sample_datetime,
        updated_at=None,
    )


@pytest.fixture
def sample_checklist(sample_datetime: datetime) -> Checklist:
    """Create a sample checklist for testing."""
    return Checklist(
        id=1,
        user_id=1,
        employee_id="EMP001",
        template_id=1,
        status=ChecklistStatus.IN_PROGRESS,
        progress_percentage=0,
        completed_tasks=0,
        total_tasks=5,
        start_date=sample_datetime,
        due_date=sample_datetime + timedelta(days=30),
        completed_at=None,
        mentor_id=2,
        hr_id=3,
        notes="Test checklist",
        created_at=sample_datetime,
        updated_at=None,
    )


@pytest.fixture
def sample_completed_checklist(sample_datetime: datetime) -> Checklist:
    """Create a sample completed checklist for testing."""
    return Checklist(
        id=2,
        user_id=2,
        employee_id="EMP002",
        template_id=1,
        status=ChecklistStatus.COMPLETED,
        progress_percentage=100,
        completed_tasks=5,
        total_tasks=5,
        start_date=sample_datetime - timedelta(days=30),
        due_date=sample_datetime,
        completed_at=sample_datetime,
        mentor_id=2,
        hr_id=3,
        notes="Completed checklist",
        created_at=sample_datetime - timedelta(days=30),
        updated_at=sample_datetime,
    )


@pytest.fixture
def sample_task(sample_datetime: datetime) -> Task:
    """Create a sample task for testing."""
    return Task(
        id=1,
        checklist_id=1,
        template_task_id=1,
        title="Complete Documentation",
        description="Read and sign all documentation",
        category="DOCUMENTATION",
        status=TaskStatus.PENDING,
        order=0,
        assignee_id=2,
        assignee_role="MENTOR",
        due_date=sample_datetime + timedelta(days=3),
        started_at=None,
        completed_at=None,
        completed_by=None,
        completion_notes=None,
        attachments=[],
        depends_on=[],
        blocks=[],
        created_at=sample_datetime,
        updated_at=None,
    )


@pytest.fixture
def sample_in_progress_task(sample_datetime: datetime) -> Task:
    """Create a sample in-progress task for testing."""
    return Task(
        id=2,
        checklist_id=1,
        template_task_id=2,
        title="Setup Development Environment",
        description="Install required tools",
        category="TECHNICAL",
        status=TaskStatus.IN_PROGRESS,
        order=1,
        assignee_id=2,
        assignee_role="MENTOR",
        due_date=sample_datetime + timedelta(days=5),
        started_at=sample_datetime,
        completed_at=None,
        completed_by=None,
        completion_notes=None,
        attachments=[],
        depends_on=[1],
        blocks=[],
        created_at=sample_datetime,
        updated_at=None,
    )


@pytest.fixture
def sample_completed_task(sample_datetime: datetime) -> Task:
    """Create a sample completed task for testing."""
    return Task(
        id=3,
        checklist_id=1,
        template_task_id=3,
        title="Attend Orientation",
        description="Attend the orientation meeting",
        category="MEETING",
        status=TaskStatus.COMPLETED,
        order=2,
        assignee_id=1,
        assignee_role="EMPLOYEE",
        due_date=sample_datetime + timedelta(days=1),
        started_at=sample_datetime,
        completed_at=sample_datetime + timedelta(hours=2),
        completed_by=1,
        completion_notes="Completed successfully",
        attachments=[],
        depends_on=[],
        blocks=[2],
        created_at=sample_datetime,
        updated_at=sample_datetime + timedelta(hours=2),
    )


@pytest.fixture
def sample_blocked_task(sample_datetime: datetime) -> Task:
    """Create a sample blocked task for testing."""
    return Task(
        id=4,
        checklist_id=1,
        template_task_id=4,
        title="Advanced Training",
        description="Complete advanced training modules",
        category="TRAINING",
        status=TaskStatus.BLOCKED,
        order=3,
        assignee_id=1,
        assignee_role="EMPLOYEE",
        due_date=sample_datetime + timedelta(days=10),
        started_at=None,
        completed_at=None,
        completed_by=None,
        completion_notes=None,
        attachments=[],
        depends_on=[2],
        blocks=[],
        created_at=sample_datetime,
        updated_at=None,
    )


@pytest.fixture
def sample_department(sample_datetime: datetime) -> Department:
    """Create a sample department for testing."""
    return Department(
        id=1,
        name="Engineering",
        description="Engineering Department",
        created_at=sample_datetime,
        updated_at=None,
    )


@pytest.fixture
def sample_checklist_create_data(sample_datetime: datetime) -> ChecklistCreate:
    """Create sample checklist creation data."""
    return ChecklistCreate(
        user_id=1,
        employee_id="EMP001",
        template_id=1,
        start_date=sample_datetime,
        due_date=sample_datetime + timedelta(days=30),
        mentor_id=2,
        hr_id=3,
        notes="Test checklist creation",
    )


@pytest.fixture
def sample_template_create_data() -> TemplateCreate:
    """Create sample template creation data."""
    return TemplateCreate(
        name="New Template",
        description="A new test template",
        department_id=1,
        position="Developer",
        level=EmployeeLevel.JUNIOR,
        duration_days=30,
        task_categories=[TaskCategory.DOCUMENTATION, TaskCategory.TRAINING],
        default_assignee_role="MENTOR",
        status=TemplateStatus.DRAFT,
    )


@pytest.fixture
def sample_task_template_create_data() -> TaskTemplateCreate:
    """Create sample task template creation data."""
    return TaskTemplateCreate(
        template_id=1,
        title="New Task",
        description="A new test task",
        instructions="Follow these instructions",
        category=TaskCategory.TECHNICAL,
        order=0,
        due_days=5,
        estimated_minutes=120,
        resources=[{"title": "Guide", "url": "https://example.com/guide"}],
        required_documents=["document1"],
        assignee_role="MENTOR",
        auto_assign=True,
        depends_on=[],
    )


@pytest.fixture
def sample_task_update_data() -> TaskUpdate:
    """Create sample task update data."""
    return TaskUpdate(
        status=TaskStatus.IN_PROGRESS,
        assignee_id=2,
    )


@pytest.fixture
def sample_task_progress_data() -> TaskProgress:
    """Create sample task progress data."""
    return TaskProgress(
        task_id=1,
        status=TaskStatus.COMPLETED,
        progress_percentage=100,
        notes="Task completed successfully",
        attachments=[{"filename": "doc.pdf", "url": "https://example.com/doc.pdf"}],
    )


@pytest.fixture
def sample_checklist_update_data() -> ChecklistUpdate:
    """Create sample checklist update data."""
    return ChecklistUpdate(
        status=ChecklistStatus.COMPLETED,
        progress_percentage=100,
        notes="Updated notes",
    )


@pytest.fixture
def sample_template_update_data() -> TemplateUpdate:
    """Create sample template update data."""
    return TemplateUpdate(
        name="Updated Template Name",
        description="Updated description",
        status=TemplateStatus.ACTIVE,
        is_default=True,
    )


@pytest.fixture
def mock_user_hr() -> dict:
    """Create a mock HR user for testing."""
    return {
        "id": 10,
        "email": "hr@example.com",
        "employee_id": "HR001",
        "role": "HR",
        "is_active": True,
        "is_verified": True,
        "department": {"id": 1, "name": "HR"},
        "position": "HR Manager",
        "level": "SENIOR",
        "first_name": "Jane",
        "last_name": "Smith",
        "telegram_id": None,
    }


@pytest.fixture
def mock_user_admin() -> dict:
    """Create a mock admin user for testing."""
    return {
        "id": 11,
        "email": "admin@example.com",
        "employee_id": "ADM001",
        "role": "ADMIN",
        "is_active": True,
        "is_verified": True,
        "department": {"id": 1, "name": "IT"},
        "position": "System Administrator",
        "level": "LEAD",
        "first_name": "Admin",
        "last_name": "User",
        "telegram_id": None,
    }


@pytest.fixture
def mock_user_mentor() -> dict:
    """Create a mock mentor user for testing."""
    return {
        "id": 2,
        "email": "mentor@example.com",
        "employee_id": "MEN001",
        "role": "MENTOR",
        "is_active": True,
        "is_verified": True,
        "department": {"id": 1, "name": "Engineering"},
        "position": "Senior Developer",
        "level": "SENIOR",
        "first_name": "John",
        "last_name": "Doe",
        "telegram_id": None,
    }


@pytest.fixture
def mock_user_employee() -> dict:
    """Create a mock employee user for testing."""
    return {
        "id": 1,
        "email": "employee@example.com",
        "employee_id": "EMP001",
        "role": "EMPLOYEE",
        "is_active": True,
        "is_verified": True,
        "department": {"id": 1, "name": "Engineering"},
        "position": "Junior Developer",
        "level": "JUNIOR",
        "first_name": "Bob",
        "last_name": "Wilson",
        "telegram_id": None,
    }


@pytest.fixture
def mock_auth_token() -> str:
    """Create a mock auth token."""
    return "Bearer mock-jwt-token-12345"


@pytest.fixture
def service_api_key() -> str:
    """Get the service API key."""
    return os.environ.get("SERVICE_API_KEY", "test-api-key")


@pytest.fixture
async def async_session():
    """Create an async database session for testing."""
    from checklists_service.database.base import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def async_client(async_session):
    """Create an async HTTP client for testing."""
    from httpx import AsyncClient, ASGITransport
    from checklists_service.main import app
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def auth_headers():
    """Create authentication headers for regular user."""
    return {"Authorization": "Bearer test-user-token"}


@pytest.fixture
def hr_headers():
    """Create authentication headers for HR user."""
    return {"Authorization": "Bearer test-hr-token"}
