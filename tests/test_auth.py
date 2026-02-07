"""JWT auth and login tests (sync, in-process TestClient)."""

import pytest


@pytest.mark.django_db(transaction=True)
def test_login_success(client, test_user):
    """POST /auth/login with valid credentials returns JWT."""
    r = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"
    assert data.get("expires_in") > 0


@pytest.mark.django_db(transaction=True)
def test_login_invalid_credentials(client):
    """POST /auth/login with invalid credentials returns 401."""
    r = client.post(
        "/auth/login",
        json={"username": "nonexistent", "password": "wrong"},
    )
    assert r.status_code == 401
