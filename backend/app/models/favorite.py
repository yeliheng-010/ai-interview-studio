from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import CreatedAtMixin


class Favorite(Base, CreatedAtMixin):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_favorites_user_question"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)

    user: Mapped["User"] = relationship(back_populates="favorites")
    question: Mapped["Question"] = relationship(back_populates="favorites")
