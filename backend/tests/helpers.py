from __future__ import annotations

from fastapi.testclient import TestClient


def auth_headers(
    client: TestClient,
    *,
    email: str = "tester@example.com",
    password: str = "strongpass123",
) -> dict[str, str]:
    register_response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )
    token = register_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def build_mock_graph_state() -> dict:
    final_items = []
    difficulty_plan = [("easy", 6), ("medium", 8), ("hard", 6)]
    for difficulty, count in difficulty_plan:
        for index in range(count):
            final_items.append(
                {
                    "difficulty": difficulty,
                    "category": "后端开发",
                    "question": f"{difficulty} 难度问题 {index + 1} 是什么？",
                    "answer": f"我会先明确目标，再给出 {difficulty} 难度下的工程判断和实现取舍。",
                    "intent": "考察工程思考与表达能力。",
                    "reference_from_resume": "简历显示候选人有 Python 和 API 开发经验。",
                }
            )
    return {
        "file_name": "resume.pdf",
        "raw_text": "Python FastAPI PostgreSQL Redis Docker Kubernetes 微服务 项目经历 技术栈 工作经历",
        "cleaned_text": "Python FastAPI PostgreSQL Redis Docker Kubernetes 微服务 项目经历 技术栈 工作经历",
        "extraction_status": "validated",
        "extraction_quality_score": 88.5,
        "extraction_error_message": None,
        "target_role": "backend engineer",
        "interview_style": "project-deep-dive",
        "resume_summary": {
            "summary": "一名偏后端的软件工程师，熟悉 Python、FastAPI 和数据库设计。",
            "technical_stack": ["Python", "FastAPI", "PostgreSQL"],
            "seniority": "中级",
            "project_themes": ["API 平台", "数据服务"],
            "domains": ["企业软件"],
            "strengths": ["接口设计", "数据建模"],
            "evidence_notes": ["简历提到使用 FastAPI 和 PostgreSQL 构建业务系统。"],
        },
        "strategy": {
            "target_role": "backend engineer",
            "interview_style": "project-deep-dive",
            "focus_areas": ["后端开发", "数据库", "系统设计"],
            "emphasis": ["真实项目经验", "工程取舍"],
            "fallback_used": False,
            "difficulty_distribution": {"easy": 6, "medium": 8, "hard": 6},
            "interview_tone": "真实程序员技术面试",
        },
        "final_items": final_items,
        "title": "backend engineer 面试训练题集",
        "meta": {
            "difficulty_breakdown": {"easy": 6, "medium": 8, "hard": 6},
            "categories": ["后端开发"],
            "total_questions": 20,
            "file_name": "resume.pdf",
            "target_role": "backend engineer",
            "interview_style": "project-deep-dive",
            "extraction_status": "validated",
            "extraction_quality_score": 88.5,
        },
    }
