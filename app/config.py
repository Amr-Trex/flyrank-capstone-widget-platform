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

        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "1025"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_security = os.getenv("SMTP_SECURITY", "none").lower()

        self.email_from = os.getenv("EMAIL_FROM", "widget-platform@example.local")
        self.notification_email = os.getenv("NOTIFICATION_EMAIL", "owner@example.com")

        if self.smtp_security not in {"none", "starttls", "ssl"}:
            self.smtp_security = "none"


@lru_cache
def get_settings():
    return Settings()