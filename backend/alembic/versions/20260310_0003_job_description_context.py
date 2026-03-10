"""add job description context to resume sessions"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260310_0003"
down_revision = "20260309_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("resume_sessions", sa.Column("job_description_text", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("resume_sessions", "job_description_text")
