from __future__ import annotations

from app.graph.builder import InterviewGraphRunner
from app.graph.practice import AnswerFeedbackGraphRunner, QuestionRegenerationGraphRunner

from tests.helpers import auth_headers, build_mock_graph_state


def test_user_answer_feedback_and_question_regeneration(client, monkeypatch) -> None:
    async def fake_run(self, **kwargs) -> dict:
        return build_mock_graph_state()

    async def fake_feedback_run(self, **kwargs) -> dict:
        return {
            "feedback": {
                "score_json": {
                    "overall": 84,
                    "relevance": 86,
                    "clarity": 82,
                    "technical_depth": 81,
                },
                "strengths": ["回答有结构。"],
                "weaknesses": ["技术细节还可以更具体。"],
                "suggestions": ["补充边界条件与取舍。"],
                "improved_answer": "如果我来优化，我会先讲背景，再讲方案和取舍。",
            }
        }

    async def fake_regenerate_run(self, **kwargs) -> dict:
        return {
            "final_item": {
                "difficulty": "easy",
                "category": "后端开发",
                "question": "重生成后的问题是什么？",
                "answer": "我会先确认上下文，再给出新的解法和取舍。",
                "intent": "考察候选人重新拆解问题的能力。",
                "reference_from_resume": "简历提到使用 FastAPI 构建业务系统。",
            }
        }

    monkeypatch.setattr(InterviewGraphRunner, "run", fake_run)
    monkeypatch.setattr(AnswerFeedbackGraphRunner, "run", fake_feedback_run)
    monkeypatch.setattr(QuestionRegenerationGraphRunner, "run", fake_regenerate_run)

    headers = auth_headers(client)
    generate_response = client.post(
        "/api/interviews/generate",
        headers=headers,
        files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    question_id = generate_response.json()["questions"][0]["id"]

    create_answer_response = client.post(
        f"/api/questions/{question_id}/my-answer",
        headers=headers,
        json={"answer_text": "我会先从接口边界、异常处理和日志这三个方面回答这个问题。"},
    )
    assert create_answer_response.status_code == 201

    get_answer_response = client.get(f"/api/questions/{question_id}/my-answer", headers=headers)
    assert get_answer_response.status_code == 200
    assert get_answer_response.json()["answer_text"].startswith("我会先从接口边界")

    feedback_response = client.post(f"/api/questions/{question_id}/feedback", headers=headers)
    assert feedback_response.status_code == 200
    assert feedback_response.json()["score_json"]["overall"] == 84

    regenerate_response = client.post(f"/api/questions/{question_id}/regenerate", headers=headers)
    assert regenerate_response.status_code == 200
    assert regenerate_response.json()["question"] == "重生成后的问题是什么？"
    assert regenerate_response.json()["my_answer"] is None
