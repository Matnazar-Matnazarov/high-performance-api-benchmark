"""
Management command to fix PostgreSQL collation version mismatch.

Run: uv run manage.py fix_db_collation

Requires DB_USER to have superuser or CREATEDB privileges.
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Fix PostgreSQL collation version mismatch (ALTER DATABASE ... REFRESH COLLATION VERSION)"

    def handle(self, *args, **options):
        if connection.vendor != "postgresql":
            self.stdout.write(
                self.style.WARNING("Not PostgreSQL; skipping collation fix.")
            )
            return

        db_settings = connection.settings_dict
        db_name = db_settings["NAME"]

        try:
            import psycopg2
            from psycopg2.sql import SQL, Identifier
        except ImportError:
            self.stderr.write("psycopg2 required. Run: uv add psycopg2-binary")
            return

        # Connect to 'postgres' to run ALTER on our database
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_settings["USER"],
            password=db_settings["PASSWORD"],
            host=db_settings["HOST"],
            port=db_settings["PORT"],
        )
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(
                    SQL("ALTER DATABASE {} REFRESH COLLATION VERSION").format(
                        Identifier(db_name)
                    )
                )
            self.stdout.write(
                self.style.SUCCESS(f"Collation refreshed for database '{db_name}'.")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"Failed: {e}\n"
                    "Ensure DB_USER has superuser. Or run manually in psql:\n"
                    f"  ALTER DATABASE {db_name} REFRESH COLLATION VERSION;"
                )
            )
        finally:
            conn.close()
