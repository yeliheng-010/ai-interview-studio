"""practice and extraction extensions"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260309_0002"
down_revision = "20260309_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("resume_sessions", sa.Column("extraction_status", sa.String(length=32), nullable=True))
    op.add_column("resume_sessions", sa.Column("extraction_quality_score", sa.Float(), nullable=True))
    op.add_column("resume_sessions", sa.Column("extraction_error_message", sa.Text(), nullable=True))
    op.add_column("resume_sessions", sa.Column("target_role", sa.String(length=64), nullable=True))
    op.add_column("resume_sessions", sa.Column("interview_style", sa.String(length=64), nullable=True))
    op.execute("UPDATE resume_sessions SET extraction_status = 'validated' WHERE extraction_status IS NULL")
    op.execute("UPDATE resume_sessions SET target_role = 'software engineer' WHERE target_role IS NULL")
    op.execute("UPDATE resume_sessions SET interview_style = 'standard' WHERE interview_style IS NULL")
    op.alter_column("resume_sessions", "extraction_status", nullable=False)
    op.alter_column("resume_sessions", "target_role", nullable=False)
    op.alter_column("resume_sessions", "interview_style", nullable=False)

    op.create_table(
        "user_answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "question_id", name="uq_user_answers_user_question"),
    )
    op.create_index(op.f("ix_user_answers_user_id"), "user_answers", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_answers_question_id"), "user_answers", ["question_id"], unique=False)

    op.create_table(
        "answer_feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_answer_id",
            sa.Integer(),
            sa.ForeignKey("user_answers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("strengths", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("weaknesses", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("suggestions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("improved_answer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_answer_id", name="uq_answer_feedback_user_answer"),
    )
    op.create_index(op.f("ix_answer_feedback_user_answer_id"), "answer_feedback", ["user_answer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_answer_feedback_user_answer_id"), table_name="answer_feedback")
    op.drop_table("answer_feedback")

    op.drop_index(op.f("ix_user_answers_question_id"), table_name="user_answers")
    op.drop_index(op.f("ix_user_answers_user_id"), table_name="user_answers")
    op.drop_table("user_answers")

    op.drop_column("resume_sessions", "interview_style")
    op.drop_column("resume_sessions", "target_role")
    op.drop_column("resume_sessions", "extraction_error_message")
    op.drop_column("resume_sessions", "extraction_quality_score")
    op.drop_column("resume_sessions", "extraction_status")
