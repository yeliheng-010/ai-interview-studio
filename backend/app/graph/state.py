from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class InterviewGraphState(TypedDict, total=False):
    user_id: int
    file_name: str
    pdf_bytes: bytes
    raw_text: str
    cleaned_text: str
    extraction_status: str
    extraction_quality_score: float
    extraction_error_message: str | None
    target_role: str
    interview_style: str
    resume_summary: dict[str, Any]
    strategy: dict[str, Any]
    easy_items: list[dict[str, Any]]
    medium_items: list[dict[str, Any]]
    hard_items: list[dict[str, Any]]
    final_items: list[dict[str, Any]]
    title: str
    meta: dict[str, Any]
    errors: list[str]


class QuestionRegenerationState(TypedDict, total=False):
    user_id: int
    question_id: int
    difficulty: str
    sort_order: int
    cleaned_text: str
    resume_summary: dict[str, Any]
    strategy: dict[str, Any]
    target_role: str
    interview_style: str
    existing_questions: list[str]
    original_question: str
    generated_item: dict[str, Any]
    final_item: dict[str, Any]
    errors: list[str]


class AnswerFeedbackState(TypedDict, total=False):
    user_id: int
    question_id: int
    question_text: str
    reference_answer: str
    user_answer: str
    target_role: str
    interview_style: str
    feedback: dict[str, Any]
    errors: list[str]
