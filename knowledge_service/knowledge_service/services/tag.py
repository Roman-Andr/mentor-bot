"""Tag management service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from knowledge_service.core import NotFoundException, ValidationException
from knowledge_service.models import Tag
from knowledge_service.schemas import TagCreate, TagUpdate


class TagService:
    """Service for tag management operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize tag service with database session."""
        self.db = db

    async def create_tag(self, tag_data: TagCreate) -> Tag:
        """Create new tag."""
        # Check for duplicate name or slug
        stmt = select(Tag).where((Tag.name == tag_data.name) | (Tag.slug == tag_data.slug))
        result = await self.db.execute(stmt)
        existing_tag = result.scalar_one_or_none()

        if existing_tag:
            msg = "Tag with this name or slug already exists"
            raise ValidationException(msg)

        tag = Tag(
            name=tag_data.name,
            slug=tag_data.slug,
            description=tag_data.description,
        )

        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)

        return tag

    async def get_tag_by_id(self, tag_id: int) -> Tag:
        """Get tag by ID."""
        stmt = select(Tag).where(Tag.id == tag_id).options(selectinload(Tag.articles))
        result = await self.db.execute(stmt)
        tag = result.scalar_one_or_none()

        if not tag:
            msg = "Tag"
            raise NotFoundException(msg)

        return tag

    async def get_tag_by_slug(self, slug: str) -> Tag:
        """Get tag by slug."""
        stmt = select(Tag).where(Tag.slug == slug).options(selectinload(Tag.articles))
        result = await self.db.execute(stmt)
        tag = result.scalar_one_or_none()

        if not tag:
            msg = "Tag"
            raise NotFoundException(msg)

        return tag

    async def update_tag(self, tag_id: int, update_data: TagUpdate) -> Tag:
        """Update tag."""
        tag = await self.get_tag_by_id(tag_id)

        # Check for conflicts if name or slug is being changed
        if update_data.name or update_data.slug:
            new_name = update_data.name or tag.name
            new_slug = update_data.slug or tag.slug

            stmt = select(Tag).where(((Tag.name == new_name) | (Tag.slug == new_slug)) & (Tag.id != tag_id))
            result = await self.db.execute(stmt)
            conflicting_tag = result.scalar_one_or_none()

            if conflicting_tag:
                msg = "Another tag with this name or slug already exists"
                raise ValidationException(msg)

        # Update fields
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(tag, field, value)

        await self.db.commit()
        await self.db.refresh(tag)

        return tag

    async def delete_tag(self, tag_id: int) -> None:
        """Delete tag."""
        tag = await self.get_tag_by_id(tag_id)

        # Check if tag is being used
        if tag.articles:
            msg = "Cannot delete tag that is in use by articles"
            raise ValidationException(msg)

        await self.db.delete(tag)
        await self.db.commit()

    async def get_tags(
        self,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
        sort_by: str = "usage_count",
        *,
        sort_desc: bool = True,
    ) -> tuple[list[Tag], int]:
        """Get paginated list of tags with filters."""
        stmt = select(Tag)
        count_stmt = select(func.count(Tag.id))

        if search:
            stmt = stmt.where(Tag.name.ilike(f"%{search}%"))
            count_stmt = count_stmt.where(Tag.name.ilike(f"%{search}%"))

        # Apply sorting
        if sort_by == "name":
            stmt = stmt.order_by(Tag.name.desc() if sort_desc else Tag.name.asc())
        elif sort_by == "created_at":
            stmt = stmt.order_by(Tag.created_at.desc() if sort_desc else Tag.created_at.asc())
        else:  # usage_count is default
            stmt = stmt.order_by(Tag.usage_count.desc() if sort_desc else Tag.usage_count.asc())

        result = await self.db.execute(count_stmt)
        total = result.scalar_one()

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        tags = list(result.scalars().all())

        return tags, total

    async def get_popular_tags(self, limit: int = 20) -> list[Tag]:
        """Get most popular tags by usage count."""
        stmt = select(Tag).order_by(Tag.usage_count.desc(), Tag.name).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_tags_by_article(self, article_id: int) -> list[Tag]:
        """Get tags for a specific article."""
        stmt = select(Tag).where(Tag.articles.any(id=article_id))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def merge_tags(self, source_tag_id: int, target_tag_id: int) -> Tag:
        """Merge two tags, moving all articles from source to target."""
        if source_tag_id == target_tag_id:
            msg = "Cannot merge tag with itself"
            raise ValidationException(msg)

        source_tag = await self.get_tag_by_id(source_tag_id)
        target_tag = await self.get_tag_by_id(target_tag_id)

        # Move all articles from source to target
        for article in list(source_tag.articles):
            if target_tag not in article.tags:
                article.tags.append(target_tag)
                target_tag.usage_count += 1

            article.tags.remove(source_tag)

        # Delete source tag
        await self.db.delete(source_tag)
        await self.db.commit()
        await self.db.refresh(target_tag)

        return target_tag
