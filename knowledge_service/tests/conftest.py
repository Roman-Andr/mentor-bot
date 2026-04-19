"""Pytest configuration for knowledge_service tests."""

import os
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

# Set required environment variables BEFORE any imports that read them
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/knowledge_db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/2")
os.environ.setdefault("SERVICE_API_KEY", "test-api-key")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8001")
os.environ.setdefault("FILE_STORAGE_PATH", "/tmp/test_files")  # noqa: S108
os.environ.setdefault("STORAGE_PATH", "/tmp/test_files")  # noqa: S108

# S3/MinIO storage configuration
os.environ.setdefault("S3_ENDPOINT", "http://localhost:9000")
os.environ.setdefault("S3_ACCESS_KEY", "test-access-key")
os.environ.setdefault("S3_SECRET_KEY", "test-secret-key")
os.environ.setdefault("S3_REGION", "us-east-1")
os.environ.setdefault("S3_USE_SSL", "false")
os.environ.setdefault("KNOWLEDGE_S3_BUCKET", "test-knowledge-bucket")
os.environ.setdefault("S3_PRESIGNED_URL_EXPIRY", "3600")

from pathlib import Path

from knowledge_service.api.deps import UserInfo
from knowledge_service.core import ArticleStatus, AttachmentType, DialogueCategory, EmployeeLevel
from knowledge_service.models import Article, Attachment, Category, DialogueScenario, Tag


@pytest.fixture
def mock_user() -> UserInfo:
    """Create a mock regular user."""
    return UserInfo(
        {
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
    )


@pytest.fixture
def mock_admin_user() -> UserInfo:
    """Create a mock admin user."""
    return UserInfo(
        {
            "id": 2,
            "email": "admin@example.com",
            "employee_id": "ADMIN001",
            "role": "ADMIN",
            "is_active": True,
            "is_verified": True,
            "department": {"id": 1, "name": "HR"},
            "position": "Manager",
            "level": "SENIOR",
            "first_name": "Admin",
            "last_name": "User",
            "telegram_id": None,
        }
    )


@pytest.fixture
def mock_hr_user() -> UserInfo:
    """Create a mock HR user."""
    return UserInfo(
        {
            "id": 3,
            "email": "hr@example.com",
            "employee_id": "HR001",
            "role": "HR",
            "is_active": True,
            "is_verified": True,
            "department": {"id": 2, "name": "HR"},
            "position": "HR Manager",
            "level": "SENIOR",
            "first_name": "HR",
            "last_name": "Manager",
            "telegram_id": None,
        }
    )


@pytest.fixture
def mock_article() -> Article:
    """Create a mock article model."""
    return Article(
        id=1,
        title="Test Article",
        slug="test-article",
        content="This is a test article content.",
        excerpt="Test excerpt",
        category_id=1,
        author_id=1,
        author_name="John Doe",
        department_id=1,
        position="Developer",
        level=EmployeeLevel.JUNIOR,
        status=ArticleStatus.PUBLISHED,
        is_pinned=False,
        is_featured=False,
        meta_title=None,
        meta_description=None,
        keywords=[],
        view_count=10,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        published_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_draft_article() -> Article:
    """Create a mock draft article model."""
    return Article(
        id=2,
        title="Draft Article",
        slug="draft-article",
        content="This is a draft article.",
        excerpt="Draft excerpt",
        category_id=1,
        author_id=1,
        author_name="John Doe",
        department_id=1,
        position="Developer",
        level=EmployeeLevel.JUNIOR,
        status=ArticleStatus.DRAFT,
        is_pinned=False,
        is_featured=False,
        meta_title=None,
        meta_description=None,
        keywords=[],
        view_count=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        published_at=None,
    )


@pytest.fixture
def mock_category() -> Category:
    """Create a mock category model."""
    return Category(
        id=1,
        name="Test Category",
        slug="test-category",
        description="Test category description",
        parent_id=None,
        order=0,
        department_id=1,
        position="Developer",
        level=EmployeeLevel.JUNIOR,
        icon="folder",
        color="#000000",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        articles=[],
        children=[],
    )


@pytest.fixture
def mock_child_category(mock_category: Category) -> Category:  # noqa: ARG001
    """Create a mock child category."""
    return Category(
        id=2,
        name="Child Category",
        slug="child-category",
        description="Child category description",
        parent_id=1,
        order=1,
        department_id=1,
        position="Developer",
        level=EmployeeLevel.JUNIOR,
        icon="subfolder",
        color="#111111",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        articles=[],
        children=[],
    )


@pytest.fixture
def mock_tag() -> Tag:
    """Create a mock tag model."""
    return Tag(
        id=1,
        name="Test Tag",
        slug="test-tag",
        description="Test tag description",
        usage_count=5,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        articles=[],
    )


@pytest.fixture
def mock_attachment() -> Attachment:
    """Create a mock attachment model."""
    return Attachment(
        id=1,
        article_id=1,
        name="test_file.pdf",
        type=AttachmentType.FILE,
        url="http://localhost/api/v1/attachments/file/1/test_file.pdf",
        file_size=1024,
        mime_type="application/pdf",
        description="Test file",
        order=0,
        is_downloadable=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_article_service(mock_article: Article, mock_draft_article: Article) -> AsyncMock:  # noqa: ARG001
    """Create a mock article service."""
    service = AsyncMock()
    service.get_article_by_id.return_value = mock_article
    service.get_article_by_slug.return_value = mock_article
    service.get_articles.return_value = ([mock_article], 1)
    service.get_articles_by_ids.return_value = [mock_article]
    service.get_department_articles.return_value = ([mock_article], 1)
    service.create_article.return_value = mock_article
    service.update_article.return_value = mock_article
    service.publish_article.return_value = mock_article
    service.get_article_stats.return_value = {
        "article_id": mock_article.id,
        "title": mock_article.title,
        "view_count": mock_article.view_count,
        "daily_views": [{"date": "2024-01-01", "count": 5}],
        "weekly_growth": 10.5,
        "popular_tags": ["test"],
    }
    service.record_view.return_value = None
    service.delete_article.return_value = None
    return service


@pytest.fixture
def mock_category_service(mock_category: Category, mock_child_category: Category) -> AsyncMock:
    """Create a mock category service."""
    service = AsyncMock()
    service.get_category_by_id.return_value = mock_category
    service.get_category_by_slug.return_value = mock_category
    service.get_categories.return_value = ([mock_category], 1)
    service.get_category_tree.return_value = (
        [
            {
                "id": 1,
                "name": "Test Category",
                "slug": "test-category",
                "description": "Test category description",
                "parent_id": None,
                "parent_name": None,
                "order": 0,
                "department_id": 1,
                "position": "Developer",
                "level": "JUNIOR",
                "icon": "folder",
                "color": "#000000",
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
                "articles_count": 0,
                "children": [
                    {
                        "id": 2,
                        "name": "Child Category",
                        "slug": "child-category",
                        "description": "Child category description",
                        "parent_id": 1,
                        "parent_name": "Test Category",
                        "order": 1,
                        "department_id": 1,
                        "position": "Developer",
                        "level": "JUNIOR",
                        "icon": "subfolder",
                        "color": "#111111",
                        "created_at": datetime.now(UTC).isoformat(),
                        "updated_at": datetime.now(UTC).isoformat(),
                        "articles_count": 0,
                        "children": [],
                    }
                ],
            }
        ],
        2,
    )
    service.get_department_categories.return_value = [mock_category, mock_child_category]
    service.create_category.return_value = mock_category
    service.update_category.return_value = mock_category
    service.delete_category.return_value = None
    return service


@pytest.fixture
def mock_tag_service(mock_tag: Tag) -> AsyncMock:
    """Create a mock tag service."""
    service = AsyncMock()
    service.get_tag_by_id.return_value = mock_tag
    service.get_tag_by_slug.return_value = mock_tag
    service.get_tags.return_value = ([mock_tag], 1)
    service.get_popular_tags.return_value = [mock_tag]
    service.get_tags_by_article.return_value = [mock_tag]
    service.create_tag.return_value = mock_tag
    service.update_tag.return_value = mock_tag
    service.delete_tag.return_value = None
    service.merge_tags.return_value = mock_tag
    return service


@pytest.fixture
def mock_attachment_service(mock_attachment: Attachment) -> AsyncMock:
    """Create a mock attachment service."""
    service = AsyncMock()
    service.get_attachment.return_value = mock_attachment
    service.get_attachments_by_article.return_value = [mock_attachment]
    service.create_attachment.return_value = mock_attachment
    service.delete_attachment.return_value = None
    return service


@pytest.fixture
def mock_search_service(mock_article: Article) -> AsyncMock:
    """Create a mock search service."""
    service = AsyncMock()
    service.search_articles.return_value = (
        [{"id": mock_article.id, "score": 1.0}],
        1,
        [],
    )
    service.get_search_suggestions.return_value = ["suggestion1", "suggestion2"]
    service.get_popular_searches.return_value = [{"query": "test", "count": 10}]
    service.get_user_search_history.return_value = ([], 0)
    service.clear_user_search_history.return_value = None
    service.get_search_stats.return_value = {
        "total_searches": 100,
        "popular_queries": [],
        "no_results_queries": [],
        "searches_by_department": {},
        "avg_results_per_search": 5.0,
        "searches_last_30_days": [],
    }
    return service


@pytest.fixture
def temp_storage_path(tmp_path: Path) -> Path:
    """Create a temporary storage path for file tests."""
    storage = tmp_path / "test_files"
    storage.mkdir(parents=True, exist_ok=True)
    return storage


@pytest.fixture
def mock_dialogue_scenario() -> DialogueScenario:
    """Create a mock dialogue scenario model."""
    return DialogueScenario(
        id=1,
        title="Welcome Flow",
        description="New employee welcome flow",
        category=DialogueCategory.CONTACTS,
        is_active=True,
        display_order=0,
        keywords=["welcome", "new employee"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        steps=[],
    )


@pytest.fixture
def mock_dialogue_service(mock_dialogue_scenario: DialogueScenario) -> AsyncMock:
    """Create a mock dialogue service."""
    service = AsyncMock()
    service.find_scenarios.return_value = ([mock_dialogue_scenario], 1)
    service.get_active_scenarios.return_value = ([mock_dialogue_scenario], 1)
    service.get_scenarios_by_category.return_value = ([mock_dialogue_scenario], 1)
    service.get_scenario_by_id.return_value = mock_dialogue_scenario
    service.create_scenario.return_value = mock_dialogue_scenario
    service.update_scenario.return_value = mock_dialogue_scenario
    service.delete_scenario.return_value = None
    service.get_first_step.return_value = AsyncMock()
    service.add_step.return_value = AsyncMock()
    service.update_step.return_value = AsyncMock()
    service.delete_step.return_value = None
    service.reorder_steps.return_value = None
    return service


@pytest.fixture
def mock_storage_service() -> MagicMock:
    """Create a mock S3 storage service."""
    from io import BytesIO

    storage = MagicMock()

    # Mock upload_file to return the object name (async)
    storage.upload_file = AsyncMock(return_value="test_object_name")

    # Mock download_file to return BytesIO (async)
    storage.download_file = AsyncMock(return_value=BytesIO(b"test file content"))

    # Mock delete_file to return True (async)
    storage.delete_file = AsyncMock(return_value=True)

    # Mock file_exists to return True (async)
    storage.file_exists = AsyncMock(return_value=True)

    # Mock get_presigned_url to return a test URL (sync - returns string directly)
    storage.get_presigned_url.return_value = (
        "http://localhost:9000/test-knowledge-bucket/articles/1/test.pdf?presigned=true"
    )

    # Mock get_public_url (sync)
    storage.get_public_url.return_value = "http://localhost:9000/test-knowledge-bucket/test_object"

    return storage
