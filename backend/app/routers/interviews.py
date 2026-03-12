from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db import get_db
from app.models import Favorite, User
from app.schemas.interview import InterviewRegenerateRequest, InterviewSetDetail, PaginatedInterviewSets
from app.services.interview_service import (
    InterviewGenerationService,
    get_question_set_for_user,
    list_question_sets_for_user,
)
from app.services.serializers import question_set_to_detail, question_set_to_list_item

router = APIRouter(prefix="/interviews", tags=["interviews"])
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=InterviewSetDetail)
async def generate_interview_set(
    file: UploadFile = File(...),
    jd_file: UploadFile | None = File(None),
    target_role: str | None = Form(None),
    interview_style: str | None = Form(None),
    job_description_text: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSetDetail:
    service = InterviewGenerationService(db)
    question_set = await service.generate_from_upload(
        user_id=current_user.id,
        upload=file,
        jd_upload=jd_file,
        target_role=target_role,
        interview_style=interview_style,
        job_description_text=job_description_text,
    )
    return question_set_to_detail(question_set, favorite_question_ids=set())


@router.post("/generate/stream")
async def generate_interview_set_stream(
    file: UploadFile = File(...),
    jd_file: UploadFile | None = File(None),
    target_role: str | None = Form(None),
    interview_style: str | None = Form(None),
    job_description_text: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    service = InterviewGenerationService(db)
    file_name, pdf_bytes, resolved_job_description_text = await service.prepare_upload_inputs(
        upload=file,
        jd_upload=jd_file,
        job_description_text=job_description_text,
    )

    async def event_stream():
        try:
            async for event in service.generate_from_bytes_stream(
                user_id=current_user.id,
                file_name=file_name,
                pdf_bytes=pdf_bytes,
                target_role=target_role,
                interview_style=interview_style,
                resolved_job_description_text=resolved_job_description_text,
            ):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except Exception as exc:  # noqa: BLE001
            logger.exception("stream generation failed")
            message = getattr(exc, "detail", str(exc))
            yield json.dumps({"event": "error", "detail": message}, ensure_ascii=False) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@router.get("", response_model=PaginatedInterviewSets)
def list_interview_sets(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedInterviewSets:
    page = max(page, 1)
    page_size = max(min(page_size, 50), 1)
    question_sets, total = list_question_sets_for_user(
        db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )
    return PaginatedInterviewSets(
        items=[question_set_to_list_item(item) for item in question_sets],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{interview_id}", response_model=InterviewSetDetail)
def get_interview_set(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSetDetail:
    question_set = get_question_set_for_user(
        db,
        user_id=current_user.id,
        question_set_id=interview_id,
        required=True,
    )
    favorite_ids = set(
        db.scalars(
            select(Favorite.question_id)
            .join(Favorite.question)
            .where(
                Favorite.user_id == current_user.id,
                Favorite.question_id.in_([question.id for question in question_set.questions]),
            )
        ).all()
    )
    return question_set_to_detail(question_set, favorite_question_ids=favorite_ids)


@router.post("/{interview_id}/regenerate", response_model=InterviewSetDetail)
async def regenerate_interview_set(
    interview_id: int,
    payload: InterviewRegenerateRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSetDetail:
    service = InterviewGenerationService(db)
    question_set = await service.regenerate_interview_set(
        user_id=current_user.id,
        question_set_id=interview_id,
        target_role=payload.target_role if payload else None,
        interview_style=payload.interview_style if payload else None,
    )
    return question_set_to_detail(question_set, favorite_question_ids=set())
