# custom database migration tool for a SQLite database...
# its purpose is to automatically run SQL scripts to update the database schema 
# and keep track of which scripts have already been applied so they don't run twice

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "widget_platform.sqlite3")
MIGRATIONS_DIR = Path("migrations")


def main():
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
          name TEXT PRIMARY KEY,
          applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )

    # iterates over all files in the migrations directory with the extension .sql
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        already_applied = conn.execute(
            "SELECT 1 FROM schema_migrations WHERE name = ?",
            (path.name,),
        ).fetchone()

        # if the migration has already been applied, then we skip it
        if already_applied:
            print(f"Skipping {path.name}, already applied")
            continue

        print(f"Applying {path.name}")
        sql = path.read_text()
        conn.executescript(sql)

        conn.execute(
            "INSERT INTO schema_migrations (name) VALUES (?)",
            (path.name,),
        )
        conn.commit()

    conn.close()
    print("Migrations complete")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)