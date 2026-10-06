# FlyRank Capstone — Embeddable Widget & Lead-Capture Platform

A backend-focused platform that lets customers create embeddable lead-capture widgets and install them on any website using one `<script>` tag.

When a visitor submits the widget, the submission is sent to a hardened public API where it is validated, abuse-protected, enriched with geo data, stored safely, and made visible to the widget owner through a dashboard API.

The project focuses on real public-internet backend concerns:

- CORS
- caching
- validation
- rate limiting
- spam protection
- fallback enrichment
- safe side effects
- tenant isolation
- idempotency
- dashboard analytics

---

## Architecture

```text
Widget Owner
  -> Authenticated Widget Management API
  -> SQLite database
  -> Embed snippet

Customer Website
  -> <script src="http://localhost:8000/public/widget.v1.js?id=widget-a-123">
  -> GET /public/widgets/{public_id}/config
  -> widget.js renders form

Website Visitor
  -> POST /public/submissions
  -> validation
  -> honeypot / rate limiting
  -> geo fallback enrichment
  -> store submission
  -> background email side effect

Widget Owner
  -> Authenticated Dashboard API
  -> submissions + stats
```

The system has three request paths:

1. **Owner path** — authenticated widget CRUD and dashboard access.
2. **Delivery path** — public widget JavaScript and widget config.
3. **Submission path** — hardened public endpoint for untrusted browser traffic.

---

## Core features

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
- Optional real SMTP support using Mailpit
- Dockerized local stack
- Dashboard API with submissions and stats

---

## Quickstart with Docker

Run:

```bash
docker compose up --build
```

This starts:

- FastAPI API
- Mailpit local SMTP server
- second-origin test page
- automatic migrations
- automatic demo seeding

The API entrypoint automatically runs:

```bash
python scripts/migrate.py
python scripts/seed.py
```

before starting the server.

### URLs

```text
API:            http://localhost:8000
API docs:       http://localhost:8000/docs
Health check:   http://localhost:8000/health
Mailpit inbox:  http://localhost:8025
Test page:      http://localhost:5500
```

Open:

```text
http://localhost:5500
```

The widget should render on a page served from a different origin than the API.

---

## Local Python setup without Docker

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

Run migrations and seed:

```bash
python scripts/migrate.py
python scripts/seed.py
```

Start the API:

```bash
python -m uvicorn app.main:app --reload
```

Start the second-origin test page in another terminal:

```bash
python -m http.server 5500 --directory test-page
```

Open:

```text
http://localhost:5500
```

---

## Demo credentials

These are local demo credentials only. They are intentionally public for evaluation.

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

Owner A owns `widget-a-123`.

Owner B owns `widget-b-123`.

---

## Embed snippet

Owners can request the embed snippet for a widget:

```bash
curl -H "X-API-Key: demo-key-owner-a" \
  http://localhost:8000/widgets/widget-a-123/embed
```

Example response:

```json
{
  "public_id": "widget-a-123",
  "embed_snippet": "<script src=\"http://localhost:8000/public/widget.v1.js?id=widget-a-123\"></script>"
}
```

The customer pastes this one line into their website.

---

## API overview

### Health

```text
GET /health
```

Example:

```bash
curl http://localhost:8000/health
```

---

## Owner API

Owner endpoints require:

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

Tenant isolation is enforced in database queries. Owner A cannot read or modify Owner B data.

---

## Public delivery API

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

The JavaScript bundle is versioned. If the script changes, a new URL such as `/public/widget.v2.js` should be used.

---

## Public submission API

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

Example:

```bash
curl -i -X POST http://localhost:8000/public/submissions \
  -H "Content-Type: application/json" \
  -d "{\"widget_public_id\": \"widget-a-123\", \"data\": {\"email\": \"person@example.com\"}}"
```

Expected status:

```text
201 Created
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

If a request is retried with the same idempotency key, the original submission is returned instead of creating a duplicate.

---

## Dashboard API

List submissions:

```bash
curl -H "X-API-Key: demo-key-owner-a" \
  "http://localhost:8000/dashboard/submissions?limit=5"
```

Filter by widget:

```bash
curl -H "X-API-Key: demo-key-owner-a" \
  "http://localhost:8000/dashboard/submissions?widget_public_id=widget-a-123"
```

Stats:

```bash
curl -H "X-API-Key: demo-key-owner-a" \
  "http://localhost:8000/dashboard/stats?days=7"
```

Stats include:

- total submissions
- per-widget counts
- per-day counts
- geo breakdown

---

## Validation and status codes

Public submissions go through:

1. body size check
2. JSON parsing
3. payload validation
4. widget lookup
5. honeypot spam check
6. rate limiting
7. field validation
8. idempotency check
9. geo enrichment fallback
10. database storage
11. background email side effect

Expected status codes:

| Scenario | Status |
|---|---:|
| Valid submission created | 201 |
| Idempotent retry | 200 |
| Malformed JSON | 400 |
| Invalid payload shape | 400 |
| Missing required field | 400 |
| Invalid email | 400 |
| Widget not found | 404 |
| Oversized payload | 413 |
| Rate limited | 429 |
| Missing or invalid API key | 401 |

Invalid input returns clean `4xx` JSON errors, not `500` crashes.

---

## CORS and second-origin behavior

The API allows requests from:

```text
http://localhost:5500
http://127.0.0.1:5500
```

The submission endpoint supports:

- cross-origin POST requests
- preflight `OPTIONS` requests
- JSON request bodies
- CORS headers

Example preflight check:

```bash
curl -i -X OPTIONS http://localhost:8000/public/submissions \
  -H "Origin: http://localhost:5500" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

Expected status:

```text
200 OK
```

---

## Rate limiting

The public submission endpoint is rate limited by IP address.

Default:

```env
RATE_LIMIT_PER_MINUTE=5
```

If too many requests arrive in a short window, the API returns:

```text
429 Too Many Requests
```

The API remains running.

The rate limiter is in-memory and resets on restart. This is intentional for the local capstone implementation.

With Docker:

```bash
docker compose restart api
```

Without Docker, restart Uvicorn.

---

## Spam protection

The widget renders a hidden honeypot field named:

```text
website
```

Normal users do not see it.

Bots often fill every field. If the honeypot is filled, the API silently drops the submission.

Example spam payload:

```json
{
  "widget_public_id": "widget-a-123",
  "data": {
    "email": "bot@example.com",
    "website": "http://spam.example"
  }
}
```

The API returns success to avoid revealing spam detection, but the submission is not stored.

---

## Geo enrichment fallback chain

The platform enriches submissions with geo data using:

```text
Provider A
  -> if Provider A fails, try Provider B
    -> if Provider B fails, store submission without geo data
```

For deterministic proof, geo providers are mocked using environment modes.

Available modes:

```env
GEO_MODE=mock
GEO_MODE=mock_a_down
GEO_MODE=mock_both_down
```

Behavior:

- `mock`: Provider A answers
- `mock_a_down`: Provider A fails, Provider B answers
- `mock_both_down`: both fail, submission still succeeds without geo data

This demonstrates graceful degradation.

---

## Email side effect

After a submission is stored, the platform triggers a confirmation email side effect.

This side effect:

- runs as a background task
- retries multiple times
- logs an alert if it ultimately fails
- never blocks or breaks the main submission response

Supported modes:

```env
EMAIL_MODE=console
EMAIL_MODE=smtp
EMAIL_MODE=fail
```

### Console mode

```env
EMAIL_MODE=console
```

The email is logged to the console.

No SMTP server is required.

This is the simplest mode and is fully enough for the capstone.

---

## Real SMTP mode

```env
EMAIL_MODE=smtp
```

The platform uses Python's built-in `smtplib` to send real email through an SMTP server.

Important:

`smtplib` is an SMTP client. It needs an SMTP server to send to.

The Docker setup uses Mailpit as the local SMTP server.

Mailpit SMTP port:

```text
1025
```

Mailpit inbox:

```text
http://localhost:8025
```

Inside Docker, the API container uses:

```env
SMTP_HOST=mailpit
SMTP_PORT=1025
```

because `mailpit` is the Docker service name.

For local Python without Docker, use:

```env
SMTP_HOST=localhost
SMTP_PORT=1025
```

External SMTP example:

```env
EMAIL_MODE=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_SECURITY=ssl
EMAIL_FROM=your-email@gmail.com
NOTIFICATION_EMAIL=your-email@gmail.com
```

Never commit real SMTP credentials.

Keep them only in `.env`, which is git-ignored.

---

## Forcing email failure

To prove that a failing email side effect does not break submissions:

```env
EMAIL_MODE=fail
```

Then submit a valid payload.

Expected:

- HTTP response is still successful
- submission is still stored
- logs show retries
- logs show a final alert

Example logs:

```text
[EMAIL JOB] attempt 1 failed: Email provider is down
[EMAIL JOB] attempt 2 failed: Email provider is down
[EMAIL JOB] attempt 3 failed: Email provider is down
[ALERT] Email side effect failed after retries. Submission remains stored.
```

---

## Database and migrations

The project uses SQLite for simplicity.

The schema is applied through:

```text
migrations/001_init.sql
```

The migration runner is:

```text
scripts/migrate.py
```

Tables:

```text
owners
widgets
submissions
schema_migrations
```

Important indexes exist for:

- widget ownership
- widget public ID
- submission widget ID
- submission owner ID
- submission creation time
- idempotency keys

Tenant isolation is enforced by filtering every owner query by `owner_id`.

---

## Probe scripts

The repository includes scripts that demonstrate the capstone behavior.

Make sure the app is running first.

With Docker:

```bash
docker compose up --build
```

Without Docker:

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

View latest submissions:

```bash
python scripts/show_latest_submissions.py
```

Test email behavior:

```bash
python scripts/test_smtp_email.py
```

---

## Acceptance probe mapping

### Probe 1 — Valid submission from second-origin page

Open:

```text
http://localhost:5500
```

Submit the widget form.

Then verify the submission appears in the dashboard API:

```bash
curl -H "X-API-Key: demo-key-owner-a" \
  "http://localhost:8000/dashboard/submissions?limit=5"
```

Or run:

```bash
python scripts/probe_final.py
```

---

### Probe 2 — Malformed and oversized payloads

Run:

```bash
python scripts/probe_stage3.py
```

Expected:

- malformed JSON returns `400`
- oversized payload returns `413`
- no `500` errors

---

### Probe 3 — Burst rate limiting

Run:

```bash
python scripts/probe_stage4.py
```

Expected:

- rapid submissions eventually return `429`
- the API remains running

The local rate limiter is in-memory and resets when the API restarts.

---

### Probe 4 — Geo fallback chain

Set:

```env
GEO_MODE=mock_a_down
```

Restart the API and submit a valid payload.

Expected:

```text
Provider A fails.
Provider B answers.
```

Then set:

```env
GEO_MODE=mock_both_down
```

Restart the API and submit again.

Expected:

```text
Provider A fails.
Provider B fails.
Submission still succeeds without geo data.
```

---

### Probe 5 — Failing email side effect

Set:

```env
EMAIL_MODE=fail
```

Restart the API and submit a valid payload.

Expected:

- submission still succeeds
- submission is stored
- logs show retries and alert

---

### Probe 6 — Honeypot spam control

Send a payload with the hidden honeypot field filled:

```bash
curl -i -X POST http://localhost:8000/public/submissions \
  -H "Content-Type: application/json" \
  -d "{\"widget_public_id\": \"widget-a-123\", \"data\": {\"email\": \"bot@example.com\", \"website\": \"http://spam.example\"}}"
```

Expected:

- API returns success to avoid revealing spam detection
- submission is not stored

---

## Environment variables

The app reads configuration from `.env`.

A committed `.env.example` file is included.

Key variables:

| Variable | Purpose |
|---|---|
| `DATABASE_PATH` | SQLite database file |
| `PUBLIC_BASE_URL` | Base URL used in embed snippet |
| `ALLOWED_ORIGINS` | CORS origins |
| `MAX_SUBMISSION_BYTES` | Max submission payload size |
| `GEO_MODE` | Mock geo fallback behavior |
| `EMAIL_MODE` | Console, SMTP, or forced failure |
| `SMTP_HOST` | SMTP server host |
| `SMTP_PORT` | SMTP server port |
| `SMTP_SECURITY` | `none`, `starttls`, or `ssl` |
| `RATE_LIMIT_PER_MINUTE` | Public submission rate limit |

---

## Docker notes

The Docker stack runs:

1. API on port 8000
2. Mailpit SMTP server on port 1025
3. Mailpit inbox UI on port 8025
4. second-origin test page on port 5500

Start:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

Stop and delete the SQLite volume:

```bash
docker compose down -v
```

Use `-v` when you want to reset the database.

---

## Troubleshooting

### Widget does not render

Check:

1. API is running on `http://localhost:8000`
2. test page is running on `http://localhost:5500`
3. demo data is seeded
4. browser console does not show CORS errors

---

### CORS error

Make sure the test page is opened from:

```text
http://localhost:5500
```

not from a `file://` URL.

Also check:

```env
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

Then restart the API.

---

### 429 Too Many Requests

The rate limiter is in-memory.

Restart the API to reset it.

With Docker:

```bash
docker compose restart api
```

---

### Mailpit email does not appear

Make sure:

```env
EMAIL_MODE=smtp
```

With Docker, the API should use:

```env
SMTP_HOST=mailpit
SMTP_PORT=1025
```

Then open:

```text
http://localhost:8025
```

---

## Required submission files

This repository includes:

```text
README.md
capstone.yaml
EVIDENCE.md
BUILDLOG.md
.env.example
```

---

## Limitations

This is a local capstone implementation, not a production SaaS.

- SQLite is used for simplicity instead of Postgres.
- Rate limiting is in-memory and resets on restart.
- Geo enrichment is mocked for deterministic proof.
- Email can run in console mode, real SMTP mode, or forced-failure mode.
- Demo API keys are intentionally public for local evaluation.
- No real CDN, domain, or hosting is used.
- The widget UI is minimal because the grade is in the backend.
- The second-origin customer page is a plain local HTML page.
- External SMTP credentials, if used, must remain only in `.env`.

---

## License

This project is provided as a portfolio capstone.

MIT is a good default license for public portfolio work.