from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.question import QuestionRead


class ResumeSummaryRead(BaseModel):
    summary: str = ""
    technical_stack: list[str] = Field(default_factory=list)
    seniority: str = "未知"
    project_themes: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    evidence_notes: list[str] = Field(default_factory=list)


class StrategyRead(BaseModel):
    target_role: str = "software engineer"
    interview_style: str = "standard"
    focus_areas: list[str] = Field(default_factory=list)
    emphasis: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    difficulty_distribution: dict[str, int] = Field(
        default_factory=lambda: {"easy": 6, "medium": 8, "hard": 6}
    )
    interview_tone: str = "真实程序员技术面试"


class InterviewRegenerateRequest(BaseModel):
    target_role: str | None = None
    interview_style: str | None = None


class InterviewSetListItem(BaseModel):
    id: int
    title: str
    created_at: datetime
    resume_session_id: int
    resume_summary: ResumeSummaryRead
    total_question_count: int
    difficulty_breakdown: dict[str, int]
    target_role: str
    interview_style: str
    extraction_quality_score: float | None = None


class InterviewSetDetail(BaseModel):
    id: int
    title: str
    created_at: datetime
    resume_session_id: int
    meta_json: dict[str, Any]
    job_description_text: str | None = None
    resume_summary: ResumeSummaryRead
    strategy: StrategyRead
    total_question_count: int
    difficulty_breakdown: dict[str, int]
    target_role: str
    interview_style: str
    extraction_status: str
    extraction_quality_score: float | None = None
    extraction_error_message: str | None = None
    questions: list[QuestionRead]


class PaginatedInterviewSets(BaseModel):
    items: list[InterviewSetListItem]
    total: int
    page: int
    page_size: int


class FavoriteItem(BaseModel):
    favorite_id: int
    favorited_at: datetime
    question_id: int
    difficulty: str
    category: str
    question: str
    answer: str
    intent: str
    reference_from_resume: str
    source_question_set_id: int
    source_question_set_title: str
