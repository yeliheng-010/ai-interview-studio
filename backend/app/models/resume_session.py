from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import CreatedAtMixin, JSONVariant


class ResumeSession(Base, CreatedAtMixin):
    __tablename__ = "resume_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    cleaned_text: Mapped[str] = mapped_column(Text, nullable=False)
    extraction_status: Mapped[str] = mapped_column(String(32), nullable=False, default="validated")
    extraction_quality_score: Mapped[float | None] = mapped_column(nullable=True)
    extraction_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_role: Mapped[str] = mapped_column(String(64), nullable=False, default="software engineer")
    interview_style: Mapped[str] = mapped_column(String(64), nullable=False, default="standard")
    job_description_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_summary_json: Mapped[dict] = mapped_column(JSONVariant, nullable=False, default=dict)
    strategy_json: Mapped[dict] = mapped_column(JSONVariant, nullable=False, default=dict)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=20)

    user: Mapped["User"] = relationship(back_populates="resume_sessions")
    question_sets: Mapped[list["QuestionSet"]] = relationship(
        back_populates="resume_session",
        cascade="all, delete-orphan",
    )
