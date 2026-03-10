from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import CreatedAtMixin


class Question(Base, CreatedAtMixin):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_set_id: Mapped[int] = mapped_column(
        ForeignKey("question_sets.id", ondelete="CASCADE"),
        index=True,
    )
    difficulty: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str] = mapped_column(Text, nullable=False)
    reference_from_resume: Mapped[str] = mapped_column(Text, nullable=False, default="")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    question_set: Mapped["QuestionSet"] = relationship(back_populates="questions")
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )
    user_answers: Mapped[list["UserAnswer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )
