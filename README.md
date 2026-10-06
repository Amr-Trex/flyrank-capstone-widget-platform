# FlyRank Capstone — Embeddable Widget & Lead-Capture Platform

A backend-focused platform where customers create embeddable lead-capture widgets, install them on any website with one `<script>` tag, and receive validated, abuse-protected, enriched submissions through a dashboard API.

The focus is on public-internet backend concerns: validation, CORS, caching, rate limiting, spam protection, fallback enrichment, safe side effects, tenant isolation, and analytics.

---

## Architecture

```text
Widget Owner
  -> Authenticated Widget API
  -> SQLite
  -> Embed snippet

Customer Website
  -> <script src="http://localhost:8000/public/widget.v1.js?id=widget-a-123">
  -> GET /public/widgets/{public_id}/config
  -> widget.js renders form

Visitor
  -> POST /public/submissions
  -> validation
  -> honeypot / rate limiting
  -> geo fallback enrichment
  -> store submission
  -> background email side effect

Owner
  -> Dashboard API
  -> submissions + stats
```

---

## Features

- Authenticated widget CRUD using `X-API-Key`
- Multi-tenant isolation for widgets and submissions
- Embed snippet generation per widget
- Public widget config endpoint with short cache headers
- Versioned widget JavaScript bundle with long cache headers
- Widget rendering on a second local origin
- Cross-origin submissions with CORS and preflight support
- Payload validation and oversized payload rejection
- Idempotent submission retries
- Rate limiting
- Honeypot spam protection
- Geo enrichment fallback chain
- Graceful degradation when all geo providers are down
- Background email side effect with retries and failure alert
- Dashboard API with submissions and stats

---

## Tech Stack

- Python 3.11+
- FastAPI
- SQLite
- Uvicorn
- Pydantic
- httpx
- python-dotenv
- Plain JavaScript widget loader
- Plain HTML test page

---

## Local Setup

Clone the repo:

```bash
git clone https://github.com/Amr-Trex/flyrank-capstone-widget-platform.git
cd flyrank-capstone-widget-platform
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy environment variables:

```bash
cp .env.example .env
```

Run migrations:

```bash
python scripts/migrate.py
```

Seed demo data:

```bash
python scripts/seed.py
```

Start the API:

```bash
python -m uvicorn app.main:app --reload
```

API docs:

```text
http://localhost:8000/docs
```

---

## Run the Second-Origin Test Page

In another terminal:

```bash
python -m http.server 5500 --directory test-page
```

Open:

```text
http://localhost:5500
```

The widget should render and submit cross-origin to the API.

---

## Demo Credentials

Local demo credentials only. Not real secrets.

Owner A:

```text
X-API-Key: demo-key-owner-a
```

Owner B:

```text
X-API-Key: demo-key-owner-b
```

Seeded widgets:

```text
widget-a-123
widget-b-123
```

---

## API Overview

### Owner API

Requires:

```text
X-API-Key: <owner-api-key>
```

Endpoints:

```text
POST   /widgets
GET    /widgets
GET    /widgets/{public_id}
PATCH  /widgets/{public_id}
DELETE /widgets/{public_id}
GET    /widgets/{public_id}/embed
GET    /dashboard/submissions
GET    /dashboard/stats
```

Example:

```bash
curl -H "X-API-Key: demo-key-owner-a" http://localhost:8000/widgets
```

---

### Public Delivery API

```text
GET /public/widgets/{public_id}/config
GET /public/widget.v1.js
```

Config cache header:

```text
Cache-Control: public, max-age=60
```

Widget JS cache header:

```text
Cache-Control: public, max-age=31536000, immutable
```

---

### Public Submission API

```text
POST /public/submissions
```

Valid payload:

```json
{
  "widget_public_id": "widget-a-123",
  "data": {
    "email": "person@example.com"
  }
}
```

Idempotent payload:

```json
{
  "widget_public_id": "widget-a-123",
  "data": {
    "email": "person@example.com"
  },
  "idempotency_key": "unique-key-123"
}
```

Example:

```bash
curl -X POST http://localhost:8000/public/submissions \
  -H "Content-Type: application/json" \
  -d "{\"widget_public_id\": \"widget-a-123\", \"data\": {\"email\": \"person@example.com\"}}"
```

Expected status:

```text
201 Created
```

---

## Validation and Abuse Protection

Public submissions go through:

1. body size check
2. JSON parsing
3. payload validation
4. widget lookup
5. honeypot spam check
6. rate limiting
7. field validation
8. idempotency check
9. storage
10. background email side effect

Expected status codes:

| Scenario | Status |
|---|---:|
| Valid submission created | 201 |
| Idempotent retry | 200 |
| Malformed JSON | 400 |
| Missing required field | 400 |
| Widget not found | 404 |
| Oversized payload | 413 |
| Rate limited | 429 |
| Missing or invalid API key | 401 |

---

## Geo Fallback and Safe Side Effects

Geo enrichment is mocked for deterministic proof.

Environment modes:

```env
GEO_MODE=mock
GEO_MODE=mock_a_down
GEO_MODE=mock_both_down
```

Behavior:

- `mock`: Provider A answers
- `mock_a_down`: Provider A fails, Provider B answers
- `mock_both_down`: both fail, submission still succeeds without geo data

Email side effect modes:

```env
EMAIL_MODE=console
EMAIL_MODE=fail
```

With `EMAIL_MODE=fail`, the submission still succeeds, is stored, and the server logs retries plus an alert.

---

## Real SMTP mode

The platform supports real SMTP email delivery.

Set:

```env
EMAIL_MODE=smtp
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_SECURITY=none
```

---

## Probe Scripts

Run the API first:

```bash
uvicorn app.main:app --reload
```

Then run:

```bash
python scripts/probe_stage2.py
python scripts/probe_stage3.py
python scripts/probe_stage4.py
python scripts/probe_stage5.py
python scripts/probe_final.py
```

View latest stored submissions:

```bash
python scripts/show_latest_submissions.py
```

---

## Environment Variables

See `.env.example`.

Key variables:

| Variable | Purpose |
|---|---|
| `DATABASE_PATH` | SQLite database file |
| `PUBLIC_BASE_URL` | Base URL used in embed snippet |
| `ALLOWED_ORIGINS` | CORS origins |
| `MAX_SUBMISSION_BYTES` | Max submission payload size |
| `GEO_MODE` | Mock geo fallback behavior |
| `EMAIL_MODE` | Console email or forced failure |
| `RATE_LIMIT_PER_MINUTE` | Public submission rate limit |

---

## Limitations

This is a local capstone implementation, not a production SaaS.

- SQLite instead of Postgres
- In-memory rate limiter, resets on restart
- Geo providers are mocked for deterministic proof
- Email is fake and logs to console
- Demo API keys are public for local evaluation
- No real CDN, hosting, domain, or SMTP provider
- Widget UI is minimal because the grade is in the backend