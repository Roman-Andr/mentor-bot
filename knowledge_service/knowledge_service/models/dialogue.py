"""Dialogue scenario and step database models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from knowledge_service.core import DialogueAnswerType, DialogueCategory
from knowledge_service.database import Base

if TYPE_CHECKING:
    from knowledge_service.models import DialogueStep


class DialogueScenario(Base):
    """Dialogue scenario model for rule-based dialogues."""

    __tablename__ = "dialogue_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    category: Mapped[DialogueCategory] = mapped_column(String(50), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    steps: Mapped[list["DialogueStep"]] = relationship(
        "DialogueStep", back_populates="scenario", cascade="all, delete-orphan", order_by="DialogueStep.step_number"
    )

    def __repr__(self) -> str:
        """Representation of DialogueScenario."""
        return f"<DialogueScenario(id={self.id}, title={self.title}, category={self.category})>"


class DialogueStep(Base):
    """Dialogue step model for scenario steps."""

    __tablename__ = "dialogue_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("dialogue_scenarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer_type: Mapped[DialogueAnswerType] = mapped_column(String(50), nullable=False, default=DialogueAnswerType.TEXT)
    options: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    answer_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_step_id: Mapped[int | None] = mapped_column(
        ForeignKey("dialogue_steps.id", ondelete="SET NULL"), nullable=True
    )
    parent_step_id: Mapped[int | None] = mapped_column(
        ForeignKey("dialogue_steps.id", ondelete="SET NULL"), nullable=True
    )
    is_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    scenario: Mapped["DialogueScenario"] = relationship("DialogueScenario", back_populates="steps")
    next_step: Mapped["DialogueStep | None"] = relationship(
        "DialogueStep",
        foreign_keys=[next_step_id],
        remote_side="DialogueStep.id",
    )
    parent_step: Mapped["DialogueStep | None"] = relationship(
        "DialogueStep",
        foreign_keys=[parent_step_id],
        remote_side="DialogueStep.id",
    )

    def __repr__(self) -> str:
        """Representation of DialogueStep."""
        return f"<DialogueStep(id={self.id}, scenario_id={self.scenario_id}, step_number={self.step_number})>"
