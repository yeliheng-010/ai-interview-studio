from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    resume_sessions: Mapped[list["ResumeSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    question_sets: Mapped[list["QuestionSet"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_answers: Mapped[list["UserAnswer"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
