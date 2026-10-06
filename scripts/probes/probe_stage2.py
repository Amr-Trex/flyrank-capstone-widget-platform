import uuid

import httpx

BASE_URL = "http://localhost:8000"

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

    show(
        "Missing auth",
        httpx.get(f"{BASE_URL}/widgets", timeout=5),
    )

    show(
        "Owner A list widgets",
        httpx.get(
            f"{BASE_URL}/widgets",
            headers=OWNER_A_HEADERS,
            timeout=5,
        ),
    )

    show(
        "Owner A reads own seeded widget",
        httpx.get(
            f"{BASE_URL}/widgets/widget-a-123",
            headers=OWNER_A_HEADERS,
            timeout=5,
        ),
    )

    show(
        "Owner B tries to read Owner A widget",
        httpx.get(
            f"{BASE_URL}/widgets/widget-a-123",
            headers=OWNER_B_HEADERS,
            timeout=5,
        ),
    )

    title = f"Evidence widget {uuid.uuid4().hex[:6]}"

    create_response = httpx.post(
        f"{BASE_URL}/widgets",
        headers=OWNER_A_HEADERS,
        json={
            "title": title,
            "description": "Created for Stage 2 evidence",
            "button_text": "Join",
        },
        timeout=5,
    )

    show("Owner A creates widget", create_response)

    try:
        public_id = create_response.json().get("public_id")
    except Exception:
        public_id = None

    if not public_id:
        print("Could not continue because widget creation failed.")
        return

    show(
        "Owner A reads created widget",
        httpx.get(
            f"{BASE_URL}/widgets/{public_id}",
            headers=OWNER_A_HEADERS,
            timeout=5,
        ),
    )

    show(
        "Owner B tries to read created widget",
        httpx.get(
            f"{BASE_URL}/widgets/{public_id}",
            headers=OWNER_B_HEADERS,
            timeout=5,
        ),
    )

    show(
        "Owner A updates created widget",
        httpx.patch(
            f"{BASE_URL}/widgets/{public_id}",
            headers=OWNER_A_HEADERS,
            json={
                "title": f"{title} updated",
            },
            timeout=5,
        ),
    )

    show(
        "Owner B tries to update created widget",
        httpx.patch(
            f"{BASE_URL}/widgets/{public_id}",
            headers=OWNER_B_HEADERS,
            json={
                "title": "This should not work",
            },
            timeout=5,
        ),
    )

    show(
        "Owner A deletes created widget",
        httpx.delete(
            f"{BASE_URL}/widgets/{public_id}",
            headers=OWNER_A_HEADERS,
            timeout=5,
        ),
    )

    show(
        "Owner A reads deleted widget",
        httpx.get(
            f"{BASE_URL}/widgets/{public_id}",
            headers=OWNER_A_HEADERS,
            timeout=5,
        ),
    )


if __name__ == "__main__":
    main()