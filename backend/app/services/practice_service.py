from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.llm import LLMError
from app.graph.practice import AnswerFeedbackGraphRunner, QuestionRegenerationGraphRunner
from app.models import AnswerFeedback, UserAnswer
from app.schemas.question import UserAnswerCreateRequest, UserAnswerUpdateRequest
from app.services.interview_service import get_question_for_user, get_question_set_for_user


class PracticeService:
    def __init__(
        self,
        db: Session,
        *,
        feedback_runner: AnswerFeedbackGraphRunner | None = None,
        regeneration_runner: QuestionRegenerationGraphRunner | None = None,
    ) -> None:
        self.db = db
        self.feedback_runner = feedback_runner or AnswerFeedbackGraphRunner()
        self.regeneration_runner = regeneration_runner or QuestionRegenerationGraphRunner()

    def get_user_answer(self, *, user_id: int, question_id: int) -> UserAnswer | None:
        get_question_for_user(self.db, user_id=user_id, question_id=question_id, required=True)
        return self.db.scalar(
            select(UserAnswer).where(
                UserAnswer.user_id == user_id,
                UserAnswer.question_id == question_id,
            )
        )

    def create_user_answer(
        self,
        *,
        user_id: int,
        question_id: int,
        payload: UserAnswerCreateRequest,
    ) -> UserAnswer:
        get_question_for_user(self.db, user_id=user_id, question_id=question_id, required=True)
        existing = self.get_user_answer(user_id=user_id, question_id=question_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your answer already exists. Use PUT to update it.",
            )

        answer = UserAnswer(
            user_id=user_id,
            question_id=question_id,
            answer_text=payload.answer_text.strip(),
        )
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def update_user_answer(
        self,
        *,
        user_id: int,
        question_id: int,
        payload: UserAnswerUpdateRequest,
    ) -> UserAnswer:
        answer = self.get_user_answer(user_id=user_id, question_id=question_id)
        if answer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User answer not found.")

        answer.answer_text = payload.answer_text.strip()
        if answer.feedback is not None:
            self.db.delete(answer.feedback)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    async def generate_feedback(
        self,
        *,
        user_id: int,
        question_id: int,
        target_role: str | None = None,
        interview_style: str | None = None,
    ) -> AnswerFeedback:
        question = get_question_for_user(self.db, user_id=user_id, question_id=question_id, required=True)
        answer = self.get_user_answer(user_id=user_id, question_id=question_id)
        if answer is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please save your own answer before requesting feedback.",
            )

        resume_session = question.question_set.resume_session
        try:
            state = await self.feedback_runner.run(
                user_id=user_id,
                question_id=question_id,
                question_text=question.question_text,
                reference_answer=question.answer_text,
                user_answer=answer.answer_text,
                target_role=target_role or resume_session.target_role,
                interview_style=interview_style or resume_session.interview_style,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except LLMError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        if answer.feedback is None:
            answer.feedback = AnswerFeedback(
                score_json=state["feedback"]["score_json"],
                strengths=state["feedback"]["strengths"],
                weaknesses=state["feedback"]["weaknesses"],
                suggestions=state["feedback"]["suggestions"],
                improved_answer=state["feedback"]["improved_answer"],
            )
        else:
            answer.feedback.score_json = state["feedback"]["score_json"]
            answer.feedback.strengths = state["feedback"]["strengths"]
            answer.feedback.weaknesses = state["feedback"]["weaknesses"]
            answer.feedback.suggestions = state["feedback"]["suggestions"]
            answer.feedback.improved_answer = state["feedback"]["improved_answer"]

        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer.feedback

    async def regenerate_question(
        self,
        *,
        user_id: int,
        question_id: int,
        target_role: str | None = None,
        interview_style: str | None = None,
    ):
        question = get_question_for_user(self.db, user_id=user_id, question_id=question_id, required=True)
        question_set = get_question_set_for_user(
            self.db,
            user_id=user_id,
            question_set_id=question.question_set_id,
            required=True,
        )
        resume_session = question_set.resume_session
        try:
            state = await self.regeneration_runner.run(
                user_id=user_id,
                question_id=question.id,
                difficulty=question.difficulty,
                sort_order=question.sort_order,
                cleaned_text=resume_session.cleaned_text,
                resume_summary=resume_session.resume_summary_json,
                strategy=resume_session.strategy_json,
                job_description_text=resume_session.job_description_text,
                existing_questions=[item.question_text for item in question_set.questions],
                original_question=question.question_text,
                target_role=target_role or resume_session.target_role,
                interview_style=interview_style or resume_session.interview_style,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except LLMError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        question.category = state["final_item"]["category"]
        question.question_text = state["final_item"]["question"]
        question.answer_text = state["final_item"]["answer"]
        question.intent = state["final_item"]["intent"]
        question.reference_from_resume = state["final_item"]["reference_from_resume"]

        for user_answer in list(question.user_answers):
            self.db.delete(user_answer)

        self.db.commit()
        return get_question_for_user(self.db, user_id=user_id, question_id=question_id, required=True)
