from __future__ import annotations

import json
import logging
from collections import defaultdict
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.core.llm import LLMError, OpenAICompatibleLLM
from app.graph.schemas import (
    InterviewStrategyLLMOutput,
    QAItemsLLMOutput,
    ResumeAnalysisLLMOutput,
)
from app.graph.state import InterviewGraphState
from app.utils.interview import (
    DEFAULT_INTERVIEW_STYLE,
    DEFAULT_TARGET_ROLE,
    DIFFICULTY_DISTRIBUTION,
    VALID_CATEGORIES,
    build_fallback_answer,
    build_local_question,
    build_reference_fallback,
    normalize_generated_item,
    normalize_question_key,
    resolve_interview_style,
    resolve_target_role,
)
from app.utils.pdf import PDFExtractionError, clean_resume_text, extract_pdf_text, validate_resume_text
from app.utils.prompt_loader import render_prompt

logger = logging.getLogger(__name__)

JSON_SYSTEM_PROMPT = "你是一个只允许输出 JSON 的严谨工作流节点。"


class InterviewGraphRunner:
    def __init__(self, llm: OpenAICompatibleLLM | None = None) -> None:
        self.llm = llm or OpenAICompatibleLLM()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(InterviewGraphState)
        workflow.add_node("extract_pdf_text", self.extract_pdf_text)
        workflow.add_node("clean_resume_text", self.clean_resume_text)
        workflow.add_node("validate_resume_text", self.validate_resume_text)
        workflow.add_node("analyze_resume", self.analyze_resume)
        workflow.add_node("plan_interview_strategy", self.plan_interview_strategy)
        workflow.add_node(
            "generate_easy_questions_and_answers",
            self.generate_easy_questions_and_answers,
        )
        workflow.add_node(
            "generate_medium_questions_and_answers",
            self.generate_medium_questions_and_answers,
        )
        workflow.add_node(
            "generate_hard_questions_and_answers",
            self.generate_hard_questions_and_answers,
        )
        workflow.add_node("deduplicate_and_repair", self.deduplicate_and_repair)
        workflow.add_node("finalize_payload", self.finalize_payload)

        workflow.add_edge(START, "extract_pdf_text")
        workflow.add_edge("extract_pdf_text", "clean_resume_text")
        workflow.add_edge("clean_resume_text", "validate_resume_text")
        workflow.add_edge("validate_resume_text", "analyze_resume")
        workflow.add_edge("analyze_resume", "plan_interview_strategy")
        workflow.add_edge("plan_interview_strategy", "generate_easy_questions_and_answers")
        workflow.add_edge(
            "generate_easy_questions_and_answers",
            "generate_medium_questions_and_answers",
        )
        workflow.add_edge(
            "generate_medium_questions_and_answers",
            "generate_hard_questions_and_answers",
        )
        workflow.add_edge("generate_hard_questions_and_answers", "deduplicate_and_repair")
        workflow.add_edge("deduplicate_and_repair", "finalize_payload")
        workflow.add_edge("finalize_payload", END)
        return workflow.compile()

    async def run(
        self,
        *,
        user_id: int,
        file_name: str,
        pdf_bytes: bytes,
        target_role: str | None = None,
        interview_style: str | None = None,
    ) -> InterviewGraphState:
        return await self.graph.ainvoke(
            {
                "user_id": user_id,
                "file_name": file_name,
                "pdf_bytes": pdf_bytes,
                "target_role": resolve_target_role(target_role),
                "interview_style": resolve_interview_style(interview_style),
                "errors": [],
            }
        )

    async def run_from_text(
        self,
        *,
        user_id: int,
        file_name: str,
        raw_text: str,
        target_role: str | None = None,
        interview_style: str | None = None,
    ) -> InterviewGraphState:
        return await self.graph.ainvoke(
            {
                "user_id": user_id,
                "file_name": file_name,
                "raw_text": raw_text,
                "target_role": resolve_target_role(target_role),
                "interview_style": resolve_interview_style(interview_style),
                "errors": [],
            }
        )

    async def extract_pdf_text(self, state: InterviewGraphState) -> dict[str, Any]:
        if state.get("raw_text"):
            logger.info("Using existing extracted resume text for %s", state["file_name"])
            return {"raw_text": state["raw_text"]}
        return {
            "raw_text": extract_pdf_text(
                state["pdf_bytes"],
                file_name=state.get("file_name", "resume.pdf"),
            )
        }

    async def clean_resume_text(self, state: InterviewGraphState) -> dict[str, Any]:
        return {"cleaned_text": clean_resume_text(state["raw_text"])}

    async def validate_resume_text(self, state: InterviewGraphState) -> dict[str, Any]:
        result = validate_resume_text(state["cleaned_text"])
        if not result.is_valid:
            raise PDFExtractionError(result.error_message or "简历文本校验失败。")
        return {
            "extraction_status": result.status,
            "extraction_quality_score": result.quality_score,
            "extraction_error_message": result.error_message,
        }

    async def analyze_resume(self, state: InterviewGraphState) -> dict[str, Any]:
        prompt = render_prompt(
            "resume_analysis.txt",
            cleaned_text=state["cleaned_text"],
            target_role=state.get("target_role", DEFAULT_TARGET_ROLE),
            interview_style=state.get("interview_style", DEFAULT_INTERVIEW_STYLE),
        )
        response = await self.llm.complete_json(
            system_prompt=JSON_SYSTEM_PROMPT,
            user_prompt=prompt,
            schema=ResumeAnalysisLLMOutput,
        )
        return {"resume_summary": response.model_dump()}

    async def plan_interview_strategy(self, state: InterviewGraphState) -> dict[str, Any]:
        prompt = render_prompt(
            "interview_strategy.txt",
            resume_summary=json.dumps(state["resume_summary"], ensure_ascii=False, indent=2),
            cleaned_text=state["cleaned_text"],
            target_role=state.get("target_role", DEFAULT_TARGET_ROLE),
            interview_style=state.get("interview_style", DEFAULT_INTERVIEW_STYLE),
        )
        response = await self.llm.complete_json(
            system_prompt=JSON_SYSTEM_PROMPT,
            user_prompt=prompt,
            schema=InterviewStrategyLLMOutput,
        )
        strategy = response.model_dump()
        strategy["target_role"] = state.get("target_role", DEFAULT_TARGET_ROLE)
        strategy["interview_style"] = state.get("interview_style", DEFAULT_INTERVIEW_STYLE)
        return {"strategy": strategy}

    async def generate_easy_questions_and_answers(self, state: InterviewGraphState) -> dict[str, Any]:
        return {
            "easy_items": await self._generate_band(
                state=state,
                difficulty="easy",
                count=DIFFICULTY_DISTRIBUTION["easy"],
                prompt_name="generate_easy_qa.txt",
            )
        }

    async def generate_medium_questions_and_answers(
        self,
        state: InterviewGraphState,
    ) -> dict[str, Any]:
        return {
            "medium_items": await self._generate_band(
                state=state,
                difficulty="medium",
                count=DIFFICULTY_DISTRIBUTION["medium"],
                prompt_name="generate_medium_qa.txt",
            )
        }

    async def generate_hard_questions_and_answers(self, state: InterviewGraphState) -> dict[str, Any]:
        return {
            "hard_items": await self._generate_band(
                state=state,
                difficulty="hard",
                count=DIFFICULTY_DISTRIBUTION["hard"],
                prompt_name="generate_hard_qa.txt",
            )
        }

    async def deduplicate_and_repair(self, state: InterviewGraphState) -> dict[str, Any]:
        resume_summary = state["resume_summary"]
        seen_questions: set[str] = set()
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for difficulty in ("easy", "medium", "hard"):
            for item in state.get(f"{difficulty}_items", []):
                normalized = normalize_generated_item(
                    item=item,
                    expected_difficulty=difficulty,
                    resume_summary=resume_summary,
                )
                if not normalized["question"]:
                    continue
                question_key = normalize_question_key(normalized["question"])
                if question_key in seen_questions:
                    continue
                seen_questions.add(question_key)
                buckets[difficulty].append(normalized)

        for difficulty, target_count in DIFFICULTY_DISTRIBUTION.items():
            buckets[difficulty] = buckets[difficulty][:target_count]
            missing_count = target_count - len(buckets[difficulty])
            if missing_count > 0:
                repaired_items = await self._repair_shortfall(
                    state=state,
                    difficulty=difficulty,
                    count=missing_count,
                    existing_questions=[item["question"] for item in buckets[difficulty]],
                )
                for item in repaired_items:
                    question_key = normalize_question_key(item["question"])
                    if question_key in seen_questions:
                        continue
                    seen_questions.add(question_key)
                    buckets[difficulty].append(item)
                    if len(buckets[difficulty]) == target_count:
                        break

            if len(buckets[difficulty]) < target_count:
                buckets[difficulty].extend(
                    self._generate_local_fallback_items(
                        state=state,
                        difficulty=difficulty,
                        count=target_count - len(buckets[difficulty]),
                        existing_questions={item["question"] for item in buckets[difficulty]},
                    )
                )

        final_items: list[dict[str, Any]] = []
        for difficulty in ("easy", "medium", "hard"):
            final_items.extend(buckets[difficulty][: DIFFICULTY_DISTRIBUTION[difficulty]])

        return {"final_items": final_items}

    async def finalize_payload(self, state: InterviewGraphState) -> dict[str, Any]:
        final_items = state["final_items"]
        difficulty_breakdown = {
            difficulty: len([item for item in final_items if item["difficulty"] == difficulty])
            for difficulty in DIFFICULTY_DISTRIBUTION
        }
        title = f"{state.get('target_role', DEFAULT_TARGET_ROLE)} 模拟面试题集"
        meta = {
            "difficulty_breakdown": difficulty_breakdown,
            "categories": sorted({item["category"] for item in final_items}),
            "total_questions": len(final_items),
            "file_name": state["file_name"],
            "target_role": state.get("target_role", DEFAULT_TARGET_ROLE),
            "interview_style": state.get("interview_style", DEFAULT_INTERVIEW_STYLE),
            "extraction_status": state.get("extraction_status", "validated"),
            "extraction_quality_score": state.get("extraction_quality_score", 0.0),
        }
        return {"title": title, "meta": meta}

    async def _generate_band(
        self,
        *,
        state: InterviewGraphState,
        difficulty: str,
        count: int,
        prompt_name: str,
    ) -> list[dict[str, Any]]:
        prompt = render_prompt(
            prompt_name,
            count=count,
            cleaned_text=state["cleaned_text"],
            resume_summary=json.dumps(state["resume_summary"], ensure_ascii=False, indent=2),
            strategy=json.dumps(state["strategy"], ensure_ascii=False, indent=2),
            target_role=state.get("target_role", DEFAULT_TARGET_ROLE),
            interview_style=state.get("interview_style", DEFAULT_INTERVIEW_STYLE),
        )
        response = await self.llm.complete_json(
            system_prompt=JSON_SYSTEM_PROMPT,
            user_prompt=prompt,
            schema=QAItemsLLMOutput,
        )
        return [
            normalize_generated_item(
                item=item.model_dump(),
                expected_difficulty=difficulty,
                resume_summary=state["resume_summary"],
            )
            for item in response.items
        ]

    async def _repair_shortfall(
        self,
        *,
        state: InterviewGraphState,
        difficulty: str,
        count: int,
        existing_questions: list[str],
    ) -> list[dict[str, Any]]:
        if count <= 0:
            return []

        prompt = render_prompt(
            "repair_items.txt",
            difficulty=difficulty,
            count=count,
            problem_summary=f"{difficulty} 难度题目数量不足，需要补齐并修复答案质量。",
            resume_summary=json.dumps(state["resume_summary"], ensure_ascii=False, indent=2),
            strategy=json.dumps(state["strategy"], ensure_ascii=False, indent=2),
            existing_questions=json.dumps(existing_questions, ensure_ascii=False, indent=2),
            target_role=state.get("target_role", DEFAULT_TARGET_ROLE),
            interview_style=state.get("interview_style", DEFAULT_INTERVIEW_STYLE),
        )
        try:
            response = await self.llm.complete_json(
                system_prompt=JSON_SYSTEM_PROMPT,
                user_prompt=prompt,
                schema=QAItemsLLMOutput,
            )
        except LLMError:
            logger.warning("LLM repair failed for %s items, using local fallback.", difficulty)
            return []

        return [
            normalize_generated_item(
                item=item.model_dump(),
                expected_difficulty=difficulty,
                resume_summary=state["resume_summary"],
            )
            for item in response.items
        ]

    def _generate_local_fallback_items(
        self,
        *,
        state: InterviewGraphState,
        difficulty: str,
        count: int,
        existing_questions: set[str],
    ) -> list[dict[str, Any]]:
        resume_summary = state["resume_summary"]
        items: list[dict[str, Any]] = []
        for index in range(count * 4):
            category = VALID_CATEGORIES[index % len(VALID_CATEGORIES)]
            question = build_local_question(
                difficulty=difficulty,
                category=category,
                resume_summary=resume_summary,
                index_seed=index,
                target_role=state.get("target_role", DEFAULT_TARGET_ROLE),
            )
            if question in existing_questions:
                continue
            reference = build_reference_fallback(resume_summary)
            items.append(
                {
                    "difficulty": difficulty,
                    "category": category,
                    "question": question,
                    "answer": build_fallback_answer(
                        question=question,
                        difficulty=difficulty,
                        category=category,
                        resume_summary=resume_summary,
                        reference=reference,
                    ),
                    "intent": "补齐去重后的题目数量，并继续考察真实工程判断。",
                    "reference_from_resume": reference,
                }
            )
            existing_questions.add(question)
            if len(items) == count:
                break
        return items
