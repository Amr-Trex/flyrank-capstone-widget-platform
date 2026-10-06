import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "widget_platform.sqlite3")


def main():
    conn = sqlite3.connect(DB_PATH)

    rows = conn.execute(
        """
        SELECT
          id,
          widget_public_id,
          data_json,
          ip_address,
          created_at
        FROM submissions
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    if not rows:
        print("No submissions found.")
        return

    for row in rows:
        print(row)

    conn.close()


if __name__ == "__main__":
    main()