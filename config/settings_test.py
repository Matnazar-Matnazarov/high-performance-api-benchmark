"""
Test settings — SQLite fallback when PostgreSQL has collation issues.

Set USE_SQLITE_FOR_TESTS=1 to use SQLite instead of PostgreSQL for tests.
Useful when: template database "template1" has a collation version mismatch.

To fix PostgreSQL collation instead:
  sudo -u postgres psql -c "ALTER DATABASE template1 REFRESH COLLATION VERSION;"
  sudo -u postgres psql -c "ALTER DATABASE postgres REFRESH COLLATION VERSION;"
"""

import os

from .settings import *  # noqa: F401, F403

if os.environ.get("USE_SQLITE_FOR_TESTS"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
