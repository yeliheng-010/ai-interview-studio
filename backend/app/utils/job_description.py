from __future__ import annotations

from app.utils.interview import resolve_job_description_text
from app.utils.pdf import clean_resume_text, extract_pdf_text

TEXT_FILE_SUFFIXES = (".txt", ".md", ".markdown")


class JobDescriptionExtractionError(ValueError):
    """Raised when an uploaded JD file cannot be converted into usable text."""


def extract_job_description_text(file_bytes: bytes, *, file_name: str) -> str:
    lower_name = file_name.lower()
    if lower_name.endswith(".pdf"):
        raw_text = extract_pdf_text(file_bytes, file_name=file_name)
    elif lower_name.endswith(TEXT_FILE_SUFFIXES):
        raw_text = _decode_text_file(file_bytes)
    else:
        raise JobDescriptionExtractionError("Only .txt, .md, and .pdf job description files are supported.")

    cleaned_text = clean_resume_text(raw_text)
    if len(cleaned_text) < 40:
        raise JobDescriptionExtractionError("The uploaded JD file does not contain enough usable text.")
    return cleaned_text


def merge_job_description_inputs(*, uploaded_text: str | None, pasted_text: str | None) -> str:
    parts = [
        resolve_job_description_text(uploaded_text),
        resolve_job_description_text(pasted_text),
    ]
    return "\n\n".join(part for part in parts if part)


def _decode_text_file(file_bytes: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "gbk", "utf-16"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise JobDescriptionExtractionError("The uploaded JD text file encoding is not supported.")
