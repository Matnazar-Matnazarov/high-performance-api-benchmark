"""Health check endpoint tests."""

import pytest
import httpx


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_live(require_server):
    """GET /health returns 200 and status ok (requires running server)."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(f"{require_server}/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ready_live(require_server):
    """GET /ready returns 200 and status healthy (requires running server)."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(f"{require_server}/ready")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["status"] in ("healthy", "unhealthy")
    assert "checks" in data
