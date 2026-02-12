"""DRF API tests: health, auth, roles, users."""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def drf_client():
    """DRF API client for /drf/ endpoints."""
    return APIClient()


@pytest.mark.django_db(transaction=True)
def test_drf_health(drf_client):
    """GET /drf/health/ returns 200."""
    r = drf_client.get("/drf/health/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.django_db(transaction=True)
def test_drf_health_test(drf_client):
    """GET /drf/health/test/ returns 200."""
    r = drf_client.get("/drf/health/test/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["message"] == "Test health check endpoint"


@pytest.mark.django_db(transaction=True)
def test_drf_ready(drf_client):
    """GET /drf/ready/ returns 200 with DB check."""
    r = drf_client.get("/drf/ready/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("healthy", "unhealthy")
    assert "checks" in data


@pytest.mark.django_db(transaction=True)
def test_drf_roles_list(drf_client):
    """GET /drf/roles/ returns role list."""
    r = drf_client.get("/drf/roles/")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(item["code"] == "ADMIN" for item in data)


@pytest.mark.django_db(transaction=True)
def test_drf_roles_detail(drf_client):
    """GET /drf/roles/code/ADMIN/ returns role."""
    r = drf_client.get("/drf/roles/code/ADMIN/")
    assert r.status_code == 200
    assert r.json() == {"code": "ADMIN", "name": "Administrator"}


@pytest.mark.django_db(transaction=True)
def test_drf_users_list(drf_client):
    """GET /drf/users/ returns paginated list."""
    r = drf_client.get("/drf/users/")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    assert isinstance(data["results"], list)


@pytest.mark.django_db(transaction=True)
def test_drf_login_success(drf_client, test_user):
    """POST /drf/auth/login/ with valid credentials returns Bolt-style JWT."""
    r = drf_client.post(
        "/drf/auth/login/",
        {"username": "admin", "password": "admin"},
        format="json",
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"


@pytest.mark.django_db(transaction=True)
def test_drf_login_invalid(drf_client):
    """POST /drf/auth/login/ with invalid credentials returns 401."""
    r = drf_client.post(
        "/drf/auth/login/",
        {"username": "nonexistent", "password": "wrong"},
        format="json",
    )
    assert r.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_drf_users_me_requires_auth(drf_client):
    """GET /drf/users/me/ without JWT returns 401."""
    r = drf_client.get("/drf/users/me/")
    assert r.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_drf_users_me_with_jwt(drf_client, test_user):
    """GET /drf/users/me/ with valid JWT returns current user."""
    login_r = drf_client.post(
        "/drf/auth/login/",
        {"username": "admin", "password": "admin"},
        format="json",
    )
    assert login_r.status_code == 200
    token = login_r.json()["access_token"]
    drf_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    r = drf_client.get("/drf/users/me/")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == test_user.id
    assert data["username"] == "admin"
    assert "role" in data
