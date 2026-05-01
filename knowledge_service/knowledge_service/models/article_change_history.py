"""Article change history database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from knowledge_service.database import Base

if TYPE_CHECKING:
    from knowledge_service.models import Article, User


class ArticleChangeHistory(Base):
    """Article change history model for audit."""

    __tablename__ = "article_change_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    old_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    old_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Representation of ArticleChangeHistory."""
        return f"<ArticleChangeHistory(id={self.id}, article_id={self.article_id}, action={self.action})>"
