import json
import sqlite3
# this script acts as the Data Access Layer 
# for handling the data submitted by end-users through the public widgets
from app.db import get_conn


def _row_to_internal_widget(row):
    widget = dict(row)

    fields_json = widget.pop("fields_json", "[]")

    try:
        widget["fields"] = json.loads(fields_json)
    except json.JSONDecodeError:
        widget["fields"] = []

    return widget


def get_active_widget_internal(public_id: str):
    conn = get_conn()
    try:
        row = conn.execute(
            """
            SELECT *
            FROM widgets
            WHERE public_id = ?
              AND status = 'active'
            """,
            (public_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return _row_to_internal_widget(row)


def _row_to_submission(row):
    submission = dict(row)

    submission.pop("owner_id", None)

    data_json = submission.pop("data_json", "{}")

    try:
        submission["data"] = json.loads(data_json)
    except json.JSONDecodeError:
        submission["data"] = {}

    return submission


def get_submission_by_id(submission_id: int):
    conn = get_conn()
    try:
        row = conn.execute(
            """
            SELECT *
            FROM submissions
            WHERE id = ?
            """,
            (submission_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return _row_to_submission(row)


def find_submission_by_idempotency(widget_public_id: str, idempotency_key: str):
    if not idempotency_key:
        return None

    conn = get_conn()
    try:
        row = conn.execute(
            """
            SELECT *
            FROM submissions
            WHERE widget_public_id = ?
              AND idempotency_key = ?
            """,
            (widget_public_id, idempotency_key),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return _row_to_submission(row)


def create_submission(
    widget: dict,
    data: dict,
    ip_address: str,
    geo: dict | None,
    idempotency_key: str | None,
):
    geo = geo or {}
    data_json = json.dumps(data)

    conn = get_conn()
    try:
        cursor = conn.execute(
            """
            INSERT INTO submissions (
              widget_public_id,
              owner_id,
              data_json,
              ip_address,
              geo_country,
              geo_city,
              geo_provider,
              idempotency_key
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                widget["public_id"],
                widget["owner_id"],
                data_json,
                ip_address,
                geo.get("country"),
                geo.get("city"),
                geo.get("provider"),
                idempotency_key,
            ),
        )
        conn.commit()
        submission_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        if idempotency_key:
            existing = find_submission_by_idempotency(
                widget["public_id"],
                idempotency_key,
            )
            if existing:
                return existing, False
        raise
    finally:
        conn.close()

    return get_submission_by_id(submission_id), True