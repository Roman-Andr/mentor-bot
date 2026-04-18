"""Tag management service with repository pattern."""

from knowledge_service.core import NotFoundException, ValidationException
from knowledge_service.models import Tag
from knowledge_service.repositories import IUnitOfWork
from knowledge_service.schemas import TagCreate, TagUpdate


class TagService:
    """Service for tag management operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize tag service with Unit of Work."""
        self._uow = uow

    async def create_tag(self, tag_data: TagCreate) -> Tag:
        """Create new tag."""
        existing = await self._uow.tags.find_by_name_or_slug(tag_data.name, tag_data.slug)
        if existing:
            msg = "Tag with this name or slug already exists"
            raise ValidationException(msg)

        tag = Tag(
            name=tag_data.name,
            slug=tag_data.slug,
            description=tag_data.description,
        )

        created = await self._uow.tags.create(tag)
        await self._uow.commit()
        return created

    async def get_tag_by_id(self, tag_id: int) -> Tag:
        """Get tag by ID."""
        tag = await self._uow.tags.get_by_id_with_articles(tag_id)
        if not tag:
            msg = "Tag"
            raise NotFoundException(msg)
        return tag

    async def get_tag_by_slug(self, slug: str) -> Tag:
        """Get tag by slug."""
        tag = await self._uow.tags.get_by_slug(slug)
        if not tag:
            msg = "Tag"
            raise NotFoundException(msg)
        return tag

    async def update_tag(self, tag_id: int, update_data: TagUpdate) -> Tag:
        """Update tag."""
        tag = await self.get_tag_by_id(tag_id)

        if update_data.name:
            conflicting = await self._uow.tags.find_by_name_or_slug_excluding(update_data.name, tag.slug, tag_id)
            if conflicting:
                msg = "Another tag with this name or slug already exists"
                raise ValidationException(msg)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(tag, field, value)

        updated = await self._uow.tags.update(tag)
        await self._uow.commit()
        return updated

    async def delete_tag(self, tag_id: int) -> None:
        """Delete tag."""
        tag = await self.get_tag_by_id(tag_id)

        if tag.articles:
            msg = "Cannot delete tag that is in use by articles"
            raise ValidationException(msg)

        await self._uow.tags.delete(tag_id)
        await self._uow.commit()

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
        items, total = await self._uow.tags.find_tags(
            skip=skip,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )
        return list(items), total

    async def get_popular_tags(self, limit: int = 20) -> list[Tag]:
        """Get most popular tags by usage count."""
        items = await self._uow.tags.get_popular(limit)
        return list(items)

    async def get_tags_by_article(self, article_id: int) -> list[Tag]:
        """Get tags for a specific article."""
        items = await self._uow.tags.find_by_article(article_id)
        return list(items)

    async def merge_tags(self, source_tag_id: int, target_tag_id: int) -> Tag:
        """Merge two tags, moving all articles from source to target."""
        if source_tag_id == target_tag_id:
            msg = "Cannot merge tag with itself"
            raise ValidationException(msg)

        source_tag = await self.get_tag_by_id(source_tag_id)
        target_tag = await self.get_tag_by_id(target_tag_id)

        for article in list(source_tag.articles):
            if target_tag not in article.tags:
                article.tags.append(target_tag)
                target_tag.usage_count += 1
            article.tags.remove(source_tag)

        await self._uow.tags.delete(source_tag_id)
        await self._uow.tags.update(target_tag)
        await self._uow.commit()
        return target_tag
