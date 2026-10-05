import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()
# this script is used to manage the configuration and settings for the application
# in a way that can be easily imported and used throughout the codebase

class Settings:
    def __init__(self):
        self.database_path = os.getenv("DATABASE_PATH", "widget_platform.sqlite3")
        self.public_base_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")
        self.allowed_origins = [
            origin.strip()
            for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings():
    return Settings()