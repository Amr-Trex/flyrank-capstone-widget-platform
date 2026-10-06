import random
import time
from app.config import get_settings

settings = get_settings()

def enrich_geo(ip_address: str) -> dict | None:
    """
    Fallback chain: Provider A -> Provider B -> None.
    Mocked to be deterministic for the capstone proof.
    """
    
    # mock provider A
    try:
        if settings.geo_mode == "mock_a_down":
            raise ConnectionError("Provider A is down")
        print(f"[GEO] Provider A succeeded for {ip_address}")
        return {"country": "US", "city": "New York", "provider": "A"}
    except Exception as e:
        print(f"[GEO] Provider A failed: {e}. Trying Provider B...")

    # mock provider B (Fallback)
    try:
        if settings.geo_mode == "mock_both_down":
            raise ConnectionError("Provider B is down")
        print(f"[GEO] Provider B succeeded for {ip_address}")
        return {"country": "UK", "city": "London", "provider": "B"}
    except Exception as e:
        print(f"[GEO] Provider B failed: {e}. Degrading gracefully.")

    # degrade gracefully
    return None

def send_confirmation_email(widget: dict, data: dict) -> bool:
    """
    Safe side effect. If it fails, we just log it and move on.
    """
    try:
        if settings.email_mode == "fail":
            raise Exception("SMTP Server is completely offline!")
            
        print(f"[EMAIL] Sent confirmation for widget '{widget['title']}' to {data}")
        return True
    except Exception as e:
        print(f"[EMAIL] Side effect failed, but we do NOT block the submission: {e}")
        return False