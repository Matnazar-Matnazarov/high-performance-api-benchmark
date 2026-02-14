"""Run pytest. Usage: uv run test [--sqlite] [pytest args...]

--sqlite  Use SQLite for tests (avoids PostgreSQL collation issues)
"""

import os
import sys


def main():
    args = sys.argv[1:]
    if "--sqlite" in args:
        args.remove("--sqlite")
        os.environ["USE_SQLITE_FOR_TESTS"] = "1"
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings_test"
    import pytest

    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main())
