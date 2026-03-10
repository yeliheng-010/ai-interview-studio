"""initial schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260309_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "resume_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("cleaned_text", sa.Text(), nullable=False),
        sa.Column("resume_summary_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("strategy_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_resume_sessions_user_id"), "resume_sessions", ["user_id"], unique=False)

    op.create_table(
        "question_sets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "resume_session_id",
            sa.Integer(),
            sa.ForeignKey("resume_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("meta_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_question_sets_user_id"), "question_sets", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_question_sets_resume_session_id"),
        "question_sets",
        ["resume_session_id"],
        unique=False,
    )

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "question_set_id",
            sa.Integer(),
            sa.ForeignKey("question_sets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("difficulty", sa.String(length=16), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("intent", sa.Text(), nullable=False),
        sa.Column("reference_from_resume", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_questions_question_set_id"), "questions", ["question_set_id"], unique=False)
    op.create_index(op.f("ix_questions_difficulty"), "questions", ["difficulty"], unique=False)

    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "question_id", name="uq_favorites_user_question"),
    )
    op.create_index(op.f("ix_favorites_user_id"), "favorites", ["user_id"], unique=False)
    op.create_index(op.f("ix_favorites_question_id"), "favorites", ["question_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_favorites_question_id"), table_name="favorites")
    op.drop_index(op.f("ix_favorites_user_id"), table_name="favorites")
    op.drop_table("favorites")

    op.drop_index(op.f("ix_questions_difficulty"), table_name="questions")
    op.drop_index(op.f("ix_questions_question_set_id"), table_name="questions")
    op.drop_table("questions")

    op.drop_index(op.f("ix_question_sets_resume_session_id"), table_name="question_sets")
    op.drop_index(op.f("ix_question_sets_user_id"), table_name="question_sets")
    op.drop_table("question_sets")

    op.drop_index(op.f("ix_resume_sessions_user_id"), table_name="resume_sessions")
    op.drop_table("resume_sessions")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
