import time

from app.config import get_settings

settings = get_settings()


def enrich_geo(ip_address: str) -> dict | None:
    """
    Fallback chain: Provider A -> Provider B -> None.
    Mocked to be deterministic for the capstone proof.
    """
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


def send_confirmation_email(widget: dict, data: dict) -> bool:
    """
    Background-style safe side effect.

    Retries a few times.
    If it still fails, logs an alert and does not break the submission.
    """
    attempts = 3

    for attempt in range(1, attempts + 1):
        try:
            if settings.email_mode == "fail":
                raise Exception("Email provider is down")

            print(
                f"[EMAIL JOB] Sent confirmation for widget "
                f"'{widget.get('title')}' to {data}"
            )
            return True

        except Exception as error:
            print(f"[EMAIL JOB] attempt {attempt} failed: {error}")
            time.sleep(0.2)

    print("[ALERT] Email side effect failed after retries. Submission remains stored.")
    return False