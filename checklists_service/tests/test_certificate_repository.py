"""Tests for certificate repository."""

import pytest
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from checklists_service.repositories.implementations.certificate import CertificateRepository
from checklists_service.models import Certificate


@pytest.mark.asyncio
async def test_create_certificate() -> None:
    """Test creating a certificate."""
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    repo = CertificateRepository(session)

    certificate = Certificate(
        id=1,
        cert_uid="test-uid",
        user_id=1,
        checklist_id=1,
        hr_id=10,
        mentor_id=2,
        issued_at=datetime.now(UTC),
    )

    session.add.assert_not_called()
    session.flush.assert_not_called()


@pytest.mark.asyncio
async def test_get_by_checklist_id() -> None:
    """Test getting certificate by checklist ID."""
    session = MagicMock()
    session.execute = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock
    repo = CertificateRepository(session)

    result = await repo.get_by_checklist_id(1)

    assert result is None
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_checklist_ids() -> None:
    """Test getting certificates by multiple checklist IDs."""
    session = MagicMock()
    session.execute = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    session.execute.return_value = result_mock
    repo = CertificateRepository(session)

    result = await repo.get_by_checklist_ids([1, 2, 3])

    assert result == []
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_user() -> None:
    """Test getting certificates for a user."""
    session = MagicMock()
    session.execute = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    session.execute.return_value = result_mock
    repo = CertificateRepository(session)

    result = await repo.get_by_user(1)

    assert result == []
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_cert_uid() -> None:
    """Test getting certificate by cert_uid."""
    session = MagicMock()
    session.execute = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock
    repo = CertificateRepository(session)

    result = await repo.get_by_cert_uid("test-uid")

    assert result is None
    session.execute.assert_awaited_once()
