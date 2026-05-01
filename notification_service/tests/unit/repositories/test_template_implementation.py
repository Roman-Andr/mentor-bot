"""Unit tests for notification_service/repositories/implementations/template.py."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from notification_service.models import NotificationTemplate
from notification_service.repositories.implementations.template import NotificationTemplateRepository
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_session() -> MagicMock:
    """Create a mock AsyncSession."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    return session


@pytest.fixture
def template_repo(mock_session: MagicMock) -> NotificationTemplateRepository:
    """Create a NotificationTemplateRepository with mock session."""
    return NotificationTemplateRepository(mock_session)


@pytest.fixture
def sample_template() -> NotificationTemplate:
    """Create a sample NotificationTemplate."""
    return NotificationTemplate(
        id=1,
        name="welcome",
        channel="telegram",
        language="en",
        subject=None,
        body_text="Welcome, {{ user_name }}!",
        body_html=None,
        version=1,
        is_active=True,
        is_default=False,
        variables=["user_name"],
        created_by=1,
    )


class TestNotificationTemplateRepositoryGetByNameChannelLanguage:
    """Tests for NotificationTemplateRepository.get_by_name_channel_language."""

    async def test_get_existing_template(
        self,
        template_repo: NotificationTemplateRepository,
        mock_session: MagicMock,
        sample_template: NotificationTemplate,
    ) -> None:
        """Get template by name, channel, and language."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_template
        mock_session.execute.return_value = mock_result

        result = await template_repo.get_by_name_channel_language("welcome", "telegram", "en")

        assert result is not None
        assert result.name == "welcome"
        assert result.channel == "telegram"
        assert result.language == "en"

    async def test_get_returns_none_when_not_found(
        self, template_repo: NotificationTemplateRepository, mock_session: MagicMock
    ) -> None:
        """Returns None when template not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await template_repo.get_by_name_channel_language("nonexistent", "email", "ru")

        assert result is None

    async def test_get_uses_language_parameter(
        self,
        template_repo: NotificationTemplateRepository,
        mock_session: MagicMock,
        sample_template: NotificationTemplate,
    ) -> None:
        """Uses the language parameter correctly."""
        sample_template.language = "ru"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_template
        mock_session.execute.return_value = mock_result

        result = await template_repo.get_by_name_channel_language("welcome", "telegram", "ru")

        assert result is not None
        assert result.language == "ru"


class TestNotificationTemplateRepositoryFindTemplates:
    """Tests for NotificationTemplateRepository.find_templates."""

    async def test_find_without_filters(
        self,
        template_repo: NotificationTemplateRepository,
        mock_session: MagicMock,
        sample_template: NotificationTemplate,
    ) -> None:
        """Find templates without any filters."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_template]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        templates, total = await template_repo.find_templates()

        assert total == 1
        assert len(templates) == 1
        assert templates[0].name == "welcome"

    async def test_find_with_name_filter(
        self,
        template_repo: NotificationTemplateRepository,
        mock_session: MagicMock,
        sample_template: NotificationTemplate,
    ) -> None:
        """Find templates filtered by name (using ilike)."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_template]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        templates, total = await template_repo.find_templates(name="wel")

        assert total == 1
        assert len(templates) == 1

    async def test_find_with_channel_filter(
        self,
        template_repo: NotificationTemplateRepository,
        mock_session: MagicMock,
        sample_template: NotificationTemplate,
    ) -> None:
        """Find templates filtered by channel."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_template]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        templates, total = await template_repo.find_templates(channel="telegram")

        assert total == 1
        assert len(templates) == 1

    async def test_find_with_language_filter(
        self,
        template_repo: NotificationTemplateRepository,
        mock_session: MagicMock,
        sample_template: NotificationTemplate,
    ) -> None:
        """Find templates filtered by language."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_template]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        templates, total = await template_repo.find_templates(language="en")

        assert total == 1
        assert len(templates) == 1

    async def test_find_with_is_active_filter(
        self,
        template_repo: NotificationTemplateRepository,
        mock_session: MagicMock,
        sample_template: NotificationTemplate,
    ) -> None:
        """Find templates filtered by is_active status."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_template]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        templates, total = await template_repo.find_templates(is_active=True)

        assert total == 1
        assert len(templates) == 1

    async def test_find_with_all_filters(
        self,
        template_repo: NotificationTemplateRepository,
        mock_session: MagicMock,
        sample_template: NotificationTemplate,
    ) -> None:
        """Find templates with all filters applied."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_template]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        templates, total = await template_repo.find_templates(
            name="welcome", channel="telegram", language="en", is_active=True
        )

        assert total == 1
        assert len(templates) == 1

    async def test_find_returns_empty_when_no_matches(
        self, template_repo: NotificationTemplateRepository, mock_session: MagicMock
    ) -> None:
        """Returns empty list and zero total when no matches."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 0

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        templates, total = await template_repo.find_templates(name="nonexistent")

        assert total == 0
        assert templates == []

    async def test_respects_pagination_parameters(
        self,
        template_repo: NotificationTemplateRepository,
        mock_session: MagicMock,
        sample_template: NotificationTemplate,
    ) -> None:
        """Respects skip and limit parameters."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 100

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_template]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        templates, total = await template_repo.find_templates(skip=10, limit=5)

        assert total == 100
        assert len(templates) == 1


class TestNotificationTemplateRepositoryGetAllVersions:
    """Tests for NotificationTemplateRepository.get_all_versions."""

    async def test_get_all_versions_returns_list(
        self,
        template_repo: NotificationTemplateRepository,
        mock_session: MagicMock,
        sample_template: NotificationTemplate,
    ) -> None:
        """Get all versions of a template including inactive."""
        version2 = NotificationTemplate(
            id=2,
            name="welcome",
            channel="telegram",
            language="en",
            subject=None,
            body_text="Welcome!",
            body_html=None,
            version=2,
            is_active=False,
            is_default=False,
            variables=[],
            created_by=1,
        )

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [version2, sample_template]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await template_repo.get_all_versions("welcome", "telegram", "en")

        assert len(result) == 2
        assert result[0].version == 2
        assert result[1].version == 1

    async def test_get_all_versions_returns_empty_when_no_matches(
        self, template_repo: NotificationTemplateRepository, mock_session: MagicMock
    ) -> None:
        """Returns empty list when no versions found."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await template_repo.get_all_versions("nonexistent", "email", "ru")

        assert result == []
