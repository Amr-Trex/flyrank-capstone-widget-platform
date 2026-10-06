import uuid

import httpx

BASE_URL = "http://localhost:8000"
SECOND_ORIGIN = "http://localhost:5500"


def show(name, response, extra_headers=None):
    print(f"=== {name} ===")
    print("Status:", response.status_code)

    if extra_headers:
        for header in extra_headers:
            print(f"{header}: {response.headers.get(header)}")

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
        "Embed snippet for Owner A widget",
        httpx.get(
            f"{BASE_URL}/widgets/widget-a-123/embed",
            headers={"X-API-Key": "demo-key-owner-a"},
            timeout=5,
        ),
    )

    show(
        "Public config with cache header",
        httpx.get(
            f"{BASE_URL}/public/widgets/widget-a-123/config",
            headers={"Origin": SECOND_ORIGIN},
            timeout=5,
        ),
        extra_headers=[
            "cache-control",
            "access-control-allow-origin",
        ],
    )

    show(
        "Versioned widget JS",
        httpx.get(
            f"{BASE_URL}/public/widget.v1.js",
            headers={"Origin": SECOND_ORIGIN},
            timeout=5,
        ),
        extra_headers=[
            "cache-control",
            "content-type",
            "access-control-allow-origin",
        ],
    )

    show(
        "CORS preflight for submission",
        httpx.options(
            f"{BASE_URL}/public/submissions",
            headers={
                "Origin": SECOND_ORIGIN,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
            timeout=5,
        ),
        extra_headers=[
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers",
        ],
    )

    email = f"stage5-{uuid.uuid4().hex[:6]}@example.com"

    show(
        "Cross-origin valid submission",
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
        extra_headers=[
            "access-control-allow-origin",
        ],
    )


if __name__ == "__main__":
    main()

