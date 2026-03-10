from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.db import get_db
from app.models import Favorite, Question, User
from app.schemas.interview import FavoriteItem
from app.services.serializers import favorite_to_schema

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteItem])
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FavoriteItem]:
    stmt = (
        select(Favorite)
        .join(Favorite.question)
        .join(Question.question_set)
        .where(Favorite.user_id == current_user.id)
        .options(joinedload(Favorite.question).joinedload(Question.question_set))
        .order_by(Favorite.created_at.desc())
    )
    favorites = db.execute(stmt).unique().scalars().all()
    return [favorite_to_schema(favorite) for favorite in favorites]
