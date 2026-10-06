import time
import httpx

BASE_URL = "http://localhost:8000"

def show(name, response):
    print(f"=== {name} ===")
    print("Status:", response.status_code)
    try:
        print(response.json())
    except Exception:
        print(response.text[:300])
    print()

def main():
    # 1. honeypot Test (Bot fills hidden 'website' field)
    show("Honeypot Spam (Should return 200 but NOT save)", 
         httpx.post(f"{BASE_URL}/public/submissions", json={
             "widget_public_id": "widget-a-123",
             "data": {"email": "bot@spam.com", "website": "http://buy-pills.com"}
         }, timeout=5))

    # 2. rate limit test (send 6 requests fast, limit is 5)
    print("=== Rate Limit Test ===")
    for i in range(6):
        res = httpx.post(f"{BASE_URL}/public/submissions", json={
            "widget_public_id": "widget-a-123",
            "data": {"email": f"user{i}@test.com"}
        }, timeout=5)
        print(f"Request {i+1}: Status {res.status_code}")
    print()

    # wait for rate limit window to reset
    print("Waiting 30 seconds...")
    time.sleep(30)

    # 3. geo fallback test (requires changing .env to mock_a_down, then mock_both_down)
    # for now, we just test the normal mock which uses Provider A
    show("Normal geo enrichment (Provider A)",
         httpx.post(f"{BASE_URL}/public/submissions", json={
             "widget_public_id": "widget-a-123",
             "data": {"email": "geo@test.com"}
         }, timeout=5))

    # 4. safe side effect test (requires changing .env to EMAIL_MODE=fail)
    # we will test this manually in the terminal output.

if __name__ == "__main__":
    main()