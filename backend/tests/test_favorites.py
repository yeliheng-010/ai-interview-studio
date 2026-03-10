from __future__ import annotations

from app.graph.builder import InterviewGraphRunner

from tests.helpers import auth_headers, build_mock_graph_state


def test_favorite_and_unfavorite_question(client, monkeypatch) -> None:
    async def fake_run(self, **kwargs) -> dict:
        return build_mock_graph_state()

    monkeypatch.setattr(InterviewGraphRunner, "run", fake_run)
    headers = auth_headers(client)

    generate_response = client.post(
        "/api/interviews/generate",
        headers=headers,
        files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    question_id = generate_response.json()["questions"][0]["id"]

    favorite_response = client.post(f"/api/questions/{question_id}/favorite", headers=headers)
    assert favorite_response.status_code == 200
    assert favorite_response.json()["is_favorited"] is True

    favorites_response = client.get("/api/favorites", headers=headers)
    assert favorites_response.status_code == 200
    favorites = favorites_response.json()
    assert len(favorites) == 1
    assert favorites[0]["question_id"] == question_id

    unfavorite_response = client.delete(f"/api/questions/{question_id}/favorite", headers=headers)
    assert unfavorite_response.status_code == 200
    assert unfavorite_response.json()["is_favorited"] is False
