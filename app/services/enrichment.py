import smtplib
import ssl
import time
from email.message import EmailMessage

from app.config import get_settings

settings = get_settings()


def enrich_geo(ip_address: str) -> dict | None:
    """
    Fallback chain: Provider A -> Provider B -> None.
    Mocked to be deterministic for the capstone proof.
    """
    time.sleep(0.1)

    # Mock Provider A
    try:
        if settings.geo_mode == "mock_a_down":
            raise ConnectionError("Provider A is down")

        print(f"[GEO] Provider A succeeded for {ip_address}")
        return {
            "country": "US",
            "city": "New York",
            "provider": "A",
        }
    except Exception as error:
        print(f"[GEO] Provider A failed: {error}. Trying Provider B...")

    # Mock Provider B
    try:
        if settings.geo_mode == "mock_both_down":
            raise ConnectionError("Provider B is down")

        print(f"[GEO] Provider B succeeded for {ip_address}")
        return {
            "country": "UK",
            "city": "London",
            "provider": "B",
        }
    except Exception as error:
        print(f"[GEO] Provider B failed: {error}. Degrading gracefully.")

    return None


def _build_email_body(widget: dict, data: dict) -> str:
    lines = [
        f"New submission for widget: {widget.get('title', 'Unknown widget')}",
        f"Widget ID: {widget.get('public_id', 'Unknown')}",
        "",
        "Submission data:",
    ]

    if not data:
        lines.append("(empty)")

    for key, value in data.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def _send_smtp_email(to_email: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.email_from
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    if settings.smtp_security == "ssl":
        with smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            timeout=5,
        ) as server:
            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password)

            server.send_message(message)

        return

    with smtplib.SMTP(
        settings.smtp_host,
        settings.smtp_port,
        timeout=5,
    ) as server:
        if settings.smtp_security == "starttls":
            server.starttls(context=ssl.create_default_context())

        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)

        server.send_message(message)


def send_confirmation_email(widget: dict, data: dict) -> bool:
    """
    Background-style safe side effect.

    Modes:
    - console: print email
    - smtp: send real email through SMTP
    - fail: force failure for capstone proof

    Retries a few times.
    If it still fails, logs an alert and does not break the submission.
    """
    attempts = 3

    for attempt in range(1, attempts + 1):
        try:
            if settings.email_mode == "fail":
                raise Exception("Email provider is down")

            if settings.email_mode == "console":
                print(
                    f"[EMAIL JOB] Console email sent for widget "
                    f"'{widget.get('title')}' to {data}"
                )
                return True

            if settings.email_mode != "smtp":
                print(
                    f"[EMAIL JOB] Unknown EMAIL_MODE '{settings.email_mode}'. "
                    "Falling back to console behavior."
                )
                print(
                    f"[EMAIL JOB] Console email sent for widget "
                    f"'{widget.get('title')}' to {data}"
                )
                return True

            visitor_email = None

            if isinstance(data.get("email"), str) and "@" in data.get("email"):
                visitor_email = data.get("email").strip()

            to_email = visitor_email or settings.notification_email

            subject = f"New submission for {widget.get('title', 'your widget')}"
            body = _build_email_body(widget, data)

            _send_smtp_email(to_email, subject, body)

            print(
                f"[EMAIL JOB] SMTP email sent to {to_email} "
                f"for widget '{widget.get('title')}'"
            )

            return True

        except Exception as error:
            print(f"[EMAIL JOB] attempt {attempt} failed: {error}")

    print("[ALERT] Email side effect failed after retries. Submission remains stored.")
    return False