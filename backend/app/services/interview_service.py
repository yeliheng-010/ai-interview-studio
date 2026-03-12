from __future__ import annotations

from collections.abc import AsyncIterator

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
        file_name, pdf_bytes, resolved_job_description_text = await self.prepare_upload_inputs(
            upload=upload,
            jd_upload=jd_upload,
            job_description_text=job_description_text,
        )
        return await self.generate_from_bytes(
            user_id=user_id,
            file_name=file_name,
            pdf_bytes=pdf_bytes,
            target_role=target_role,
            interview_style=interview_style,
            resolved_job_description_text=resolved_job_description_text,
        )

    async def prepare_upload_inputs(
        self,
        *,
        upload: UploadFile,
        jd_upload: UploadFile | None = None,
        job_description_text: str | None = None,
    ) -> tuple[str, bytes, str]:
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
        return file_name, pdf_bytes, resolved_job_description_text

    async def generate_from_bytes(
        self,
        *,
        user_id: int,
        file_name: str,
        pdf_bytes: bytes,
        target_role: str | None = None,
        interview_style: str | None = None,
        resolved_job_description_text: str = "",
    ) -> QuestionSet:

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

    async def generate_from_bytes_stream(
        self,
        *,
        user_id: int,
        file_name: str,
        pdf_bytes: bytes,
        target_role: str | None = None,
        interview_style: str | None = None,
        resolved_job_description_text: str = "",
    ) -> AsyncIterator[dict]:
        step_messages = {
            "extract_pdf_text": "已提取简历文本",
            "clean_resume_text": "已清洗简历文本",
            "validate_resume_text": "简历文本质量校验通过",
            "analyze_resume": "简历分析完成",
            "plan_interview_strategy": "面试策略规划完成",
            "generate_easy_questions_and_answers": "已生成 easy 题目",
            "generate_medium_questions_and_answers": "已生成 medium 题目",
            "generate_hard_questions_and_answers": "已生成 hard 题目",
            "deduplicate_and_repair": "已完成题目去重与修复",
            "append_leetcode_questions": "已追加 LeetCode 算法题",
            "finalize_payload": "题集封装完成，正在落库",
        }
        final_state = None
        running_count = 0

        try:
            async for event in self.graph_runner.run_with_progress(
                user_id=user_id,
                file_name=file_name,
                pdf_bytes=pdf_bytes,
                target_role=target_role,
                interview_style=interview_style,
                job_description_text=resolved_job_description_text,
            ):
                if event.get("event") == "completed":
                    final_state = event["state"]
                    continue

                step_name = event.get("step")
                update = event.get("update", {})
                yield {
                    "event": "stage",
                    "step": step_name,
                    "message": step_messages.get(step_name, "处理中"),
                }

                if step_name == "analyze_resume":
                    resume_summary = update.get("resume_summary", {})
                    suggestions = resume_summary.get("resume_improvement_suggestions", [])
                    if suggestions:
                        yield {
                            "event": "resume_suggestions",
                            "suggestions": suggestions,
                        }

                if step_name in {
                    "generate_easy_questions_and_answers",
                    "generate_medium_questions_and_answers",
                    "generate_hard_questions_and_answers",
                }:
                    band_key = {
                        "generate_easy_questions_and_answers": "easy_items",
                        "generate_medium_questions_and_answers": "medium_items",
                        "generate_hard_questions_and_answers": "hard_items",
                    }[step_name]
                    for item in update.get(band_key, []):
                        running_count += 1
                        yield {
                            "event": "question",
                            "index": running_count,
                            "difficulty": item.get("difficulty"),
                            "category": item.get("category"),
                            "question": item.get("question"),
                            "is_leetcode": False,
                        }

                if step_name == "append_leetcode_questions":
                    for item in update.get("leetcode_items", []):
                        running_count += 1
                        yield {
                            "event": "question",
                            "index": running_count,
                            "difficulty": item.get("difficulty"),
                            "category": item.get("category"),
                            "question": item.get("question"),
                            "is_leetcode": True,
                        }

            if final_state is None:
                raise RuntimeError("Interview generation did not complete.")

            question_set = self._persist_generated_state(user_id=user_id, state=final_state)
            yield {
                "event": "completed",
                "interview_id": question_set.id,
                "title": question_set.title,
            }
        except PDFExtractionError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except LLMError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

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
