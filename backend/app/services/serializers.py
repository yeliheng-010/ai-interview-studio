from __future__ import annotations

from collections.abc import Iterable

from app.models import AnswerFeedback, Favorite, Question, QuestionSet, UserAnswer
from app.schemas.interview import (
    FavoriteItem,
    InterviewSetDetail,
    InterviewSetListItem,
    ResumeSummaryRead,
    StrategyRead,
)
from app.schemas.question import (
    AnswerFeedbackRead,
    QuestionDetail,
    QuestionRead,
    UserAnswerRead,
)
from app.utils.interview import DIFFICULTY_DISTRIBUTION


def build_difficulty_breakdown(questions: Iterable[Question]) -> dict[str, int]:
    breakdown = {key: 0 for key in DIFFICULTY_DISTRIBUTION}
    for question in questions:
        if question.difficulty in breakdown:
            breakdown[question.difficulty] += 1
    return breakdown


def feedback_to_schema(feedback: AnswerFeedback | None) -> AnswerFeedbackRead | None:
    if feedback is None:
        return None
    return AnswerFeedbackRead(
        id=feedback.id,
        score_json=feedback.score_json,
        strengths=feedback.strengths,
        weaknesses=feedback.weaknesses,
        suggestions=feedback.suggestions,
        improved_answer=feedback.improved_answer,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
    )


def user_answer_to_schema(user_answer: UserAnswer | None) -> UserAnswerRead | None:
    if user_answer is None:
        return None
    return UserAnswerRead(
        id=user_answer.id,
        question_id=user_answer.question_id,
        answer_text=user_answer.answer_text,
        created_at=user_answer.created_at,
        updated_at=user_answer.updated_at,
        feedback=feedback_to_schema(user_answer.feedback),
    )


def question_to_schema(question: Question, *, is_favorited: bool = False) -> QuestionRead:
    my_answer = user_answer_to_schema(question.user_answers[0] if question.user_answers else None)
    return QuestionRead(
        id=question.id,
        difficulty=question.difficulty,
        category=question.category,
        question=question.question_text,
        answer=question.answer_text,
        intent=question.intent,
        reference_from_resume=question.reference_from_resume,
        is_favorited=is_favorited,
        my_answer=my_answer,
        created_at=question.created_at,
    )


def question_to_detail(question: Question, *, is_favorited: bool = False) -> QuestionDetail:
    return QuestionDetail(
        **question_to_schema(question, is_favorited=is_favorited).model_dump(),
        question_set_id=question.question_set_id,
    )


def question_set_to_list_item(question_set: QuestionSet) -> InterviewSetListItem:
    resume_session = question_set.resume_session
    return InterviewSetListItem(
        id=question_set.id,
        title=question_set.title,
        created_at=question_set.created_at,
        resume_session_id=question_set.resume_session_id,
        resume_summary=ResumeSummaryRead.model_validate(resume_session.resume_summary_json),
        total_question_count=len(question_set.questions),
        difficulty_breakdown=build_difficulty_breakdown(question_set.questions),
        target_role=resume_session.target_role,
        interview_style=resume_session.interview_style,
        extraction_quality_score=resume_session.extraction_quality_score,
    )


def question_set_to_detail(
    question_set: QuestionSet,
    *,
    favorite_question_ids: set[int] | None = None,
) -> InterviewSetDetail:
    favorite_question_ids = favorite_question_ids or set()
    resume_session = question_set.resume_session
    questions = [
        question_to_schema(question, is_favorited=question.id in favorite_question_ids)
        for question in question_set.questions
    ]
    return InterviewSetDetail(
        id=question_set.id,
        title=question_set.title,
        created_at=question_set.created_at,
        resume_session_id=question_set.resume_session_id,
        meta_json=question_set.meta_json,
        job_description_text=resume_session.job_description_text,
        resume_summary=ResumeSummaryRead.model_validate(resume_session.resume_summary_json),
        strategy=StrategyRead.model_validate(resume_session.strategy_json),
        total_question_count=len(question_set.questions),
        difficulty_breakdown=build_difficulty_breakdown(question_set.questions),
        target_role=resume_session.target_role,
        interview_style=resume_session.interview_style,
        extraction_status=resume_session.extraction_status,
        extraction_quality_score=resume_session.extraction_quality_score,
        extraction_error_message=resume_session.extraction_error_message,
        questions=questions,
    )


def favorite_to_schema(favorite: Favorite) -> FavoriteItem:
    question = favorite.question
    question_set = question.question_set
    return FavoriteItem(
        favorite_id=favorite.id,
        favorited_at=favorite.created_at,
        question_id=question.id,
        difficulty=question.difficulty,
        category=question.category,
        question=question.question_text,
        answer=question.answer_text,
        intent=question.intent,
        reference_from_resume=question.reference_from_resume,
        source_question_set_id=question_set.id,
        source_question_set_title=question_set.title,
    )
