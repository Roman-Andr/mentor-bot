"""SQLAlchemy implementation of Tag repository."""

from collections.abc import Sequence
from typing import cast

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from knowledge_service.models import Tag
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.tag import ITagRepository


class TagRepository(SqlAlchemyBaseRepository[Tag, int], ITagRepository):
    """SQLAlchemy implementation of Tag repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize tag repository."""
        super().__init__(session, Tag)

    async def get_by_slug(self, slug: str) -> Tag | None:
        """Retrieve tag by slug with articles."""
        stmt = select(Tag).where(Tag.slug == slug).options(selectinload(Tag.articles))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_articles(self, entity_id: int) -> Tag | None:
        """Retrieve tag by ID with associated articles."""
        stmt = select(Tag).where(Tag.id == entity_id).options(selectinload(Tag.articles))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name_or_slug(self, name: str, slug: str) -> Tag | None:
        """Find tag by name or slug."""
        stmt = select(Tag).where(or_(Tag.name == name, Tag.slug == slug))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name_or_slug_excluding(self, name: str, slug: str, exclude_id: int) -> Tag | None:
        """Find tag by name or slug, excluding a specific ID."""
        stmt = select(Tag).where(
            or_(Tag.name == name, Tag.slug == slug),
            Tag.id != exclude_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_tags(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        sort_by: str = "usage_count",
        sort_desc: bool = True,
    ) -> tuple[Sequence[Tag], int]:
        """Find tags with search and sorting options."""
        stmt = select(Tag)
        count_stmt = select(func.count(Tag.id))

        if search:
            search_filter = Tag.name.ilike(f"%{search}%")
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        if sort_by == "name":
            stmt = stmt.order_by(Tag.name.desc() if sort_desc else Tag.name.asc())
        elif sort_by == "created_at":
            stmt = stmt.order_by(Tag.created_at.desc() if sort_desc else Tag.created_at.asc())
        else:
            stmt = stmt.order_by(Tag.usage_count.desc() if sort_desc else Tag.usage_count.asc())

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    async def get_popular(self, limit: int = 20) -> Sequence[Tag]:
        """Get most popular tags by usage count."""
        stmt = select(Tag).order_by(Tag.usage_count.desc(), Tag.name).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_by_article(self, article_id: int) -> Sequence[Tag]:
        """Find all tags associated with an article."""
        stmt = select(Tag).where(Tag.articles.any(id=article_id))
        result = await self._session.execute(stmt)
        return result.scalars().all()
