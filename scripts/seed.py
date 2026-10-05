
# this script is so that we can add "dummy" seeding data into the widget database for testing
import json
import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "widget_platform.sqlite3")


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")

    # owners dummy data
    owners = [
        ("Owner A", "demo-key-owner-a"),
        ("Owner B", "demo-key-owner-b"),
    ]

    for name, api_key in owners:
        conn.execute(
            "INSERT OR IGNORE INTO owners (name, api_key) VALUES (?, ?)",
            (name, api_key),
        )

    # getting the id of each created owner
    owner_a = conn.execute(
        "SELECT id FROM owners WHERE api_key = ?",
        ("demo-key-owner-a",),
    ).fetchone()[0]

    owner_b = conn.execute(
        "SELECT id FROM owners WHERE api_key = ?",
        ("demo-key-owner-b",),
    ).fetchone()[0]

    # the fields for each widget for each owner
    fields_a = json.dumps(
        [
            {
                "name": "email",
                "label": "Email",
                "type": "email",
                "required": True,
            }
        ]
    )

    fields_b = json.dumps(
        [
            {
                "name": "name",
                "label": "Name",
                "type": "text",
                "required": True,
            },
            {
                "name": "message",
                "label": "Message",
                "type": "textarea",
                "required": True,
            },
        ]
    )

    # widgets dummy data relating to each owner
    widgets = [
        (
            owner_a,
            "widget-a-123",
            "signup_form",
            "Newsletter Signup",
            "Get product updates",
            "Subscribe",
            fields_a,
            "active",
        ),
        (
            owner_b,
            "widget-b-123",
            "cta",
            "Contact Us",
            "Talk to our team",
            "Send",
            fields_b,
            "active",
        ),
    ]

    for widget in widgets:
        conn.execute(
            """
            INSERT OR IGNORE INTO widgets (
              owner_id,
              public_id,
              type,
              title,
              description,
              button_text,
              fields_json,
              status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            widget,
        )

    conn.commit()
    conn.close()

    print("Seed complete.")
    print("Owner A API key: demo-key-owner-a")
    print("Owner B API key: demo-key-owner-b")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)