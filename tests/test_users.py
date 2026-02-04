"""User endpoints: list (pagination, search), get by id, me (JWT)."""

import pytest
import httpx


@pytest.mark.integration
@pytest.mark.asyncio
async def test_users_list_pagination(require_server):
    """GET /users returns paginated list (requires running server)."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(f"{require_server}/users?page=1&page_size=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert isinstance(data["items"], list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_users_search(require_server):
    """GET /users?search=... filters by username."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(f"{require_server}/users?search=admin")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    for item in data["items"]:
        assert "admin" in item.get("username", "").lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_users_me_requires_auth(require_server):
    """GET /users/me without JWT returns 401."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(f"{require_server}/users/me")
    assert r.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_users_me_with_jwt(require_server):
    """GET /users/me with valid JWT returns current user (requires admin user)."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        login_r = await client.post(
            f"{require_server}/auth/login",
            json={"username": "admin", "password": "admin"},
        )
    if login_r.status_code != 200:
        pytest.skip("Create superuser with username=admin, password=admin")
    token = login_r.json()["access_token"]
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(
            f"{require_server}/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert "username" in data
