from __future__ import annotations

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload, with_loader_criteria

from app.core.llm import LLMError
from app.graph.builder import InterviewGraphRunner
from app.models import Question, QuestionSet, ResumeSession, UserAnswer
from app.utils.job_description import (
    JobDescriptionExtractionError,
    extract_job_description_text,
    merge_job_description_inputs,
)
from app.utils.pdf import PDFExtractionError


class InterviewGenerationService:
    def __init__(self, db: Session, graph_runner: InterviewGraphRunner | None = None) -> None:
        self.db = db
        self.graph_runner = graph_runner or InterviewGraphRunner()

    async def generate_from_upload(
        self,
        *,
        user_id: int,
        upload: UploadFile,
        jd_upload: UploadFile | None = None,
        target_role: str | None = None,
        interview_style: str | None = None,
        job_description_text: str | None = None,
    ) -> QuestionSet:
        file_name = upload.filename or "resume.pdf"
        if not file_name.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF resumes are supported.",
            )

        pdf_bytes = await upload.read()
        if not pdf_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded PDF is empty.",
            )

        resolved_job_description_text = await self._resolve_job_description_text(
            jd_upload=jd_upload,
            pasted_text=job_description_text,
        )

        try:
            state = await self.graph_runner.run(
                user_id=user_id,
                file_name=file_name,
                pdf_bytes=pdf_bytes,
                target_role=target_role,
                interview_style=interview_style,
                job_description_text=resolved_job_description_text,
            )
        except PDFExtractionError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except LLMError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        return self._persist_generated_state(user_id=user_id, state=state)

    async def _resolve_job_description_text(
        self,
        *,
        jd_upload: UploadFile | None,
        pasted_text: str | None,
    ) -> str:
        uploaded_text = ""
        if jd_upload is not None:
            file_name = jd_upload.filename or "job-description.txt"
            file_bytes = await jd_upload.read()
            if not file_bytes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uploaded JD file is empty.",
                )
            try:
                uploaded_text = extract_job_description_text(file_bytes, file_name=file_name)
            except (JobDescriptionExtractionError, PDFExtractionError) as exc:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        return merge_job_description_inputs(
            uploaded_text=uploaded_text,
            pasted_text=pasted_text,
        )

    async def regenerate_interview_set(
        self,
        *,
        user_id: int,
        question_set_id: int,
        target_role: str | None = None,
        interview_style: str | None = None,
    ) -> QuestionSet:
        source_set = get_question_set_for_user(
            self.db,
            user_id=user_id,
            question_set_id=question_set_id,
            required=True,
        )
        source_session = source_set.resume_session

        try:
            state = await self.graph_runner.run_from_text(
                user_id=user_id,
                file_name=source_session.original_filename,
                raw_text=source_session.raw_text,
                target_role=target_role or source_session.target_role,
                interview_style=interview_style or source_session.interview_style,
                job_description_text=source_session.job_description_text,
            )
        except PDFExtractionError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except LLMError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        return self._persist_generated_state(user_id=user_id, state=state)

    def _persist_generated_state(self, *, user_id: int, state: dict) -> QuestionSet:
        resume_session = ResumeSession(
            user_id=user_id,
            original_filename=state["file_name"],
            raw_text=state["raw_text"],
            cleaned_text=state["cleaned_text"],
            extraction_status=state.get("extraction_status", "validated"),
            extraction_quality_score=state.get("extraction_quality_score"),
            extraction_error_message=state.get("extraction_error_message"),
            target_role=state["target_role"],
            interview_style=state["interview_style"],
            job_description_text=state.get("job_description_text") or None,
            resume_summary_json=state["resume_summary"],
            strategy_json=state["strategy"],
            total_questions=len(state["final_items"]),
        )
        self.db.add(resume_session)
        self.db.flush()

        question_set = QuestionSet(
            user_id=user_id,
            resume_session_id=resume_session.id,
            title=state["title"],
            meta_json=state["meta"],
        )
        self.db.add(question_set)
        self.db.flush()

        for index, item in enumerate(state["final_items"], start=1):
            self.db.add(
                Question(
                    question_set_id=question_set.id,
                    difficulty=item["difficulty"],
                    category=item["category"],
                    question_text=item["question"],
                    answer_text=item["answer"],
                    intent=item["intent"],
                    reference_from_resume=item["reference_from_resume"],
                    sort_order=index,
                )
            )

        self.db.commit()
        return get_question_set_for_user(
            self.db,
            user_id=user_id,
            question_set_id=question_set.id,
            required=True,
        )


def _question_set_loader_options(user_id: int) -> list:
    return [
        joinedload(QuestionSet.resume_session),
        selectinload(QuestionSet.questions)
        .selectinload(Question.user_answers)
        .selectinload(UserAnswer.feedback),
        with_loader_criteria(UserAnswer, UserAnswer.user_id == user_id, include_aliases=True),
    ]


def _question_loader_options(user_id: int) -> list:
    return [
        joinedload(Question.question_set).joinedload(QuestionSet.resume_session),
        selectinload(Question.user_answers).selectinload(UserAnswer.feedback),
        with_loader_criteria(UserAnswer, UserAnswer.user_id == user_id, include_aliases=True),
    ]


def list_question_sets_for_user(
    db: Session,
    *,
    user_id: int,
    page: int,
    page_size: int,
) -> tuple[list[QuestionSet], int]:
    total = db.scalar(select(func.count(QuestionSet.id)).where(QuestionSet.user_id == user_id)) or 0
    stmt = (
        select(QuestionSet)
        .where(QuestionSet.user_id == user_id)
        .options(*_question_set_loader_options(user_id))
        .order_by(QuestionSet.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    question_sets = db.execute(stmt).unique().scalars().all()
    return question_sets, total


def get_question_set_for_user(
    db: Session,
    *,
    user_id: int,
    question_set_id: int,
    required: bool = False,
) -> QuestionSet | None:
    stmt = (
        select(QuestionSet)
        .where(QuestionSet.id == question_set_id, QuestionSet.user_id == user_id)
        .options(*_question_set_loader_options(user_id))
    )
    question_set = db.execute(stmt).unique().scalar_one_or_none()
    if question_set is None and required:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview set not found.")
    return question_set


def get_question_for_user(
    db: Session,
    *,
    user_id: int,
    question_id: int,
    required: bool = False,
) -> Question | None:
    stmt = (
        select(Question)
        .join(Question.question_set)
        .where(Question.id == question_id, QuestionSet.user_id == user_id)
        .options(*_question_loader_options(user_id))
    )
    question = db.execute(stmt).unique().scalar_one_or_none()
    if question is None and required:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    return question
