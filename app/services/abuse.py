import time
from app.config import get_settings

settings = get_settings()

# in-memory stores for the capstone demo
# in a real app, we would use Redis.
request_counts = {}

def check_rate_limit(ip_address: str) -> bool:
    """Returns True if allowed, False if rate limited."""
    now = time.time()
    window = 30  # 30 seconds window
    
    # cleaning up old entries occasionally to prevent memory leaks
    if len(request_counts) > 1000:
        request_counts.clear()

    if ip_address not in request_counts:
        request_counts[ip_address] = []

    # remove requests older than 1 minute
    request_counts[ip_address] = [
        t for t in request_counts[ip_address] if now - t < window
    ]

    if len(request_counts[ip_address]) >= settings.rate_limit_per_minute:
        return False

    request_counts[ip_address].append(now)
    return True

def check_honeypot(data: dict) -> bool:
    """Returns True if spam (honeypot filled), False if clean."""
    # bots fill hidden fields named 'website' or 'url'. humans don't see them.
    return bool(data.get("website")) or bool(data.get("url"))


