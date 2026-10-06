import json

from app.db import get_conn


def _row_to_submission(row):
    submission = dict(row)

    submission.pop("owner_id", None)

    data_json = submission.pop("data_json", "{}")

    try:
        submission["data"] = json.loads(data_json)
    except json.JSONDecodeError:
        submission["data"] = {}

    return submission


def list_owner_submissions(owner_id: int, widget_public_id: str | None, limit: int):
    conn = get_conn()

    query = """
        SELECT *
        FROM submissions
        WHERE owner_id = ?
    """

    params = [owner_id]

    if widget_public_id:
        query += " AND widget_public_id = ?"
        params.append(widget_public_id)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    try:
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()

    return [_row_to_submission(row) for row in rows]


def get_owner_stats(owner_id: int, days: int):
    conn = get_conn()

    days = int(days)
    modifier = f"-{days} days"

    try:
        total_row = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM submissions
            WHERE owner_id = ?
            """,
            (owner_id,),
        ).fetchone()

        per_widget_rows = conn.execute(
            """
            SELECT
              widget_public_id,
              COUNT(*) AS submission_count
            FROM submissions
            WHERE owner_id = ?
            GROUP BY widget_public_id
            ORDER BY submission_count DESC
            """,
            (owner_id,),
        ).fetchall()

        per_day_rows = conn.execute(
            f"""
            SELECT
              date(created_at) AS day,
              COUNT(*) AS submission_count
            FROM submissions
            WHERE owner_id = ?
              AND created_at >= datetime('now', '{modifier}')
            GROUP BY day
            ORDER BY day
            """,
            (owner_id,),
        ).fetchall()

        geo_rows = conn.execute(
            """
            SELECT
              COALESCE(geo_country, 'unknown') AS country,
              COUNT(*) AS submission_count
            FROM submissions
            WHERE owner_id = ?
            GROUP BY country
            ORDER BY submission_count DESC
            """,
            (owner_id,),
        ).fetchall()
    finally:
        conn.close()

    return {
        "total_submissions": total_row["total"],
        "window_days": days,
        "per_widget": [dict(row) for row in per_widget_rows],
        "per_day": [dict(row) for row in per_day_rows],
        "geo_breakdown": [dict(row) for row in geo_rows],
    }