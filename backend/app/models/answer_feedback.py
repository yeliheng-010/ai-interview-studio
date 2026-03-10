from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import JSONVariant, TimestampMixin


class AnswerFeedback(Base, TimestampMixin):
    __tablename__ = "answer_feedback"
    __table_args__ = (
        UniqueConstraint("user_answer_id", name="uq_answer_feedback_user_answer"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_answer_id: Mapped[int] = mapped_column(
        ForeignKey("user_answers.id", ondelete="CASCADE"),
        index=True,
    )
    score_json: Mapped[dict] = mapped_column(JSONVariant, nullable=False, default=dict)
    strengths: Mapped[list[str]] = mapped_column(JSONVariant, nullable=False, default=list)
    weaknesses: Mapped[list[str]] = mapped_column(JSONVariant, nullable=False, default=list)
    suggestions: Mapped[list[str]] = mapped_column(JSONVariant, nullable=False, default=list)
    improved_answer: Mapped[str] = mapped_column(Text, nullable=False)

    user_answer: Mapped["UserAnswer"] = relationship(back_populates="feedback")
