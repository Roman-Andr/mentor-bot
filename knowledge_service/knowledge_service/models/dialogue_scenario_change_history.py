"""Dialogue scenario change history database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from knowledge_service.database import Base


class DialogueScenarioChangeHistory(Base):
    """Dialogue scenario change history model for audit."""

    __tablename__ = "dialogue_scenario_change_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("dialogue_scenarios.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    old_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Representation of DialogueScenarioChangeHistory."""
        return f"<DialogueScenarioChangeHistory(id={self.id}, scenario_id={self.scenario_id}, action={self.action})>"
