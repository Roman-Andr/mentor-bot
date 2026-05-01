"""Tests for certificate repository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.models import Certificate
from checklists_service.repositories.implementations.certificate import CertificateRepository


@pytest.mark.asyncio
async def test_create_certificate(async_session: AsyncSession) -> None:
    """Test creating a certificate."""
    repo = CertificateRepository(async_session)
    
    certificate = Certificate(
        cert_uid="test-uid-123",
        user_id=1,
        checklist_id=1,
        hr_id=2,
        mentor_id=3,
    )
    
    created = await repo.create(certificate)
    assert created.id is not None
    assert created.cert_uid == "test-uid-123"
    assert created.user_id == 1


@pytest.mark.asyncio
async def test_get_by_checklist_id(async_session: AsyncSession) -> None:
    """Test getting certificate by checklist ID."""
    repo = CertificateRepository(async_session)
    
    # Create a certificate first
    certificate = Certificate(
        cert_uid="test-uid-456",
        user_id=1,
        checklist_id=2,
    )
    await repo.create(certificate)
    
    # Retrieve it
    retrieved = await repo.get_by_checklist_id(2)
    assert retrieved is not None
    assert retrieved.cert_uid == "test-uid-456"


@pytest.mark.asyncio
async def test_get_by_checklist_ids(async_session: AsyncSession) -> None:
    """Test getting certificates by multiple checklist IDs."""
    repo = CertificateRepository(async_session)
    
    # Create multiple certificates
    await repo.create(Certificate(cert_uid="test-uid-1", user_id=1, checklist_id=10))
    await repo.create(Certificate(cert_uid="test-uid-2", user_id=2, checklist_id=11))
    
    # Retrieve them
    certificates = await repo.get_by_checklist_ids([10, 11])
    assert len(certificates) == 2


@pytest.mark.asyncio
async def test_get_by_user(async_session: AsyncSession) -> None:
    """Test getting certificates for a user."""
    repo = CertificateRepository(async_session)
    
    # Create certificates for user 1
    await repo.create(Certificate(cert_uid="test-uid-user-1", user_id=100, checklist_id=20))
    await repo.create(Certificate(cert_uid="test-uid-user-2", user_id=100, checklist_id=21))
    
    # Retrieve user's certificates
    certificates = await repo.get_by_user(100)
    assert len(certificates) == 2
    assert all(c.user_id == 100 for c in certificates)


@pytest.mark.asyncio
async def test_get_by_cert_uid(async_session: AsyncSession) -> None:
    """Test getting certificate by cert_uid."""
    repo = CertificateRepository(async_session)
    
    # Create a certificate
    await repo.create(Certificate(cert_uid="unique-uid-789", user_id=1, checklist_id=30))
    
    # Retrieve by cert_uid
    retrieved = await repo.get_by_cert_uid("unique-uid-789")
    assert retrieved is not None
    assert retrieved.checklist_id == 30
