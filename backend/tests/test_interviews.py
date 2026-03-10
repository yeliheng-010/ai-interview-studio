from __future__ import annotations

from app.graph.builder import InterviewGraphRunner

from tests.helpers import auth_headers, build_mock_graph_state


def test_generate_interview_persists_full_set(client, monkeypatch) -> None:
    async def fake_run(self, **kwargs) -> dict:
        return build_mock_graph_state()

    monkeypatch.setattr(InterviewGraphRunner, "run", fake_run)
    headers = auth_headers(client)

    response = client.post(
        "/api/interviews/generate",
        headers=headers,
        data={"target_role": "backend engineer", "interview_style": "project-deep-dive"},
        files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "backend engineer 模拟面试题集"
    assert payload["target_role"] == "backend engineer"
    assert payload["interview_style"] == "project-deep-dive"
    assert payload["difficulty_breakdown"] == {"easy": 6, "medium": 8, "hard": 6}
    assert len(payload["questions"]) == 20

    list_response = client.get("/api/interviews", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1


def test_regenerate_interview_creates_new_set(client, monkeypatch) -> None:
    async def fake_run(self, **kwargs) -> dict:
        return build_mock_graph_state()

    async def fake_run_from_text(self, **kwargs) -> dict:
        state = build_mock_graph_state()
        state["title"] = "backend engineer 重生成题集"
        return state

    monkeypatch.setattr(InterviewGraphRunner, "run", fake_run)
    monkeypatch.setattr(InterviewGraphRunner, "run_from_text", fake_run_from_text)

    headers = auth_headers(client)
    generate_response = client.post(
        "/api/interviews/generate",
        headers=headers,
        files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    source_id = generate_response.json()["id"]

    regenerate_response = client.post(f"/api/interviews/{source_id}/regenerate", headers=headers)
    assert regenerate_response.status_code == 200
    assert regenerate_response.json()["title"] == "backend engineer 重生成题集"
