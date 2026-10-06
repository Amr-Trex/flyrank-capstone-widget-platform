import uuid

import httpx

BASE_URL = "http://localhost:8000"
SECOND_ORIGIN = "http://localhost:5500"

OWNER_A_HEADERS = {
    "X-API-Key": "demo-key-owner-a"
}

OWNER_B_HEADERS = {
    "X-API-Key": "demo-key-owner-b"
}


def show(name, response):
    print(f"=== {name} ===")
    print("Status:", response.status_code)

    if response.text:
        try:
            print(response.json())
        except Exception:
            print(response.text[:300])
    else:
        print("(empty response body)")

    print()


def main():
    show(
        "Health",
        httpx.get(f"{BASE_URL}/health", timeout=5),
    )

    email = f"final-{uuid.uuid4().hex[:6]}@example.com"

    show(
        "Valid cross-origin submission",
        httpx.post(
            f"{BASE_URL}/public/submissions",
            headers={"Origin": SECOND_ORIGIN},
            json={
                "widget_public_id": "widget-a-123",
                "data": {
                    "email": email,
                },
            },
            timeout=5,
        ),
    )

    show(
        "Owner A dashboard submissions",
        httpx.get(
            f"{BASE_URL}/dashboard/submissions?limit=5",
            headers=OWNER_A_HEADERS,
            timeout=5,
        ),
    )

    show(
        "Owner A dashboard stats",
        httpx.get(
            f"{BASE_URL}/dashboard/stats?days=7",
            headers=OWNER_A_HEADERS,
            timeout=5,
        ),
    )

    show(
        "Owner B dashboard submissions",
        httpx.get(
            f"{BASE_URL}/dashboard/submissions?limit=5",
            headers=OWNER_B_HEADERS,
            timeout=5,
        ),
    )

    show(
        "Owner B tries to filter by Owner A widget",
        httpx.get(
            f"{BASE_URL}/dashboard/submissions?widget_public_id=widget-a-123",
            headers=OWNER_B_HEADERS,
            timeout=5,
        ),
    )


if __name__ == "__main__":
    main()


