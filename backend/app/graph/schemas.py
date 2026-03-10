from __future__ import annotations

from pydantic import BaseModel, Field


class ResumeAnalysisLLMOutput(BaseModel):
    summary: str
    technical_stack: list[str] = Field(default_factory=list)
    seniority: str = "未知"
    project_themes: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    evidence_notes: list[str] = Field(default_factory=list)


class InterviewStrategyLLMOutput(BaseModel):
    target_role: str = "software engineer"
    interview_style: str = "standard"
    focus_areas: list[str] = Field(default_factory=list)
    emphasis: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    difficulty_distribution: dict[str, int] = Field(
        default_factory=lambda: {"easy": 6, "medium": 8, "hard": 6}
    )
    interview_tone: str = "真实程序员技术面试"


class QAItemOutput(BaseModel):
    difficulty: str
    category: str
    question: str
    answer: str
    intent: str
    reference_from_resume: str = ""


class QAItemsLLMOutput(BaseModel):
    items: list[QAItemOutput] = Field(default_factory=list)


class FeedbackScoreOutput(BaseModel):
    overall: int = Field(ge=0, le=100)
    relevance: int = Field(ge=0, le=100)
    clarity: int = Field(ge=0, le=100)
    technical_depth: int = Field(ge=0, le=100)


class AnswerFeedbackLLMOutput(BaseModel):
    score_json: FeedbackScoreOutput
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    improved_answer: str
