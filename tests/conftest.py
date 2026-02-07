"""
Pytest configuration and fixtures.

Uses django_bolt's sync TestClient so the request handler runs in the same
thread as the test; then pytest-django's db fixture allows database access.
No live server; no skips.
"""

import os
import sys

import django
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


@pytest.fixture
def api():
    """BoltAPI instance with all routes registered."""
    from api import api as app

    return app


@pytest.fixture
def client(api):
    """Sync HTTP client; handler runs in test thread so DB is allowed."""
    from django_bolt.testing import TestClient

    with TestClient(api) as c:
        yield c


@pytest.fixture(autouse=True)
def _close_db_connections_after_test():
    """Close all DB connections after each test so PostgreSQL teardown can drop the test DB."""
    yield
    from django.db import connections

    connections.close_all()


def _terminate_postgres_test_sessions():
    """Terminate all other connections to the test DB so pytest-django can drop it (PostgreSQL only)."""
    from django.conf import settings
    from django.db import connections

    db_settings = settings.DATABASES.get("default", {})
    if "postgresql" not in (db_settings.get("ENGINE") or ""):
        connections.close_all()
        return

    name = db_settings.get("NAME", "")
    if not name.startswith("test_"):
        connections.close_all()
        return

    # Use a fresh connection so we don't rely on Django's connection state at teardown
    try:
        import psycopg2

        conn = psycopg2.connect(
            dbname=name,
            user=db_settings.get("USER"),
            password=db_settings.get("PASSWORD"),
            host=db_settings.get("HOST"),
            port=db_settings.get("PORT"),
            connect_timeout=2,
        )
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid();
                    """,
                    [name],
                )
        finally:
            conn.close()
    except Exception:
        pass
    finally:
        connections.close_all()


@pytest.fixture(scope="session", autouse=True)
def _postgres_teardown_connections(django_db_setup):
    """Run after django_db_setup so we are torn down first: terminate other PG sessions, then DB can be dropped."""
    yield
    _terminate_postgres_test_sessions()


@pytest.fixture
def test_user(transactional_db):
    """User for login/me tests (username=admin, password=admin). Committed so handler thread can read."""
    from django.contrib.auth import get_user_model
    from accounts.models import Role

    User = get_user_model()
    return User.objects.create_user(
        username="admin",
        password="admin",
        email="admin@test.local",
        role=Role.ADMIN,
    )
