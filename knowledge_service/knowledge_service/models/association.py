"""Association tables for many-to-many relationships."""

from sqlalchemy import Column, ForeignKey, Integer, Table

from knowledge_service.database import Base

# Association table for many-to-many relationship between articles and tags
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)
