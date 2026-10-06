import json
import uuid

from app.db import get_conn


def _row_to_widget(row):
    '''
    This function is used to convert a row from the database to a widget dictionary.
    It is used by the list_widgets and get_widget_by_public_id functions.
    '''
    widget = dict(row)

    widget.pop("id", None)
    widget.pop("owner_id", None)

    fields_json = widget.pop("fields_json", "[]")

    try:
        widget["fields"] = json.loads(fields_json)
    except json.JSONDecodeError:
        widget["fields"] = []

    return widget


def create_widget(owner_id: int, data: dict):
    '''
    Creates a new widget for the given owner.
    '''
    public_id = uuid.uuid4().hex[:12]
    fields_json = json.dumps(data.get("fields", []))

    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO widgets (
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
            (
                owner_id,
                public_id,
                data.get("type", "signup_form"),
                data["title"],
                data.get("description", ""),
                data.get("button_text", "Submit"),
                fields_json,
                "active",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return get_widget_by_public_id(owner_id, public_id)


def list_widgets(owner_id: int):
    '''
    Lists all widgets for the given owner.
    '''
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT *
            FROM widgets
            WHERE owner_id = ?
            ORDER BY created_at DESC
            """,
            (owner_id,),
        ).fetchall()
    finally:
        conn.close()

    return [_row_to_widget(row) for row in rows]


def get_widget_by_public_id(owner_id: int, public_id: str):
    conn = get_conn()
    try:
        row = conn.execute(
            """
            SELECT *
            FROM widgets
            WHERE public_id = ?
              AND owner_id = ?
            """,
            (public_id, owner_id),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return _row_to_widget(row)


def update_widget(owner_id: int, public_id: str, updates: dict):
    if "fields" in updates and updates["fields"] is not None:
        updates["fields_json"] = json.dumps(updates.pop("fields"))
    else:
        updates.pop("fields", None)

    allowed_columns = {
        "title",
        "description",
        "button_text",
        "status",
        "fields_json",
    }

    clean_updates = {
        key: value
        for key, value in updates.items()
        if key in allowed_columns
    }

    if not clean_updates:
        return get_widget_by_public_id(owner_id, public_id)

    set_clause = ", ".join(f"{key} = ?" for key in clean_updates.keys())
    values = list(clean_updates.values()) + [public_id, owner_id]

    conn = get_conn()
    try:
        conn.execute(
            f"""
            UPDATE widgets
            SET {set_clause}
            WHERE public_id = ?
              AND owner_id = ?
            """,
            values,
        )
        conn.commit()
    finally:
        conn.close()

    return get_widget_by_public_id(owner_id, public_id)


def delete_widget(owner_id: int, public_id: str):
    conn = get_conn()
    try:
        cursor = conn.execute(
            """
            DELETE FROM widgets
            WHERE public_id = ?
              AND owner_id = ?
            """,
            (public_id, owner_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


        