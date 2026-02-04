"""Health check routes: /health, /ready."""

from django_bolt.health import add_health_check, register_health_checks


async def check_custom():
    """Optional custom health check (e.g. Redis later)."""
    return True, "OK"


def register(api):
    """Register health endpoints on the given BoltAPI."""
    register_health_checks(api)
    add_health_check(check_custom)
