"""Integration tests for Unit of Work commits to verify database persistence."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from checklists_service.core.enums import ChecklistStatus, TaskStatus
from checklists_service.database.base import Base
from checklists_service.models import Checklist, Task
from checklists_service.repositories.implementations.checklist import ChecklistRepository
from checklists_service.repositories.implementations.task import TaskRepository
from checklists_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from checklists_service.services import TaskService


@pytest.fixture
async def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

    # Use SQLite in-memory for faster tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    yield async_session
    
    await engine.dispose()


@pytest.fixture
async def db_session(in_memory_db):
    """Create a database session for testing."""
    async with in_memory_db() as session:
        yield session


@pytest.fixture
async def real_uow(db_session):
    """Create a real Unit of Work with actual database session."""
    async with SqlAlchemyUnitOfWork(lambda: db_session) as uow:
        yield uow


@pytest.mark.asyncio
async def test_task_complete_commits_to_database(real_uow):
    """Test that complete_task actually commits changes to the database."""
    # Create a checklist
    now = datetime.now(UTC)
    checklist = Checklist(
        id=1,
        user_id=1,
        employee_id="EMP001",
        template_id=1,
        status=ChecklistStatus.IN_PROGRESS,
        progress_percentage=0,
        completed_tasks=0,
        total_tasks=1,
        start_date=now,
        due_date=now,
        completed_at=None,
        mentor_id=None,
        hr_id=None,
        notes=None,
        created_at=now,
        updated_at=None,
        is_overdue=False,
        days_remaining=None,
    )
    await real_uow.checklists.add(checklist)
    await real_uow.commit()
    
    # Create a task
    task = Task(
        id=1,
        checklist_id=1,
        template_task_id=1,
        title="Test Task",
        description="Test",
        category="General",
        order=1,
        assignee_id=1,
        assignee_role="MENTOR",
        due_date=now,
        depends_on=[],
        status=TaskStatus.PENDING,
        started_at=None,
        completed_at=None,
        completed_by=None,
        completion_notes=None,
        attachments=[],
        blocks=[],
        created_at=now,
        updated_at=None,
        is_overdue=False,
        can_start=True,
        can_complete=True,
    )
    await real_uow.tasks.add(task)
    await real_uow.commit()
    
    # Complete the task using the service
    service = TaskService(real_uow)
    completed_task = await service.complete_task(1, completed_by=1)
    
    # Verify task was marked as completed in memory
    assert completed_task.status == TaskStatus.COMPLETED
    assert completed_task.completed_at is not None
    
    # Create a new UoW with a fresh session to verify database persistence
    async with SqlAlchemyUnitOfWork(lambda: db_session) as new_uow:
        # Fetch the task from the database
        fetched_task = await new_uow.tasks.get_by_id(1)
        
        # Verify the task is actually COMPLETED in the database
        assert fetched_task is not None
        assert fetched_task.status == TaskStatus.COMPLETED
        assert fetched_task.completed_at is not None
        assert fetched_task.completed_by == 1


@pytest.mark.asyncio
async def test_recalculate_progress_commits_to_database(real_uow):
    """Test that recalculate_progress actually commits changes to the database."""
    # Create a checklist with 2 tasks
    now = datetime.now(UTC)
    checklist = Checklist(
        id=1,
        user_id=1,
        employee_id="EMP001",
        template_id=1,
        status=ChecklistStatus.IN_PROGRESS,
        progress_percentage=0,
        completed_tasks=0,
        total_tasks=2,
        start_date=now,
        due_date=now,
        completed_at=None,
        mentor_id=None,
        hr_id=None,
        notes=None,
        created_at=now,
        updated_at=None,
        is_overdue=False,
        days_remaining=None,
    )
    await real_uow.checklists.add(checklist)
    await real_uow.commit()
    
    # Create 2 tasks
    task1 = Task(
        id=1,
        checklist_id=1,
        template_task_id=1,
        title="Task 1",
        description="Test",
        category="General",
        order=1,
        assignee_id=1,
        assignee_role="MENTOR",
        due_date=now,
        depends_on=[],
        status=TaskStatus.COMPLETED,
        started_at=None,
        completed_at=now,
        completed_by=1,
        completion_notes=None,
        attachments=[],
        blocks=[],
        created_at=now,
        updated_at=None,
        is_overdue=False,
        can_start=True,
        can_complete=True,
    )
    task2 = Task(
        id=2,
        checklist_id=1,
        template_task_id=2,
        title="Task 2",
        description="Test",
        category="General",
        order=2,
        assignee_id=1,
        assignee_role="MENTOR",
        due_date=now,
        depends_on=[],
        status=TaskStatus.PENDING,
        started_at=None,
        completed_at=None,
        completed_by=None,
        completion_notes=None,
        attachments=[],
        blocks=[],
        created_at=now,
        updated_at=None,
        is_overdue=False,
        can_start=True,
        can_complete=True,
    )
    await real_uow.tasks.add(task1)
    await real_uow.tasks.add(task2)
    await real_uow.commit()
    
    # Recalculate progress
    await real_uow.checklists.recalculate_progress(1)
    
    # Create a new UoW with a fresh session to verify database persistence
    async with SqlAlchemyUnitOfWork(lambda: db_session) as new_uow:
        # Fetch the checklist from the database
        fetched_checklist = await new_uow.checklists.get_by_id(1)
        
        # Verify the progress was actually updated in the database
        assert fetched_checklist is not None
        assert fetched_checklist.completed_tasks == 1
        assert fetched_checklist.total_tasks == 2
        assert fetched_checklist.progress_percentage == 50


@pytest.mark.asyncio
async def test_uow_commit_persists_changes(real_uow):
    """Test that UoW.commit() actually persists changes to the database."""
    # Create a checklist
    now = datetime.now(UTC)
    checklist = Checklist(
        id=1,
        user_id=1,
        employee_id="EMP001",
        template_id=1,
        status=ChecklistStatus.IN_PROGRESS,
        progress_percentage=0,
        completed_tasks=0,
        total_tasks=0,
        start_date=now,
        due_date=now,
        completed_at=None,
        mentor_id=None,
        hr_id=None,
        notes=None,
        created_at=now,
        updated_at=None,
        is_overdue=False,
        days_remaining=None,
    )
    
    # Add to repository but don't commit yet
    await real_uow.checklists.add(checklist)
    
    # Create a new UoW with a fresh session to verify it's NOT in database yet
    async with SqlAlchemyUnitOfWork(lambda: db_session) as new_uow:
        fetched = await new_uow.checklists.get_by_id(1)
        assert fetched is None  # Should not exist yet
    
    # Now commit
    await real_uow.commit()
    
    # Create a new UoW with a fresh session to verify it IS in database now
    async with SqlAlchemyUnitOfWork(lambda: db_session) as new_uow:
        fetched = await new_uow.checklists.get_by_id(1)
        assert fetched is not None  # Should exist now
        assert fetched.employee_id == "EMP001"


@pytest.mark.asyncio
async def test_uow_rollback_does_not_persist_changes(real_uow):
    """Test that UoW.rollback() does not persist changes to the database."""
    # Create a checklist
    now = datetime.now(UTC)
    checklist = Checklist(
        id=1,
        user_id=1,
        employee_id="EMP001",
        template_id=1,
        status=ChecklistStatus.IN_PROGRESS,
        progress_percentage=0,
        completed_tasks=0,
        total_tasks=0,
        start_date=now,
        due_date=now,
        completed_at=None,
        mentor_id=None,
        hr_id=None,
        notes=None,
        created_at=now,
        updated_at=None,
        is_overdue=False,
        days_remaining=None,
    )
    
    # Add to repository
    await real_uow.checklists.add(checklist)
    
    # Rollback instead of commit
    await real_uow.rollback()
    
    # Create a new UoW with a fresh session to verify it's NOT in database
    async with SqlAlchemyUnitOfWork(lambda: db_session) as new_uow:
        fetched = await new_uow.checklists.get_by_id(1)
        assert fetched is None  # Should not exist after rollback
