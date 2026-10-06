import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.database_path = os.getenv("DATABASE_PATH", "widget_platform.sqlite3")
        self.public_base_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

        self.allowed_origins = [
            origin.strip()
            for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
            if origin.strip()
        ]

        self.max_submission_bytes = int(os.getenv("MAX_SUBMISSION_BYTES", "10000"))
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))
        self.geo_mode = os.getenv("GEO_MODE", "mock")
        self.email_mode = os.getenv("EMAIL_MODE", "console")


@lru_cache
def get_settings():
    return Settings()