import json
import uuid

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
    show(
        "Health",
        httpx.get(f"{BASE_URL}/health", timeout=5),
    )

    show(
        "Valid submission",
        httpx.post(
            f"{BASE_URL}/public/submissions",
            json={
                "widget_public_id": "widget-a-123",
                "data": {
                    "email": "stage3@example.com"
                },
            },
            timeout=5,
        ),
    )

    show(
        "Missing required field",
        httpx.post(
            f"{BASE_URL}/public/submissions",
            json={
                "widget_public_id": "widget-a-123",
                "data": {},
            },
            timeout=5,
        ),
    )

    show(
        "Invalid email",
        httpx.post(
            f"{BASE_URL}/public/submissions",
            json={
                "widget_public_id": "widget-a-123",
                "data": {
                    "email": "not-an-email"
                },
            },
            timeout=5,
        ),
    )

    show(
        "Malformed JSON",
        httpx.post(
            f"{BASE_URL}/public/submissions",
            content=b'{"widget_public_id":',
            headers={"Content-Type": "application/json"},
            timeout=5,
        ),
    )

    big_payload = {
        "widget_public_id": "widget-a-123",
        "data": {
            "email": "big@example.com",
            "junk": "x" * 20000,
        },
    }

    big_bytes = json.dumps(big_payload).encode()

    show(
        "Oversized payload",
        httpx.post(
            f"{BASE_URL}/public/submissions",
            content=big_bytes,
            headers={"Content-Type": "application/json"},
            timeout=5,
        ),
    )

    idempotency_key = f"stage3-{uuid.uuid4().hex}"

    idempotent_payload = {
        "widget_public_id": "widget-a-123",
        "data": {
            "email": "idempotent@example.com"
        },
        "idempotency_key": idempotency_key,
    }

    show(
        "Idempotent first attempt",
        httpx.post(
            f"{BASE_URL}/public/submissions",
            json=idempotent_payload,
            timeout=5,
        ),
    )

    show(
        "Idempotent retry attempt",
        httpx.post(
            f"{BASE_URL}/public/submissions",
            json=idempotent_payload,
            timeout=5,
        ),
    )


if __name__ == "__main__":
    main()