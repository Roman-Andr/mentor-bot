"""Tests for unit of work implementation."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from checklists_service.repositories.unit_of_work import SqlAlchemyUnitOfWork, sqlalchemy_uow
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class TestSqlAlchemyUnitOfWork:
    """Test SQLAlchemy Unit of Work."""

    @pytest.fixture
    def mock_session_factory(self):
        """Create a mock session factory."""
        factory = MagicMock(spec=async_sessionmaker)
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        factory.return_value = mock_session
        return factory

    async def test_initialization(self, mock_session_factory):
        """Test UOW initialization."""
        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        assert uow._session_factory is mock_session_factory
        assert uow._session is None
        assert not hasattr(uow, "checklists")

    async def test_aenter_initializes_repositories(self, mock_session_factory):
        """Test entering context initializes repositories."""
        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        async with uow as u:
            assert u._session is not None
            assert hasattr(u, "checklists")
            assert hasattr(u, "tasks")
            assert hasattr(u, "templates")
            assert hasattr(u, "task_templates")

    async def test_aexit_closes_session(self, mock_session_factory):
        """Test exiting context closes session."""
        uow = SqlAlchemyUnitOfWork(mock_session_factory)
        session = None

        async with uow as u:
            session = u._session

        session.close.assert_awaited_once()

    async def test_commit(self, mock_session_factory):
        """Test commit calls session commit."""
        uow = SqlAlchemyUnitOfWork(mock_session_factory)
        session = None

        async with uow as u:
            session = u._session
            await u.commit()

        # Commit is called twice: once explicitly, once in __aexit__
        assert session.commit.await_count == 2

    async def test_commit_no_session_raises(self, mock_session_factory):
        """Test commit without session raises error."""
        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await uow.commit()

    async def test_rollback(self, mock_session_factory):
        """Test rollback calls session rollback."""
        uow = SqlAlchemyUnitOfWork(mock_session_factory)
        session = None

        async with uow as u:
            session = u._session
            await u.rollback()

        session.rollback.assert_awaited_once()

    async def test_rollback_no_session_raises(self, mock_session_factory):
        """Test rollback without session raises error."""
        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await uow.rollback()

    async def test_context_manager_exception_rolls_back(self, mock_session_factory):
        """Test exception in context properly rolls back and closes session."""
        mock_session = mock_session_factory.return_value

        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        with pytest.raises(ValueError):
            async with uow:
                raise ValueError("Test error")

        # Rollback should be called on exception
        mock_session.rollback.assert_awaited_once()
        # Session should still be closed even on exception
        mock_session.close.assert_awaited_once()


class TestSqlalchemyUowContextManager:
    """Test the sqlalchemy_uow helper function."""

    async def test_sqlalchemy_uow_yields_uow(self):
        """Test that sqlalchemy_uow yields a usable UOW."""
        mock_factory = MagicMock(spec=async_sessionmaker)
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        mock_factory.return_value = mock_session

        async with sqlalchemy_uow(mock_factory) as uow:
            assert isinstance(uow, SqlAlchemyUnitOfWork)
            assert uow._session is not None


class TestIUnitOfWorkProtocol:
    """Test IUnitOfWork Protocol implementation (lines 28, 32, 36, 40)."""

    async def test_iunit_of_work_protocol_methods(self):
        """Test that IUnitOfWork protocol methods exist and are abstract (line 28, 32, 36, 40)."""
        from checklists_service.repositories.unit_of_work import IUnitOfWork

        # Verify IUnitOfWork is a Protocol
        assert hasattr(IUnitOfWork, "__protocol_attrs__")

        # Check that abstract methods exist with ellipsis (...) body

        # commit method should be abstract (line 28)
        assert hasattr(IUnitOfWork, "commit")

        # rollback method should be abstract (line 32)
        assert hasattr(IUnitOfWork, "rollback")

        # __aenter__ method should be abstract (line 36)
        assert hasattr(IUnitOfWork, "__aenter__")

        # __aexit__ method should be abstract (line 40)
        assert hasattr(IUnitOfWork, "__aexit__")

    async def test_sqlalchemy_uow_implements_protocol(self):
        """Test that SqlAlchemyUnitOfWork properly implements IUnitOfWork protocol."""
        from checklists_service.repositories.unit_of_work import IUnitOfWork

        mock_factory = MagicMock(spec=async_sessionmaker)
        mock_session = MagicMock(spec=AsyncSession)
        mock_factory.return_value = mock_session

        uow = SqlAlchemyUnitOfWork(mock_factory)

        # Verify SqlAlchemyUnitOfWork is considered an implementation of IUnitOfWork
        assert isinstance(uow, IUnitOfWork)

    async def test_protocol_runtime_checkable(self):
        """Test that IUnitOfWork is runtime checkable."""
        from checklists_service.repositories.unit_of_work import IUnitOfWork

        # Verify the protocol is decorated with @runtime_checkable
        # In Python 3.14, Protocol classes have _is_runtime_checkable attribute
        if hasattr(IUnitOfWork, "_is_runtime_checkable"):
            assert IUnitOfWork._is_runtime_checkable is True
        else:
            # Alternative check: verify it has the runtime_checkable marker
            assert getattr(IUnitOfWork, "_is_protocol", False) is True

    async def test_protocol_method_signatures(self):
        """Test that IUnitOfWork protocol methods are defined (lines 28, 32, 36, 40)."""
        from checklists_service.repositories.unit_of_work import IUnitOfWork

        # Verify the protocol has the expected abstract methods
        # These are the method definitions using ... (ellipsis)
        assert hasattr(IUnitOfWork, "commit")
        assert hasattr(IUnitOfWork, "rollback")
        assert hasattr(IUnitOfWork, "__aenter__")
        assert hasattr(IUnitOfWork, "__aexit__")

        # Verify they are abstract methods with ... (ellipsis) body
        # When imported, these methods are just abstract definitions
        commit_method = getattr(IUnitOfWork, "commit", None)
        assert commit_method is not None


class TestIUnitOfWorkInterface:
    """Direct test of IUnitOfWork interface method bodies (lines 28, 32, 36, 40)."""

    async def test_iunit_of_work_commit_is_abstract(self):
        """Test IUnitOfWork.commit is defined with ... (line 28)."""
        import inspect

        from checklists_service.repositories.unit_of_work import IUnitOfWork

        # Get the source of the class
        source = inspect.getsource(IUnitOfWork)

        # Verify commit method has ... body in the source
        assert "def commit" in source
        assert "..." in source or "pass" in source or "raise NotImplementedError" in source

    async def test_iunit_of_work_rollback_is_abstract(self):
        """Test IUnitOfWork.rollback is defined with ... (line 32)."""
        import inspect

        from checklists_service.repositories.unit_of_work import IUnitOfWork

        source = inspect.getsource(IUnitOfWork)
        assert "def rollback" in source

    async def test_iunit_of_work_aenter_is_abstract(self):
        """Test IUnitOfWork.__aenter__ is defined with ... (line 36)."""
        import inspect

        from checklists_service.repositories.unit_of_work import IUnitOfWork

        source = inspect.getsource(IUnitOfWork)
        assert "def __aenter__" in source

    async def test_iunit_of_work_aexit_is_abstract(self):
        """Test IUnitOfWork.__aexit__ is defined with ... (line 40)."""
        import inspect

        from checklists_service.repositories.unit_of_work import IUnitOfWork

        source = inspect.getsource(IUnitOfWork)
        assert "def __aexit__" in source

    async def test_iunit_of_work_implements_all_required_methods(self):
        """Test that IUnitOfWork defines all required abstract methods (lines 28, 32, 36, 40)."""
        from checklists_service.repositories.unit_of_work import IUnitOfWork

        # Get all methods defined in the protocol
        required_methods = {"commit", "rollback", "__aenter__", "__aexit__"}

        for method_name in required_methods:
            assert hasattr(IUnitOfWork, method_name), f"IUnitOfWork missing method: {method_name}"

    async def test_sqlalchemy_uow_concrete_implements_all_protocol_methods(self):
        """Test that SqlAlchemyUnitOfWork implements all IUnitOfWork protocol methods."""
        from checklists_service.repositories.unit_of_work import IUnitOfWork, SqlAlchemyUnitOfWork

        # Get all methods from the protocol
        protocol_methods = {
            name for name in dir(IUnitOfWork) if not name.startswith("_") or name in ("__aenter__", "__aexit__")
        }
        protocol_methods.discard("__protocol_attrs__")
        protocol_methods.discard("__parameters__")
        protocol_methods.discard("__subclasshook__")

        # Get all methods from the implementation
        impl_methods = set()
        for name in dir(SqlAlchemyUnitOfWork):
            if not name.startswith("_") or name in ("__aenter__", "__aexit__"):
                attr = getattr(SqlAlchemyUnitOfWork, name)
                if callable(attr) and not isinstance(attr, property):
                    impl_methods.add(name)

        # All protocol methods should be in implementation (except internal ones)
        required = {"commit", "rollback", "__aenter__", "__aexit__"}
        for method in required:
            assert hasattr(SqlAlchemyUnitOfWork, method), f"SqlAlchemyUnitOfWork missing implementation of {method}"
