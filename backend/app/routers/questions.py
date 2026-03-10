from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db import get_db
from app.models import Favorite, User
from app.schemas.question import (
    AnswerFeedbackRead,
    AnswerFeedbackRequest,
    FavoriteToggleResponse,
    QuestionDetail,
    QuestionRegenerateRequest,
    UserAnswerCreateRequest,
    UserAnswerRead,
    UserAnswerUpdateRequest,
)
from app.services.interview_service import get_question_for_user
from app.services.practice_service import PracticeService
from app.services.serializers import feedback_to_schema, question_to_detail, user_answer_to_schema

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/{question_id}", response_model=QuestionDetail)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionDetail:
    question = get_question_for_user(db, user_id=current_user.id, question_id=question_id, required=True)
    is_favorited = (
        db.scalar(
            select(Favorite).where(
                Favorite.user_id == current_user.id,
                Favorite.question_id == question_id,
            )
        )
        is not None
    )
    return question_to_detail(question, is_favorited=is_favorited)


@router.get("/{question_id}/my-answer", response_model=UserAnswerRead | None)
def get_my_answer(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserAnswerRead | None:
    service = PracticeService(db)
    return user_answer_to_schema(service.get_user_answer(user_id=current_user.id, question_id=question_id))


@router.post(
    "/{question_id}/my-answer",
    response_model=UserAnswerRead,
    status_code=status.HTTP_201_CREATED,
)
def create_my_answer(
    question_id: int,
    payload: UserAnswerCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserAnswerRead:
    service = PracticeService(db)
    answer = service.create_user_answer(
        user_id=current_user.id,
        question_id=question_id,
        payload=payload,
    )
    return user_answer_to_schema(answer)


@router.put("/{question_id}/my-answer", response_model=UserAnswerRead)
def update_my_answer(
    question_id: int,
    payload: UserAnswerUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserAnswerRead:
    service = PracticeService(db)
    answer = service.update_user_answer(
        user_id=current_user.id,
        question_id=question_id,
        payload=payload,
    )
    return user_answer_to_schema(answer)


@router.post("/{question_id}/feedback", response_model=AnswerFeedbackRead)
async def generate_feedback(
    question_id: int,
    payload: AnswerFeedbackRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnswerFeedbackRead:
    service = PracticeService(db)
    feedback = await service.generate_feedback(
        user_id=current_user.id,
        question_id=question_id,
        target_role=payload.target_role if payload else None,
        interview_style=payload.interview_style if payload else None,
    )
    return feedback_to_schema(feedback)


@router.post("/{question_id}/regenerate", response_model=QuestionDetail)
async def regenerate_question(
    question_id: int,
    payload: QuestionRegenerateRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionDetail:
    service = PracticeService(db)
    question = await service.regenerate_question(
        user_id=current_user.id,
        question_id=question_id,
        target_role=payload.target_role if payload else None,
        interview_style=payload.interview_style if payload else None,
    )
    is_favorited = (
        db.scalar(
            select(Favorite).where(
                Favorite.user_id == current_user.id,
                Favorite.question_id == question_id,
            )
        )
        is not None
    )
    return question_to_detail(question, is_favorited=is_favorited)


@router.post("/{question_id}/favorite", response_model=FavoriteToggleResponse)
def favorite_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteToggleResponse:
    get_question_for_user(db, user_id=current_user.id, question_id=question_id, required=True)
    favorite = db.scalar(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.question_id == question_id,
        )
    )
    if favorite is None:
        db.add(Favorite(user_id=current_user.id, question_id=question_id))
        db.commit()
    return FavoriteToggleResponse(question_id=question_id, is_favorited=True)


@router.delete("/{question_id}/favorite", response_model=FavoriteToggleResponse)
def unfavorite_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteToggleResponse:
    get_question_for_user(db, user_id=current_user.id, question_id=question_id, required=True)
    favorite = db.scalar(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.question_id == question_id,
        )
    )
    if favorite is not None:
        db.delete(favorite)
        db.commit()
    return FavoriteToggleResponse(question_id=question_id, is_favorited=False)
