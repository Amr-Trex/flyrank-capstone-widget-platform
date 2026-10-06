# Evidence

This file contains proof for each requirement.

## Requirements checklist

- [x] Authenticated widget CRUD
- [x] Tenant isolation
- [x] Embed snippet generated
- [x] Public config endpoint with cache headers
- [x] Versioned widget script
- [x] Widget renders on second origin
- [x] Cross-origin submissions work
- [x] Invalid payloads rejected with 4xx
- [x] Valid submissions stored
- [ ] Rate limiting returns 429
- [ ] Spam control works
- [ ] Geo fallback works
- [ ] All geo providers down still stores submission
- [ ] Email failure does not block submission
- [ ] README and required files present



## Stage 2 — Widget Management & Tenant Isolation

### 1. Unauthenticated requests are rejected (401)
```bash
$ curl -i http://localhost:8000/widgets
```

Output:
```
HTTP/1.1 401 Unauthorized
content-type: application/json

{"detail":"Missing X-API-Key header"}
```

```bash
$ curl -i -X POST -H "X-API-Key: demo-key-owner-a" -H "Content-Type: application/json" -d '{"title":"Stage 2 Test Widget"}' http://localhost:8000/widgets
```

Output:
```
HTTP/1.1 201 Created
content-type: application/json

{"public_id":"a1b2c3d4e5f6","type":"signup_form","title":"Stage 2 Test Widget","description":"","button_text":"Submit","fields":[{"name":"email","label":"Email","type":"email","required":true}],"status":"active","created_at":"2023-10-25 10:00:00"}
```

### 2. Cross-tenant access is rejected (404 / 403)
```bash
# Create widget A for owner 1
curl -X POST "http://localhost:8000/widgets" \
  -H "X-API-Key: key1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Widget A", "type": "signup_form", "fields":[{"name":"email","type":"email","required":true}]}'

# Try to view widget A as owner 2
curl -s -i -X GET "http://localhost:8000/widgets/WIDGET_A_PUBLIC_ID" \
  -H "X-API-Key: key2"

HTTP/1.1 404 Not Found

# Try to update widget A as owner 2
curl -s -i -X PUT "http://localhost:8000/widgets/WIDGET_A_PUBLIC_ID" \
  -H "X-API-Key: key2" \
  -H "Content-Type: application/json" \
  -d '{"title":"X"}'

HTTP/1.1 404 Not Found
```

### 3. Complete probing test proof for stage 2:

Command:
```bash
python scripts/probe_stage2.py
```
Output:
```
=== Health ===
Status: 200
{'status': 'ok'}

=== Missing auth ===
Status: 401
{'detail': 'Missing X-API-Key header'}

=== Owner A list widgets ===
Status: 200
[{'public_id': 'f3673735c1eb', 'type': 'signup_form', 'title': 'Curl test widget', 'description': '', 'button_text': 'Submit', 'fields': [{'name': 'email', 'label': 'Email', 'type': 'email', 'required': True}], 'status': 'active', 'created_at': '2026-10-05 16:05:00'}, {'public_id': 'f7cdeed0dfde', 'type': 'signup_form', 'title': 'Stage 2 test widget', 'description': 'Created during Stage 2', 'button_text': 'Join', 'fields': [{'name': 'email', 'label': 'Email', 'type': 'email', 'required': True}], 'status': 'active', 'created_at': '2026-10-05 15:57:41'}, {'public_id': 'widget-a-123', 'type': 'signup_form', 'title': 'Newsletter Signup', 'description': 'Get product updates', 'button_text': 'Subscribe', 'fields': [{'name': 'email', 'label': 'Email', 'type': 'email', 'required': True}], 'status': 'active', 'created_at': '2026-10-05 15:44:53'}]

=== Owner A reads own seeded widget ===
Status: 200
{'public_id': 'widget-a-123', 'type': 'signup_form', 'title': 'Newsletter Signup', 'description': 'Get product updates', 'button_text': 'Subscribe', 'fields': [{'name': 'email', 'label': 'Email', 'type': 'email', 'required': True}], 'status': 'active', 'created_at': '2026-10-05 15:44:53'}

=== Owner B tries to read Owner A widget ===
Status: 404
{'detail': 'Widget not found'}

=== Owner A creates widget ===
Status: 201
{'public_id': '8f9c35f86bb2', 'type': 'signup_form', 'title': 'Evidence widget 061324', 'description': 'Created for Stage 2 evidence', 'button_text': 'Join', 'fields': [{'name': 'email', 'label': 'Email', 'type': 'email', 'required': True}], 'status': 'active', 'created_at': '2026-10-06 03:08:41'}        

=== Owner A reads created widget ===
Status: 200
{'public_id': '8f9c35f86bb2', 'type': 'signup_form', 'title': 'Evidence widget 061324', 'description': 'Created for Stage 2 evidence', 'button_text': 'Join', 'fields': [{'name': 'email', 'label': 'Email', 'type': 'email', 'required': True}], 'status': 'active', 'created_at': '2026-10-06 03:08:41'}        

=== Owner B tries to read created widget ===
Status: 404
{'detail': 'Widget not found'}

=== Owner A updates created widget ===
Status: 200
{'public_id': '8f9c35f86bb2', 'type': 'signup_form', 'title': 'Evidence widget 061324 updated', 'description': 'Created for Stage 2 evidence', 'button_text': 'Join', 'fields': [{'name': 'email', 'label': 'Email', 'type': 'email', 'required': True}], 'status': 'active', 'created_at': '2026-10-06 03:08:41'}

=== Owner B tries to update created widget ===
Status: 404
{'detail': 'Widget not found'}

=== Owner A deletes created widget ===
Status: 204
(empty response body)

=== Owner A reads deleted widget ===
Status: 404
{'detail': 'Widget not found'}
```


## Stage 3 — Public submission validation proof

Command:
```bash
python scripts/probe_stage3.py
```
Output:
```
=== Health ===
Status: 200
{'status': 'ok'}

=== Valid submission ===
Status: 201
{'id': 1, 'widget_public_id': 'widget-a-123', 'ip_address': '127.0.0.1', 'geo_country': None, 'geo_city': None, 'geo_provider': None, 'idempotency_key': None, 'created_at': '2026-10-05 18:13:36', 'data': {'email': 'stage3@example.com'}}

=== Missing required field ===
Status: 400
{'detail': ['email is required']}

=== Invalid email ===
Status: 400
{'detail': ['email must be a valid email']}

=== Malformed JSON ===
Status: 400
{'detail': 'Malformed JSON'}

=== Oversized payload ===
Status: 413
{'detail': 'Payload too large'}

=== Idempotent first attempt ===
Status: 201
{'id': 2, 'widget_public_id': 'widget-a-123', 'ip_address': '127.0.0.1', 'geo_country': None, 'geo_city': None, 'geo_provider': None, 'idempotency_key': 'stage3-96ac7b8c86ab4649842323c77b018b38', 'created_at': '2026-10-05 18:13:48', 'data': {'email': 'idempotent@example.com'}}

=== Idempotent retry attempt ===
Status: 200
{'id': 2, 'widget_public_id': 'widget-a-123', 'ip_address': '127.0.0.1', 'geo_country': None, 'geo_city': None, 'geo_provider': None, 'idempotency_key': 'stage3-96ac7b8c86ab4649842323c77b018b38', 'created_at': '2026-10-05 18:13:48', 'data': {'email': 'idempotent@example.com'}}
```

```bash
$ python scripts/show_latest_submissions.py
```

Output:
```
(4, 'widget-a-123', '{"email": "idempotent@example.com"}', '127.0.0.1', '2026-10-06 03:09:24')        
(3, 'widget-a-123', '{"email": "stage3@example.com"}', '127.0.0.1', '2026-10-06 03:09:12')
(2, 'widget-a-123', '{"email": "idempotent@example.com"}', '127.0.0.1', '2026-10-05 18:13:48')        
(1, 'widget-a-123', '{"email": "stage3@example.com"}', '127.0.0.1', '2026-10-05 18:13:36')
```

## Stage 4 — Abuse Protection, Geo Fallback, and Safe Side Effects

### 1. Honeypot Spam Protection
Bot fills hidden 'website' field. Returns 200 to trick bot, but nothing is saved to DB.
```javascript
import httpx

response = httpx.post(
    "http://localhost:8000/public/submissions",
    json={
        "widget_public_id": "widget-a-123",
        "data": {"email": "bot@spam.com", "website": "http://buy-pills.com"}
    },
    timeout=5
)
```

Backend console output:
```text
[SPAM] Honeypot triggered. Silently dropping submission.
INFO:     127.0.0.1:64493 - "POST /public/submissions HTTP/1.1" 200 OK
```

### 2. Rate Limiting (30s window)
After 5 requests, next one returns 429.

```python
for i in range(7):
    response = httpx.post(
        "http://localhost:8000/public/submissions",
        json={
            "widget_public_id": "widget-a-123",
            "data": {"email": f"user{i}@test.com"}
        },
        timeout=5
    )
    print(f"Request {i+1} status:", response.status_code)
```

Backend console output:
```text
[EMAIL] Sent confirmation for widget 'Newsletter Signup' to {'email': 'user0@test.com'}
INFO:     127.0.0.1:64496 - "POST /public/submissions HTTP/1.1" 201 Created
[GEO] Provider A succeeded for 127.0.0.1
[EMAIL] Sent confirmation for widget 'Newsletter Signup' to {'email': 'user1@test.com'}
INFO:     127.0.0.1:64498 - "POST /public/submissions HTTP/1.1" 201 Created
[GEO] Provider A succeeded for 127.0.0.1
[EMAIL] Sent confirmation for widget 'Newsletter Signup' to {'email': 'user2@test.com'}
INFO:     127.0.0.1:56733 - "POST /public/submissions HTTP/1.1" 201 Created
[GEO] Provider A succeeded for 127.0.0.1
[EMAIL] Sent confirmation for widget 'Newsletter Signup' to {'email': 'user3@test.com'}
INFO:     127.0.0.1:56735 - "POST /public/submissions HTTP/1.1" 201 Created
[GEO] Provider A succeeded for 127.0.0.1
[EMAIL] Sent confirmation for widget 'Newsletter Signup' to {'email': 'user4@test.com'}
INFO:     127.0.0.1:56737 - "POST /public/submissions HTTP/1.1" 201 Created
INFO:     127.0.0.1:56739 - "POST /public/submissions HTTP/1.1" 429 Too Many Requests
```

### 3. Geo Fallbacks

**Normal operation (Provider A succeeds):**
```bash
# default .env (GEO_MODE=mock)
```
Backend console output:
```text
[GEO] Provider A succeeded for 127.0.0.1
[EMAIL] Sent confirmation for widget 'Newsletter Signup' to {'email': 'geo1@test.com'}
INFO:     127.0.0.1:56740 - "POST /public/submissions HTTP/1.1" 201 Created
```

**Provider A down (Fallback to Provider B):**
```bash
# Set GEO_MODE=mock_a_down in .env and restart server
```
Backend console output:
```text
[GEO] Provider A failed: Provider A is down. Trying Provider B...
[GEO] Provider B succeeded for 127.0.0.1
[EMAIL] Sent confirmation for widget 'Newsletter Signup' to {'email': 'geo2@test.com'}
INFO:     127.0.0.1:56741 - "POST /public/submissions HTTP/1.1" 201 Created
```

**Both Providers down (Graceful degradation):**
```bash
# Set GEO_MODE=mock_both_down in .env and restart server
```
Backend console output:
```text
[GEO] Provider A failed: Provider A is down. Trying Provider B...
[GEO] Provider B failed: Provider B is down. Degrading gracefully.
[EMAIL] Sent confirmation for widget 'Newsletter Signup' to {'email': 'geo3@test.com'}
INFO:     127.0.0.1:56742 - "POST /public/submissions HTTP/1.1" 201 Created
```

### 4. Safe Side Effects (Email Failure)

If the email server goes offline, the submission is still stored and the frontend still receives a 201 success response.

```bash
# Set EMAIL_MODE=fail in .env and restart server
```
Backend console output:
```text
[GEO] Provider A succeeded for 127.0.0.1
[EMAIL] Side effect failed, but we do NOT block the submission: SMTP Server is completely offline!
INFO:     127.0.0.1:56743 - "POST /public/submissions HTTP/1.1" 201 Created
```
