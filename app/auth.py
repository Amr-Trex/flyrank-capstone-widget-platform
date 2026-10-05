from fastapi import Header, HTTPException, status

from app.db import get_conn
# this script is used to handle authentication and authorization for the application
# it uses a simple API key-based authentication system
# it takes the X-API-Key header from the request and validates it against the database

def get_current_owner(x_api_key: str | None = Header(default=None, alias="X-API-Key"), ):
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, name FROM owners WHERE api_key = ?",
            (x_api_key,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return dict(row)

