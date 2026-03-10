from __future__ import annotations

from app.utils import pdf as pdf_utils


def test_text_first_extraction_clean_and_validate(monkeypatch) -> None:
    class FakePage:
        def __init__(self, text: str) -> None:
            self._text = text

        def extract_text(self) -> str:
            return self._text

    class FakeReader:
        def __init__(self, _stream) -> None:
            self.pages = [
                FakePage("Skills\nPython FastAPI PostgreSQL Docker"),
                FakePage(
                    "Experience\nBuilt backend services for internal platforms\nProjects\nAPI gateway and data platform\nEducation\nComputer Science"
                ),
            ]

    monkeypatch.setattr(pdf_utils, "PdfReader", FakeReader)

    raw_text = pdf_utils.extract_pdf_text(b"%PDF-1.4 fake", file_name="resume.pdf")
    cleaned_text = pdf_utils.clean_resume_text(raw_text)
    validation = pdf_utils.validate_resume_text(cleaned_text)

    assert "Python FastAPI PostgreSQL Docker" in raw_text
    assert "Experience" in cleaned_text
    assert validation.is_valid is True
    assert validation.quality_score >= 55


def test_validate_resume_text_rejects_poor_quality() -> None:
    validation = pdf_utils.validate_resume_text("Python")
    assert validation.is_valid is False
    assert validation.status in {"failed", "fallback_required"}
