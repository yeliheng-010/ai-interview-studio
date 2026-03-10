from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class UserAnswer(Base, TimestampMixin):
    __tablename__ = "user_answers"
    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_answers_user_question"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="user_answers")
    question: Mapped["Question"] = relationship(back_populates="user_answers")
    feedback: Mapped["AnswerFeedback | None"] = relationship(
        back_populates="user_answer",
        cascade="all, delete-orphan",
        uselist=False,
    )
