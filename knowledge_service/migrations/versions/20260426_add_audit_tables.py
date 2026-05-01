"""
add_audit_tables.

Revision ID: c3d4e5f6g7h8
Revises: 0444f265d1b2
Create Date: 2026-04-26 10:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6g7h8"
down_revision: str | None = "0444f265d1b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Extend search_history table with context column
    op.add_column("search_history", sa.Column("context", sa.JSON(), nullable=True))

    # Article change history table
    op.create_table(
        "article_change_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_title", sa.Text(), nullable=True),
        sa.Column("new_title", sa.Text(), nullable=True),
        sa.Column("old_content", sa.Text(), nullable=True),
        sa.Column("new_content", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_article_change_history_article_id_changed_at"), "article_change_history", ["article_id", "changed_at"])

    # Article view history table
    op.create_table(
        "article_view_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("viewed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("level", sa.String(length=50), nullable=True),
        sa.Column("referrer", sa.Text(), nullable=True),
        sa.Column("session_id", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_article_view_history_article_id"), "article_view_history", ["article_id"])
    op.create_index(op.f("ix_article_view_history_user_id"), "article_view_history", ["user_id"])
    op.create_index(op.f("ix_article_view_history_viewed_at"), "article_view_history", ["viewed_at"])

    # Category change history table
    op.create_table(
        "category_change_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_name", sa.Text(), nullable=True),
        sa.Column("new_name", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_category_change_history_category_id_changed_at"), "category_change_history", ["category_id", "changed_at"])

    # Dialogue scenario change history table
    op.create_table(
        "dialogue_scenario_change_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_name", sa.Text(), nullable=True),
        sa.Column("new_name", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["scenario_id"], ["dialogue_scenarios.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dialogue_scenario_change_history_scenario_id_changed_at"), "dialogue_scenario_change_history", ["scenario_id", "changed_at"])


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_dialogue_scenario_change_history_scenario_id_changed_at"), table_name="dialogue_scenario_change_history")
    op.drop_table("dialogue_scenario_change_history")

    op.drop_index(op.f("ix_category_change_history_category_id_changed_at"), table_name="category_change_history")
    op.drop_table("category_change_history")

    op.drop_index(op.f("ix_article_view_history_viewed_at"), table_name="article_view_history")
    op.drop_index(op.f("ix_article_view_history_user_id"), table_name="article_view_history")
    op.drop_index(op.f("ix_article_view_history_article_id"), table_name="article_view_history")
    op.drop_table("article_view_history")

    op.drop_index(op.f("ix_article_change_history_article_id_changed_at"), table_name="article_change_history")
    op.drop_table("article_change_history")

    op.drop_column("search_history", "context")
