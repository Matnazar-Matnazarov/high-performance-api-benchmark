"""
Root conftest — set USE_SQLITE_FOR_TESTS override before pytest-django loads.
"""

import os

if os.environ.get("USE_SQLITE_FOR_TESTS"):
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings_test"
