from __future__ import annotations

from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def render_prompt(prompt_name: str, **kwargs: object) -> str:
    template = (PROMPT_DIR / prompt_name).read_text(encoding="utf-8")
    return template.format(**kwargs)
