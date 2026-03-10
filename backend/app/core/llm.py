from __future__ import annotations

import json
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.config import settings

ModelT = TypeVar("ModelT", bound=BaseModel)


class LLMError(RuntimeError):
    """Raised when the upstream LLM cannot satisfy the request."""


class OpenAICompatibleLLM:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.openai_api_key
        self.base_url = (base_url or settings.openai_base_url).rstrip("/")
        self.model = model or settings.openai_model
        self.timeout_seconds = settings.openai_timeout_seconds

    async def complete_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[ModelT],
        temperature: float = 0.2,
    ) -> ModelT:
        if not self.api_key:
            raise LLMError("OPENAI_API_KEY is not configured.")

        payload = {
            "model": self.model,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        timeout = httpx.Timeout(
            timeout=self.timeout_seconds,
            connect=min(self.timeout_seconds, 20.0),
        )
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise LLMError(
                f"LLM request timed out after {self.timeout_seconds:.0f} seconds. "
                "Please retry, or use a shorter resume / a faster model."
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMError(f"LLM transport error: {exc}") from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise LLMError(f"LLM request failed: {exc.response.text}") from exc

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Unexpected LLM response shape.") from exc

        parsed = self._extract_json(content)
        try:
            return schema.model_validate(parsed)
        except ValidationError as exc:
            raise LLMError(f"LLM JSON validation failed: {exc}") from exc

    def _extract_json(self, text: str) -> Any:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()

        start_candidates = [index for index in (cleaned.find("{"), cleaned.find("[")) if index != -1]
        end_candidates = [index for index in (cleaned.rfind("}"), cleaned.rfind("]")) if index != -1]
        if not start_candidates or not end_candidates:
            raise LLMError("LLM did not return JSON.")

        blob = cleaned[min(start_candidates) : max(end_candidates) + 1]
        try:
            return json.loads(blob)
        except json.JSONDecodeError as exc:
            raise LLMError("LLM returned invalid JSON.") from exc
