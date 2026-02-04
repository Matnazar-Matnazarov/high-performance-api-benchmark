"""JWT auth and login tests."""

import pytest
import httpx


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_success(require_server):
    """POST /auth/login with valid credentials returns JWT (requires server + user)."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(
            f"{require_server}/auth/login",
            json={"username": "admin", "password": "admin"},
        )
    if r.status_code == 401:
        pytest.skip("No admin user or wrong password – create superuser first")
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"
    assert data.get("expires_in") > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_invalid_credentials(require_server):
    """POST /auth/login with invalid credentials returns 401."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(
            f"{require_server}/auth/login",
            json={"username": "nonexistent", "password": "wrong"},
        )
    assert r.status_code == 401
