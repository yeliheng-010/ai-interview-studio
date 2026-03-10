from __future__ import annotations

import re
from typing import Any

DEFAULT_TARGET_ROLE = "software engineer"
DEFAULT_INTERVIEW_STYLE = "standard"

TARGET_ROLE_OPTIONS = [
    "software engineer",
    "backend engineer",
    "frontend engineer",
    "full-stack engineer",
    "Java engineer",
    "Python engineer",
    "Go engineer",
    "test development engineer",
    "DevOps engineer",
    "algorithm engineer",
    "data engineer",
]

INTERVIEW_STYLE_OPTIONS = [
    "standard",
    "fundamentals-heavy",
    "project-deep-dive",
    "system-design-heavy",
    "algorithm-heavy",
    "real-world-scenario",
    "big-tech-style",
    "startup-practical-style",
]

DIFFICULTY_DISTRIBUTION = {"easy": 6, "medium": 8, "hard": 6}
VALID_DIFFICULTIES = set(DIFFICULTY_DISTRIBUTION.keys())
VALID_CATEGORIES = [
    "语言基础",
    "后端开发",
    "前端开发",
    "数据库",
    "系统设计",
    "算法与数据结构",
    "测试与质量",
    "DevOps",
    "项目经历",
    "架构设计",
    "工程实践",
    "安全",
]


def normalize_whitespace(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def resolve_target_role(value: str | None) -> str:
    normalized = normalize_whitespace(value)
    return normalized or DEFAULT_TARGET_ROLE


def resolve_interview_style(value: str | None) -> str:
    normalized = normalize_whitespace(value)
    return normalized or DEFAULT_INTERVIEW_STYLE


def resolve_job_description_text(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized


def normalize_question_key(question: str) -> str:
    lowered = normalize_whitespace(question).lower()
    lowered = re.sub(r"[^\w\u4e00-\u9fff]+", "", lowered)
    return lowered


def coerce_category(category: str | None) -> str:
    normalized = normalize_whitespace(category)
    if normalized in VALID_CATEGORIES:
        return normalized
    if "数据库" in normalized:
        return "数据库"
    if "前端" in normalized:
        return "前端开发"
    if "后端" in normalized or "接口" in normalized:
        return "后端开发"
    if "系统" in normalized or "架构" in normalized:
        return "系统设计"
    if "算法" in normalized or "复杂度" in normalized:
        return "算法与数据结构"
    if "测试" in normalized:
        return "测试与质量"
    if "部署" in normalized or "容器" in normalized:
        return "DevOps"
    if "安全" in normalized:
        return "安全"
    if "项目" in normalized or "经历" in normalized:
        return "项目经历"
    return "工程实践"


def coerce_difficulty(difficulty: str | None, expected: str) -> str:
    normalized = normalize_whitespace(difficulty).lower()
    if normalized in VALID_DIFFICULTIES:
        return normalized
    return expected


def build_reference_fallback(resume_summary: dict[str, Any]) -> str:
    evidence_notes = resume_summary.get("evidence_notes") or []
    if evidence_notes:
        return normalize_whitespace(evidence_notes[0])
    technical_stack = resume_summary.get("technical_stack") or []
    if technical_stack:
        return f"简历显示候选人涉及 {technical_stack[0]} 相关经验。"
    return "简历信息有限，以下答案采用通用程序员工程场景作答。"


def build_fallback_answer(
    *,
    question: str,
    difficulty: str,
    category: str,
    resume_summary: dict[str, Any],
    reference: str,
) -> str:
    technical_stack = resume_summary.get("technical_stack") or ["常见 Web 技术栈"]
    primary_stack = technical_stack[0]
    if difficulty == "easy":
        return (
            f"我会先把问题拆成输入、处理和输出三个最基本的部分，再结合 {primary_stack} 的经验给出一个稳妥实现。"
            "实际开发里我会先保证边界条件、日志和错误处理是清楚的，避免一开始就把问题做复杂。"
            f"如果和简历经历相关，我会补充说明 {reference} 对我处理这类问题的影响。"
        )
    if difficulty == "medium":
        return (
            f"我通常会先明确业务目标和约束，再从模块划分、数据流和异常处理三个层面回答。"
            f"对于这类 {category} 问题，我会结合 {primary_stack} 的实践经验说明为什么这么设计，并补充性能、可维护性和协作成本上的取舍。"
        )
    return (
        f"如果我在真实面试里回答这道题，我会先说明目标系统的吞吐、稳定性和演进边界，然后再谈技术选型和风险控制。"
        f"对于“{question}”这类高难度问题，我会把方案拆成架构分层、数据一致性、故障隔离和成本评估几个部分，"
        "最后给出一个可以渐进落地的实现路径，而不是直接给理想化答案。"
    )


def ensure_answer_quality(
    *,
    answer: str | None,
    question: str,
    difficulty: str,
    category: str,
    resume_summary: dict[str, Any],
    reference: str,
) -> str:
    normalized = normalize_whitespace(answer)
    generic_markers = ["教材", "百科", "sample answer", "候选人可以说"]
    if (
        len(normalized) < 40
        or "我" not in normalized
        or any(marker in normalized.lower() for marker in generic_markers)
    ):
        return build_fallback_answer(
            question=question,
            difficulty=difficulty,
            category=category,
            resume_summary=resume_summary,
            reference=reference,
        )
    return normalized


def normalize_generated_item(
    *,
    item: dict[str, Any],
    expected_difficulty: str,
    resume_summary: dict[str, Any],
) -> dict[str, Any]:
    question = normalize_whitespace(item.get("question"))
    category = coerce_category(item.get("category"))
    reference = normalize_whitespace(item.get("reference_from_resume")) or build_reference_fallback(
        resume_summary
    )
    difficulty = coerce_difficulty(item.get("difficulty"), expected_difficulty)
    intent = normalize_whitespace(item.get("intent")) or "考察候选人的工程理解、表达和取舍能力。"
    answer = ensure_answer_quality(
        answer=item.get("answer"),
        question=question,
        difficulty=difficulty,
        category=category,
        resume_summary=resume_summary,
        reference=reference,
    )
    return {
        "difficulty": difficulty,
        "category": category,
        "question": question,
        "answer": answer,
        "intent": intent,
        "reference_from_resume": reference,
    }


def build_local_question(
    *,
    difficulty: str,
    category: str,
    resume_summary: dict[str, Any],
    index_seed: int,
    target_role: str = DEFAULT_TARGET_ROLE,
) -> str:
    stacks = resume_summary.get("technical_stack") or ["常见 Web 技术栈"]
    themes = resume_summary.get("project_themes") or ["业务系统开发"]
    stack = stacks[index_seed % len(stacks)]
    theme = themes[index_seed % len(themes)]

    if difficulty == "easy":
        templates = [
            f"面向 {target_role} 岗位，你在 {stack} 开发里通常如何做代码分层，避免小功能越写越乱？",
            f"如果让你快速接手一个 {theme} 相关模块，你会先看哪些信息来降低理解成本？",
            f"你在日常开发中如何处理接口参数校验和错误返回，保证问题容易排查？",
        ]
    elif difficulty == "medium":
        templates = [
            f"结合 {stack} 的实际开发经验，你会如何设计一个可扩展的 {category} 方案？",
            f"如果 {theme} 模块在高峰期出现延迟上升，你会按什么顺序排查并定位瓶颈？",
            f"当需求频繁变动时，你会怎样控制模块边界，避免 {category} 设计不断返工？",
        ]
    else:
        templates = [
            f"如果你负责一个围绕 {theme} 的核心系统重构，你会如何平衡稳定性、交付节奏和架构演进？",
            f"面对跨服务的高并发场景，你会怎样设计 {category} 方案来兼顾一致性和可用性？",
            f"如果线上系统在复杂依赖链路中出现雪崩风险，你会如何设计止损和恢复策略？",
        ]
    return templates[index_seed % len(templates)]
