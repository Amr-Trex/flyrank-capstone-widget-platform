import sqlite3

from app.config import get_settings
# this script is used to establish a connection to the SQLite database
# and manage database connections throughout the application

def get_conn():
    settings = get_settings()
    try:
        conn = sqlite3.connect(settings.database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
    except sqlite3.Error as e:
        raise ConnectionError(f"Failed to connect to database: {e}")
        
    return conn
