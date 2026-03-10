from __future__ import annotations

import json
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.core.llm import LLMError, OpenAICompatibleLLM
from app.graph.schemas import AnswerFeedbackLLMOutput, QAItemsLLMOutput
from app.graph.state import AnswerFeedbackState, QuestionRegenerationState
from app.utils.interview import (
    DEFAULT_INTERVIEW_STYLE,
    DEFAULT_TARGET_ROLE,
    build_fallback_answer,
    build_local_question,
    build_reference_fallback,
    normalize_generated_item,
    normalize_question_key,
    resolve_job_description_text,
    resolve_interview_style,
    resolve_target_role,
)
from app.utils.prompt_loader import render_prompt

JSON_SYSTEM_PROMPT = "你是一个只允许输出 JSON 的严谨工作流节点。"


class QuestionRegenerationGraphRunner:
    def __init__(self, llm: OpenAICompatibleLLM | None = None) -> None:
        self.llm = llm or OpenAICompatibleLLM()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(QuestionRegenerationState)
        workflow.add_node("prepare_regeneration_context", self.prepare_regeneration_context)
        workflow.add_node("generate_replacement_question", self.generate_replacement_question)
        workflow.add_node("finalize_replacement_question", self.finalize_replacement_question)

        workflow.add_edge(START, "prepare_regeneration_context")
        workflow.add_edge("prepare_regeneration_context", "generate_replacement_question")
        workflow.add_edge("generate_replacement_question", "finalize_replacement_question")
        workflow.add_edge("finalize_replacement_question", END)
        return workflow.compile()

    async def run(
        self,
        *,
        user_id: int,
        question_id: int,
        difficulty: str,
        sort_order: int,
        cleaned_text: str,
        resume_summary: dict[str, Any],
        strategy: dict[str, Any],
        job_description_text: str | None,
        existing_questions: list[str],
        original_question: str,
        target_role: str | None = None,
        interview_style: str | None = None,
    ) -> QuestionRegenerationState:
        return await self.graph.ainvoke(
            {
                "user_id": user_id,
                "question_id": question_id,
                "difficulty": difficulty,
                "sort_order": sort_order,
                "cleaned_text": cleaned_text,
                "resume_summary": resume_summary,
                "strategy": strategy,
                "job_description_text": resolve_job_description_text(job_description_text),
                "existing_questions": existing_questions,
                "original_question": original_question,
                "target_role": resolve_target_role(target_role or strategy.get("target_role")),
                "interview_style": resolve_interview_style(interview_style or strategy.get("interview_style")),
                "errors": [],
            }
        )

    async def prepare_regeneration_context(self, state: QuestionRegenerationState) -> dict[str, Any]:
        original_key = normalize_question_key(state["original_question"])
        return {
            "existing_questions": [
                question
                for question in state.get("existing_questions", [])
                if normalize_question_key(question) != original_key
            ],
            "target_role": resolve_target_role(state.get("target_role")),
            "interview_style": resolve_interview_style(state.get("interview_style")),
        }

    async def generate_replacement_question(self, state: QuestionRegenerationState) -> dict[str, Any]:
        prompt = render_prompt(
            "regenerate_question.txt",
            difficulty=state["difficulty"],
            sort_order=state["sort_order"],
            cleaned_text=state["cleaned_text"],
            resume_summary=json.dumps(state["resume_summary"], ensure_ascii=False, indent=2),
            strategy=json.dumps(state["strategy"], ensure_ascii=False, indent=2),
            existing_questions=json.dumps(state["existing_questions"], ensure_ascii=False, indent=2),
            original_question=state["original_question"],
            target_role=state.get("target_role", DEFAULT_TARGET_ROLE),
            interview_style=state.get("interview_style", DEFAULT_INTERVIEW_STYLE),
            job_description_text=state.get("job_description_text") or "未提供岗位 JD。",
        )
        response = await self.llm.complete_json(
            system_prompt=JSON_SYSTEM_PROMPT,
            user_prompt=prompt,
            schema=QAItemsLLMOutput,
        )
        return {"generated_item": response.items[0].model_dump() if response.items else {}}

    async def finalize_replacement_question(self, state: QuestionRegenerationState) -> dict[str, Any]:
        resume_summary = state["resume_summary"]
        item = normalize_generated_item(
            item=state.get("generated_item", {}),
            expected_difficulty=state["difficulty"],
            resume_summary=resume_summary,
        )
        question_key = normalize_question_key(item["question"])
        existing_keys = {normalize_question_key(question) for question in state["existing_questions"]}
        if not item["question"] or question_key in existing_keys:
            category = item["category"] or "工程实践"
            question = ""
            for offset in range(6):
                candidate = build_local_question(
                    difficulty=state["difficulty"],
                    category=category,
                    resume_summary=resume_summary,
                    index_seed=state["sort_order"] + offset,
                    target_role=state.get("target_role", DEFAULT_TARGET_ROLE),
                )
                if normalize_question_key(candidate) not in existing_keys:
                    question = candidate
                    break
            if not question:
                question = build_local_question(
                    difficulty=state["difficulty"],
                    category=category,
                    resume_summary=resume_summary,
                    index_seed=state["sort_order"] + 7,
                    target_role=state.get("target_role", DEFAULT_TARGET_ROLE),
                )
            reference = build_reference_fallback(resume_summary)
            item = {
                "difficulty": state["difficulty"],
                "category": category,
                "question": question,
                "answer": build_fallback_answer(
                    question=question,
                    difficulty=state["difficulty"],
                    category=category,
                    resume_summary=resume_summary,
                    reference=reference,
                ),
                "intent": "在原有题集结构内替换为同难度的新题目，继续保持练习价值。",
                "reference_from_resume": reference,
            }
        return {"final_item": item}


class AnswerFeedbackGraphRunner:
    def __init__(self, llm: OpenAICompatibleLLM | None = None) -> None:
        self.llm = llm or OpenAICompatibleLLM()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AnswerFeedbackState)
        workflow.add_node("prepare_feedback_context", self.prepare_feedback_context)
        workflow.add_node("evaluate_answer_feedback", self.evaluate_answer_feedback)
        workflow.add_node("finalize_answer_feedback", self.finalize_answer_feedback)

        workflow.add_edge(START, "prepare_feedback_context")
        workflow.add_edge("prepare_feedback_context", "evaluate_answer_feedback")
        workflow.add_edge("evaluate_answer_feedback", "finalize_answer_feedback")
        workflow.add_edge("finalize_answer_feedback", END)
        return workflow.compile()

    async def run(
        self,
        *,
        user_id: int,
        question_id: int,
        question_text: str,
        reference_answer: str,
        user_answer: str,
        target_role: str | None = None,
        interview_style: str | None = None,
    ) -> AnswerFeedbackState:
        return await self.graph.ainvoke(
            {
                "user_id": user_id,
                "question_id": question_id,
                "question_text": question_text,
                "reference_answer": reference_answer,
                "user_answer": user_answer,
                "target_role": resolve_target_role(target_role),
                "interview_style": resolve_interview_style(interview_style),
                "errors": [],
            }
        )

    async def prepare_feedback_context(self, state: AnswerFeedbackState) -> dict[str, Any]:
        if len(state["user_answer"].strip()) < 20:
            raise ValueError("用户作答过短，无法生成有价值的反馈。")
        return {
            "target_role": resolve_target_role(state.get("target_role")),
            "interview_style": resolve_interview_style(state.get("interview_style")),
        }

    async def evaluate_answer_feedback(self, state: AnswerFeedbackState) -> dict[str, Any]:
        prompt = render_prompt(
            "evaluate_answer_feedback.txt",
            question_text=state["question_text"],
            reference_answer=state["reference_answer"],
            user_answer=state["user_answer"],
            target_role=state.get("target_role", DEFAULT_TARGET_ROLE),
            interview_style=state.get("interview_style", DEFAULT_INTERVIEW_STYLE),
        )
        try:
            response = await self.llm.complete_json(
                system_prompt=JSON_SYSTEM_PROMPT,
                user_prompt=prompt,
                schema=AnswerFeedbackLLMOutput,
            )
            return {"feedback": response.model_dump(mode="json")}
        except LLMError:
            return {"feedback": self._build_local_feedback(state)}

    async def finalize_answer_feedback(self, state: AnswerFeedbackState) -> dict[str, Any]:
        feedback = state["feedback"]
        feedback["strengths"] = feedback.get("strengths") or ["回答已经围绕题目作答，没有明显跑题。"]
        feedback["weaknesses"] = feedback.get("weaknesses") or ["还可以补充更具体的技术细节和取舍。"]
        feedback["suggestions"] = feedback.get("suggestions") or ["先讲背景，再讲方案，最后讲取舍和结果。"]
        if not feedback.get("improved_answer"):
            feedback["improved_answer"] = (
                f"如果我来回答这道题，我会先明确问题背景，再说明我的处理思路、关键取舍和落地方式。"
                f"结合题目“{state['question_text']}”，我会重点补充系统约束、风险点，以及我会如何验证方案是否有效。"
            )
        return {"feedback": feedback}

    def _build_local_feedback(self, state: AnswerFeedbackState) -> dict[str, Any]:
        overlap = len(
            set(state["user_answer"].lower().split()) & set(state["reference_answer"].lower().split())
        )
        base_score = min(60 + overlap * 3, 88)
        return {
            "score_json": {
                "overall": base_score,
                "relevance": min(base_score + 4, 92),
                "clarity": min(base_score + 2, 90),
                "technical_depth": max(base_score - 6, 55),
            },
            "strengths": [
                "回答已经围绕题目作答，没有明显跑题。",
                "整体表达具备一定的工程语境。",
            ],
            "weaknesses": [
                "缺少更具体的技术拆解和方案取舍。",
                "和高质量参考回答相比，细节层次还不够完整。",
            ],
            "suggestions": [
                "先交代目标和约束，再说明实现路径。",
                "增加性能、稳定性或协作成本方面的权衡描述。",
            ],
            "improved_answer": (
                "如果我来进一步优化这道题的回答，我会先把问题背景和目标讲清楚，再说明我的拆解顺序。"
                "在具体方案上，我会补充为什么选择这种实现、它的边界条件是什么，以及上线后我会如何验证结果。"
            ),
        }
