from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from io import BytesIO

from pypdf import PdfReader

logger = logging.getLogger(__name__)

SECTION_HINTS = [
    "skills",
    "experience",
    "projects",
    "education",
    "工作经历",
    "项目经历",
    "专业技能",
    "教育经历",
]


class PDFExtractionError(ValueError):
    """Raised when a resume PDF does not contain enough usable text."""


@dataclass(slots=True)
class ResumeTextValidationResult:
    is_valid: bool
    quality_score: float
    status: str
    error_message: str | None = None
    signal_tags: list[str] = field(default_factory=list)


def extract_pdf_text(pdf_bytes: bytes, *, file_name: str = "resume.pdf") -> str:
    logger.info("Starting native PDF text extraction for %s", file_name)
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to parse PDF %s", file_name)
        raise PDFExtractionError("无法读取 PDF 文件，请确认上传的是有效的文本型简历 PDF。") from exc

    page_texts: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        page_text = (page.extract_text() or "").strip()
        logger.info("Extracted %s characters from %s page %s", len(page_text), file_name, index)
        if page_text:
            page_texts.append(page_text)

    raw_text = "\n\n".join(page_texts).strip()
    if not raw_text:
        logger.error("No extractable text found in %s", file_name)
        raise PDFExtractionError(
            "未能从 PDF 中提取到可用文本。当前流程坚持 text-first，本次不会把 PDF 页面转成图片发送给模型。"
        )

    return raw_text


def _looks_like_heading(line: str) -> bool:
    lowered = line.lower().strip(":：")
    if lowered in SECTION_HINTS:
        return True
    if len(line) <= 28 and (line.endswith(":") or line.endswith("：")):
        return True
    return bool(re.fullmatch(r"[A-Z][A-Z\\s/&-]{2,}", line))


def _should_merge_line(previous_line: str, next_line: str) -> bool:
    if not previous_line or not next_line:
        return False
    if _looks_like_heading(previous_line) or _looks_like_heading(next_line):
        return False
    if previous_line.endswith((".", "。", "!", "！", "?", "？", ":", "：")):
        return False
    if next_line.startswith(("-", "•", "*", "1.", "2.", "3.")):
        return False
    if len(previous_line) > 120 or len(next_line) > 120:
        return False
    return True


def clean_resume_text(text: str) -> str:
    normalized_lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    normalized_lines = [line for line in normalized_lines if line]

    merged_lines: list[str] = []
    for line in normalized_lines:
        if merged_lines and _should_merge_line(merged_lines[-1], line):
            merged_lines[-1] = f"{merged_lines[-1]} {line}"
        else:
            merged_lines.append(line)

    cleaned = "\n".join(merged_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def validate_resume_text(text: str) -> ResumeTextValidationResult:
    stripped = text.strip()
    text_length = len(stripped)
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_+.#/-]*|[\u4e00-\u9fff]{2,}", stripped)
    unique_ratio = len({token.lower() for token in tokens}) / max(len(tokens), 1)
    lowered_text = stripped.lower()
    hit_sections = [hint for hint in SECTION_HINTS if hint in lowered_text]

    quality_score = round(
        min(text_length / 1800, 1.0) * 45
        + min(len(tokens) / 220, 1.0) * 25
        + min(len(hit_sections) / 4, 1.0) * 20
        + min(unique_ratio / 0.55, 1.0) * 10,
        2,
    )

    signal_tags = []
    if text_length >= 240:
        signal_tags.append("length_ok")
    if len(tokens) >= 40:
        signal_tags.append("token_density_ok")
    if hit_sections:
        signal_tags.append("section_structure_ok")
    if unique_ratio >= 0.28:
        signal_tags.append("unique_terms_ok")

    if text_length < 120 or len(tokens) < 25 or quality_score < 40:
        error_message = (
            "提取到的简历文本质量过低，无法安全送入 LLM 做分析。"
            "当前系统默认只走本地 text-first 提取路径，未启用 OCR 图片回退。"
        )
        logger.error(
            "Resume text validation failed: length=%s tokens=%s score=%s",
            text_length,
            len(tokens),
            quality_score,
        )
        return ResumeTextValidationResult(
            is_valid=False,
            quality_score=quality_score,
            status="failed",
            error_message=error_message,
            signal_tags=signal_tags,
        )

    if quality_score < 55:
        error_message = (
            "已提取到文本，但质量偏低。当前系统保持 text-first，若需要 OCR 回退请在后续版本显式开启。"
        )
        logger.warning(
            "Resume text validation requires fallback: length=%s tokens=%s score=%s",
            text_length,
            len(tokens),
            quality_score,
        )
        return ResumeTextValidationResult(
            is_valid=False,
            quality_score=quality_score,
            status="fallback_required",
            error_message=error_message,
            signal_tags=signal_tags,
        )

    logger.info(
        "Resume text validated successfully: length=%s tokens=%s score=%s",
        text_length,
        len(tokens),
        quality_score,
    )
    return ResumeTextValidationResult(
        is_valid=True,
        quality_score=quality_score,
        status="validated",
        signal_tags=signal_tags,
    )
