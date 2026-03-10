from __future__ import annotations


def test_register_login_and_me(client) -> None:
    register_response = client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "securepass123"},
    )
    assert register_response.status_code == 201
    register_data = register_response.json()
    assert register_data["user"]["email"] == "user@example.com"
    assert register_data["access_token"]

    login_response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "securepass123"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"
