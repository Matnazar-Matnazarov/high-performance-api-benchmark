"""User endpoints: list, search, get by id, me (JWT) — sync, in-process."""

import pytest


@pytest.mark.django_db(transaction=True)
def test_users_list_pagination(client):
    """GET /users returns paginated list."""
    r = client.get("/users?page=1&page_size=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert isinstance(data["items"], list)


@pytest.mark.django_db(transaction=True)
def test_users_search(client, test_user):
    """GET /users?search=... filters by username."""
    r = client.get("/users?search=admin")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    for item in data["items"]:
        assert "admin" in item.get("username", "").lower()


def test_users_me_requires_auth(client):
    """GET /users/me without JWT returns 401."""
    r = client.get("/users/me")
    assert r.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_users_me_with_jwt(client, test_user):
    """GET /users/me with valid JWT returns current user."""
    login_r = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert login_r.status_code == 200
    token = login_r.json()["access_token"]
    r = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == test_user.id
    assert data["username"] == "admin"
    assert "role" in data
