# Build Log

## AI usage

- Used AI to help plan the capstone and structure the repository.
- Will use AI for debugging and implementation help where needed.
- I review and understand any code I add or generate before committing.

## Notes

- Starting with SQLite for simplicity.
- Targeting core requirements first, stretch goals later only if time permits.

## Stage 2 — Widget management API

### Where AI helped

- AI helped scaffold the FastAPI app, SQLite migration, auth, and widget CRUD. I reviewed the files, edited whatever was important based on my judgement, and tested the endpoints manually.
- AI helped structure the repository layer so widget queries filter by `owner_id`.

### What I checked

- I verified that requests without an API key return `401`.
- I verified that Owner A can create, read, update, and delete widgets.
- I verified that Owner B cannot read or modify Owner A's widgets.
- I verified that tenant isolation is enforced in database queries, not only in the UI.

### What I changed

- I made sure widget responses do not expose internal database IDs unnecessarily.
- I kept the repository layer separate from the HTTP layer so the database logic is not mixed into route handlers.
- I used fixed local demo API keys only for evaluation, not real secrets.

### Cost tracking

- The running application does not call any paid AI service.
- AI was used only as a development assistant, so there is no runtime AI cost to track for this stage.

---

## Stage 3 — Public submission endpoint

### Where AI helped

- AI helped design the public submission flow: raw body size check, JSON parsing, payload validation, field validation, then database storage.
- AI helped structure the idempotency check so a retried submission does not create a duplicate row.

### Where AI needed correction

- The first AI-style approach wanted to parse JSON immediately. I changed the order so the raw body size is checked before JSON parsing.
- The first validation error output was too detailed and could include awkward Pydantic internals, so I simplified the error response to clean JSON messages.
- I made sure empty idempotency keys are treated as no idempotency key instead of storing empty strings.

### What I checked

- Valid submissions return `201` and are stored.
- Missing required fields return `400`.
- Invalid email values return `400`.
- Malformed JSON returns `400`.
- Oversized payloads return `413`.
- Retrying with the same idempotency key returns the original submission instead of creating a duplicate.

### Cost tracking

- No AI calls are made during public submission handling.
- Therefore no per-request AI cost tracking is needed for this stage.


