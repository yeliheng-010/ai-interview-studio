from __future__ import annotations

import random
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
    "ai application engineer",
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

LEETCODE_BONUS_COUNT = 2

LEETCODE_QUESTION_BANK = [
    {
        "id": 146,
        "title": "LRU Cache",
        "difficulty": "hard",
        "prompt": "请你设计并实现 LRU 缓存，要求 `get` 和 `put` 都是 O(1)。你会如何选择数据结构并处理更新顺序？",
        "answer": (
            "我会用哈希表加双向链表来实现。哈希表负责 O(1) 定位节点，双向链表负责维护最近使用顺序。"
            "每次 `get` 命中或 `put` 更新时，我都会把对应节点移动到链表头。插入新节点时如果超容量，就淘汰链表尾节点并同步删除哈希表映射。"
            "这样可以保证访问和更新都维持 O(1)，并且边界上要注意重复 put、容量为 1 以及命中后顺序刷新。"
        ),
        "intent": "考察哈希表与链表组合建模、复杂度分析和边界处理能力。",
    },
    {
        "id": 560,
        "title": "Subarray Sum Equals K",
        "difficulty": "medium",
        "prompt": "给定整数数组和 `k`，统计和为 `k` 的连续子数组个数。你会如何把时间复杂度降到 O(n)？",
        "answer": (
            "我会用前缀和加哈希计数来做。遍历到位置 i 时，当前前缀和是 `pre`，如果之前出现过 `pre-k`，就说明存在若干个区间和为 k。"
            "所以每一步先累计答案 `count += freq[pre-k]`，再把当前 `pre` 的出现次数加一。初始化 `freq[0]=1` 可以覆盖从下标 0 开始的区间。"
            "这个方法是 O(n) 时间、O(n) 空间，关键是理解“区间和 = 两个前缀和之差”。"
        ),
        "intent": "考察前缀和建模能力、哈希计数技巧和复杂度优化能力。",
    },
    {
        "id": 215,
        "title": "Kth Largest Element in an Array",
        "difficulty": "medium",
        "prompt": "在无序数组中找第 k 大元素，你会优先选择什么方案？不同方案的复杂度如何权衡？",
        "answer": (
            "我通常先给出两种方案：最小堆和快速选择。最小堆维护大小为 k 的堆，遍历数组时把更大的元素入堆并弹出堆顶，复杂度是 O(n log k)。"
            "快速选择基于分区思想，平均 O(n) 但最坏 O(n^2)。面试里我会先实现最小堆保证稳定正确，再说明如果追求平均性能可用随机化 quickselect。"
            "同时我会关注重复元素、k 的边界和原地修改副作用。"
        ),
        "intent": "考察候选人在多解场景下的复杂度取舍和实现稳定性。",
    },
    {
        "id": 239,
        "title": "Sliding Window Maximum",
        "difficulty": "hard",
        "prompt": "长度为 `k` 的滑动窗口最大值问题，你会如何用 O(n) 时间完成？",
        "answer": (
            "我会用单调队列。队列里存下标，并保持对应值单调递减。每次窗口右移时，先弹掉队尾所有小于当前值的元素，再把当前下标入队；"
            "然后如果队首下标已经滑出窗口范围就弹出。此时队首就是当前窗口最大值。"
            "这个方法每个元素最多进出队一次，所以总复杂度 O(n)。实现上我会重点处理窗口初始化和边界 `k=1`。"
        ),
        "intent": "考察单调队列思想、线性复杂度证明和边界处理能力。",
    },
    {
        "id": 297,
        "title": "Serialize and Deserialize Binary Tree",
        "difficulty": "hard",
        "prompt": "二叉树序列化与反序列化你会怎样设计协议，保证可还原且实现清晰？",
        "answer": (
            "我会选层序遍历方案，用逗号分隔节点值，空节点用 `#` 占位。序列化时按队列 BFS 输出，反序列化时同样按顺序重建左右子节点。"
            "这个协议可读性好，也容易验证正确性。时间复杂度是 O(n)，空间复杂度也是 O(n)。"
            "我会特别关注尾部连续空节点的处理、负数值解析和空树场景，保证编码解码是一一对应的。"
        ),
        "intent": "考察数据结构编码能力、协议设计意识和可逆性验证能力。",
    },
    {
        "id": 199,
        "title": "Binary Tree Right Side View",
        "difficulty": "medium",
        "prompt": "给定二叉树，返回从右侧看到的节点。你会选择 BFS 还是 DFS，为什么？",
        "answer": (
            "我会优先用 BFS 按层遍历，因为每层最后访问到的节点就是右视图结果，逻辑直观且不容易错。"
            "DFS 也可以做，按“根-右-左”顺序遍历并记录每层首次出现的节点。"
            "如果我在面试里写代码，我会先实现 BFS 确保可读性，再补充 DFS 作为等价解法。"
            "复杂度方面两者都是 O(n)，空间取决于树的宽度或高度。"
        ),
        "intent": "考察树遍历策略选择、表达清晰度和复杂度分析能力。",
    },
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


def build_random_leetcode_items(
    *,
    resume_summary: dict[str, Any],
    count: int = LEETCODE_BONUS_COUNT,
) -> list[dict[str, Any]]:
    if count <= 0:
        return []

    selected = random.sample(LEETCODE_QUESTION_BANK, k=min(count, len(LEETCODE_QUESTION_BANK)))
    reference = (
        "这是一道附加 LeetCode 算法题，用于检验编码与复杂度分析能力。"
        if resume_summary.get("technical_stack")
        else "简历信息有限，附加算法题按通用程序员场景评估。"
    )
    items: list[dict[str, Any]] = []
    for item in selected:
        items.append(
            {
                "difficulty": item["difficulty"],
                "category": "算法与数据结构",
                "question": f"LeetCode {item['id']}. {item['title']}：{item['prompt']}",
                "answer": item["answer"],
                "intent": item["intent"],
                "reference_from_resume": reference,
            }
        )
    return items
