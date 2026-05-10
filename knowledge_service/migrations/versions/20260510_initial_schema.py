"""
initial_schema.

Revision ID: 20260510_knowledge_initial
Revises:
Create Date: 2026-05-10 00:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260510_knowledge_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # From knowledge_service/migrations/versions/20260425_1440_initial_schema.py
    op.create_table(
        "dialogue_scenarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dialogue_scenarios_category"), "dialogue_scenarios", ["category"], unique=False)
    op.create_index(op.f("ix_dialogue_scenarios_display_order"), "dialogue_scenarios", ["display_order"], unique=False)
    op.create_index(op.f("ix_dialogue_scenarios_id"), "dialogue_scenarios", ["id"], unique=False)
    op.create_index(op.f("ix_dialogue_scenarios_is_active"), "dialogue_scenarios", ["is_active"], unique=False)
    op.create_index(op.f("ix_dialogue_scenarios_title"), "dialogue_scenarios", ["title"], unique=False)
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("usage_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tags_id"), "tags", ["id"], unique=False)
    op.create_index(op.f("ix_tags_name"), "tags", ["name"], unique=True)
    op.create_index(op.f("ix_tags_slug"), "tags", ["slug"], unique=True)
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("level", sa.String(length=50), nullable=True),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)
    op.create_index(op.f("ix_categories_department_id"), "categories", ["department_id"], unique=False)
    op.create_index(op.f("ix_categories_level"), "categories", ["level"], unique=False)
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=False)
    op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=True)
    op.create_table(
        "dialogue_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        sa.Column("step_number", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer_type", sa.String(length=50), nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("answer_content", sa.Text(), nullable=True),
        sa.Column("next_step_id", sa.Integer(), nullable=True),
        sa.Column("parent_step_id", sa.Integer(), nullable=True),
        sa.Column("is_final", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["next_step_id"], ["dialogue_steps.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["parent_step_id"], ["dialogue_steps.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["scenario_id"], ["dialogue_scenarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dialogue_steps_id"), "dialogue_steps", ["id"], unique=False)
    op.create_index(op.f("ix_dialogue_steps_scenario_id"), "dialogue_steps", ["scenario_id"], unique=False)
    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("query", sa.String(length=500), nullable=False),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("results_count", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_search_history_id"), "search_history", ["id"], unique=False)
    op.create_index(op.f("ix_search_history_query"), "search_history", ["query"], unique=False)
    op.create_index(op.f("ix_search_history_user_id"), "search_history", ["user_id"], unique=False)
    op.create_index(op.f("ix_search_history_department_id"), "search_history", ["department_id"], unique=False)
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("slug", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("author_name", sa.String(length=200), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("level", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("is_pinned", sa.Boolean(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("view_count", sa.Integer(), nullable=False),
        sa.Column("meta_title", sa.String(length=200), nullable=True),
        sa.Column("meta_description", sa.String(length=500), nullable=True),
        sa.Column("keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_articles_author_id"), "articles", ["author_id"], unique=False)
    op.create_index(op.f("ix_articles_department_id"), "articles", ["department_id"], unique=False)
    op.create_index(op.f("ix_articles_id"), "articles", ["id"], unique=False)
    op.create_index(op.f("ix_articles_level"), "articles", ["level"], unique=False)
    op.create_index(op.f("ix_articles_search_vector"), "articles", ["search_vector"], unique=False)
    op.create_index(op.f("ix_articles_slug"), "articles", ["slug"], unique=True)
    op.create_index(op.f("ix_articles_status"), "articles", ["status"], unique=False)
    op.create_index(op.f("ix_articles_title"), "articles", ["title"], unique=False)
    op.create_table(
        "article_tags",
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"]),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"]),
        sa.PrimaryKeyConstraint("article_id", "tag_id"),
    )
    op.create_table(
        "article_views",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("viewed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_article_views_article_id"), "article_views", ["article_id"], unique=False)
    op.create_index(op.f("ix_article_views_id"), "article_views", ["id"], unique=False)
    op.create_index(op.f("ix_article_views_user_id"), "article_views", ["user_id"], unique=False)
    op.create_index(op.f("ix_article_views_viewed_at"), "article_views", ["viewed_at"], unique=False)
    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("type", sa.Enum("FILE", "LINK", "EMBED", name="attachmenttype"), nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_downloadable", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attachments_article_id"), "attachments", ["article_id"], unique=False)
    op.create_index(op.f("ix_attachments_id"), "attachments", ["id"], unique=False)
    op.create_index(op.f("ix_attachments_type"), "attachments", ["type"], unique=False)

    # From knowledge_service/migrations/versions/20260426_add_audit_tables.py
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_article_change_history_article_id_changed_at"), "article_change_history", ["article_id", "changed_at"]
    )

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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_category_change_history_category_id_changed_at"),
        "category_change_history",
        ["category_id", "changed_at"],
    )

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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_dialogue_scenario_change_history_scenario_id_changed_at"),
        "dialogue_scenario_change_history",
        ["scenario_id", "changed_at"],
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # From knowledge_service/migrations/versions/20260426_add_audit_tables.py
    op.drop_index(
        op.f("ix_dialogue_scenario_change_history_scenario_id_changed_at"),
        table_name="dialogue_scenario_change_history",
    )
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

    # From knowledge_service/migrations/versions/20260425_1440_initial_schema.py
    op.drop_index(op.f("ix_attachments_type"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_id"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_article_id"), table_name="attachments")
    op.drop_table("attachments")
    op.drop_index(op.f("ix_article_views_viewed_at"), table_name="article_views")
    op.drop_index(op.f("ix_article_views_user_id"), table_name="article_views")
    op.drop_index(op.f("ix_article_views_id"), table_name="article_views")
    op.drop_index(op.f("ix_article_views_article_id"), table_name="article_views")
    op.drop_table("article_views")
    op.drop_table("article_tags")
    op.drop_index(op.f("ix_articles_title"), table_name="articles")
    op.drop_index(op.f("ix_articles_status"), table_name="articles")
    op.drop_index(op.f("ix_articles_slug"), table_name="articles")
    op.drop_index(op.f("ix_articles_search_vector"), table_name="articles")
    op.drop_index(op.f("ix_articles_level"), table_name="articles")
    op.drop_index(op.f("ix_articles_id"), table_name="articles")
    op.drop_index(op.f("ix_articles_department_id"), table_name="articles")
    op.drop_index(op.f("ix_articles_author_id"), table_name="articles")
    op.drop_table("articles")
    op.drop_index(op.f("ix_search_history_department_id"), table_name="search_history")
    op.drop_index(op.f("ix_search_history_user_id"), table_name="search_history")
    op.drop_index(op.f("ix_search_history_query"), table_name="search_history")
    op.drop_index(op.f("ix_search_history_id"), table_name="search_history")
    op.drop_table("search_history")
    op.drop_index(op.f("ix_dialogue_steps_scenario_id"), table_name="dialogue_steps")
    op.drop_index(op.f("ix_dialogue_steps_id"), table_name="dialogue_steps")
    op.drop_table("dialogue_steps")
    op.drop_index(op.f("ix_categories_slug"), table_name="categories")
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_index(op.f("ix_categories_level"), table_name="categories")
    op.drop_index(op.f("ix_categories_department_id"), table_name="categories")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")
    op.drop_index(op.f("ix_tags_slug"), table_name="tags")
    op.drop_index(op.f("ix_tags_name"), table_name="tags")
    op.drop_index(op.f("ix_tags_id"), table_name="tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_dialogue_scenarios_title"), table_name="dialogue_scenarios")
    op.drop_index(op.f("ix_dialogue_scenarios_is_active"), table_name="dialogue_scenarios")
    op.drop_index(op.f("ix_dialogue_scenarios_id"), table_name="dialogue_scenarios")
    op.drop_index(op.f("ix_dialogue_scenarios_display_order"), table_name="dialogue_scenarios")
    op.drop_index(op.f("ix_dialogue_scenarios_category"), table_name="dialogue_scenarios")
    op.drop_table("dialogue_scenarios")
