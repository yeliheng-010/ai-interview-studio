from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import CreatedAtMixin, JSONVariant


class QuestionSet(Base, CreatedAtMixin):
    __tablename__ = "question_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    resume_session_id: Mapped[int] = mapped_column(
        ForeignKey("resume_sessions.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    meta_json: Mapped[dict] = mapped_column(JSONVariant, nullable=False, default=dict)

    user: Mapped["User"] = relationship(back_populates="question_sets")
    resume_session: Mapped["ResumeSession"] = relationship(back_populates="question_sets")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="question_set",
        cascade="all, delete-orphan",
        order_by="Question.sort_order",
    )
