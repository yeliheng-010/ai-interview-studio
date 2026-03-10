from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AnswerFeedbackRead(BaseModel):
    id: int
    score_json: dict[str, int]
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    improved_answer: str
    created_at: datetime
    updated_at: datetime


class UserAnswerCreateRequest(BaseModel):
    answer_text: str = Field(min_length=20, max_length=5000)


class UserAnswerUpdateRequest(BaseModel):
    answer_text: str = Field(min_length=20, max_length=5000)


class AnswerFeedbackRequest(BaseModel):
    target_role: str | None = None
    interview_style: str | None = None


class QuestionRegenerateRequest(BaseModel):
    target_role: str | None = None
    interview_style: str | None = None


class UserAnswerRead(BaseModel):
    id: int
    question_id: int
    answer_text: str
    created_at: datetime
    updated_at: datetime
    feedback: AnswerFeedbackRead | None = None


class QuestionRead(BaseModel):
    id: int
    difficulty: str
    category: str
    question: str
    answer: str
    intent: str
    reference_from_resume: str
    is_favorited: bool = False
    my_answer: UserAnswerRead | None = None
    created_at: datetime


class QuestionDetail(QuestionRead):
    question_set_id: int


class FavoriteToggleResponse(BaseModel):
    question_id: int
    is_favorited: bool
