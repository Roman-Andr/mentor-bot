from datetime import datetime

from feedback_service.database import Base
from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column


class Comment(Base):
    """Model for comments and suggestions."""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
