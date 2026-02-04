"""
Pytest configuration and fixtures.

Unit tests run without a server. Integration tests require a running server;
if the server is not reachable, they are skipped (no failure).

Start server for integration tests:
    uv run manage.py runbolt --dev --host localhost --port 8000
Then: pytest tests/ -v
Skip integration: pytest tests/ -v -m "not integration"
"""

import os
import sys

import django
import pytest

# Project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for API. Override with env BASE_URL or default localhost:8000."""
    return os.environ.get("BASE_URL", "http://localhost:8000")


@pytest.fixture
async def require_server(api_base_url):
    """Skip integration test if API server is not reachable."""
    try:
        import httpx

        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.get(f"{api_base_url}/health")
    except (httpx.ConnectError, OSError, Exception):
        pytest.skip(
            "API server not running. Start: "
            "uv run manage.py runbolt --dev --host localhost --port 8000"
        )
    return api_base_url
