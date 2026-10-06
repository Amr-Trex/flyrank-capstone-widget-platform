import json
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from app import submissions_repository as sub_repo
from app.abuse import check_honeypot, check_rate_limit
from app.config import get_settings
from app.enrichment import enrich_geo, send_confirmation_email
from app.services import clean_and_validate_submission_data

router = APIRouter(prefix="/public", tags=["public"])
settings = get_settings()

class SubmissionPayload(BaseModel):
    widget_public_id: str = Field(min_length=1, max_length=64)
    data: dict
    idempotency_key: Optional[str] = Field(default=None, max_length=100)

@router.post("/submissions", status_code=201)
async def create_submission(request: Request, background_tasks: BackgroundTasks):
    # 1. Check raw body size
    body = await request.body()
    if len(body) > settings.max_submission_bytes:
        raise HTTPException(status_code=413, detail="Payload too large")

    # 2. Parse JSON
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Malformed JSON")

    # 3. Validate Payload Shape
    try:
        payload = SubmissionPayload(**parsed)
    except ValidationError as validation_error:
        errors = [{"field": ".".join(str(p) for p in e.get("loc", [])), "message": e.get("msg")} for e in validation_error.errors()]
        raise HTTPException(status_code=400, detail=errors)

    # 4. Find Widget
    widget = sub_repo.get_active_widget_internal(payload.widget_public_id)
    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")

    # 5. Honeypot Spam Check (Silent Rejection)
    if check_honeypot(payload.data):
        print("[SPAM] Honeypot triggered. Silently dropping submission.")
        # Return 200 to trick the bot, but do NOT save to DB
        return JSONResponse(status_code=200, content={"message": "Success"})

    # 6. Rate Limiting
    ip_address = request.client.host if request.client else "unknown"
    if not check_rate_limit(ip_address):
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    # 7. Idempotency Check
    idempotency_key = payload.idempotency_key.strip() if payload.idempotency_key else None
    if idempotency_key:
        existing = sub_repo.find_submission_by_idempotency(payload.widget_public_id, idempotency_key)
        if existing:
            return JSONResponse(status_code=200, content=existing)

    # 8. Field Validation
    cleaned_data, errors = clean_and_validate_submission_data(widget, payload.data)
    if errors:
        raise HTTPException(status_code=400, detail=errors)

    # 9. Geo Enrichment (Safe Fallback)
    geo_data = enrich_geo(ip_address)

    # 10. Store Submission
    submission, created = sub_repo.create_submission(
        widget=widget,
        data=cleaned_data,
        ip_address=ip_address,
        geo=geo_data,
        idempotency_key=idempotency_key,
    )

    if not created:
        return JSONResponse(status_code=200, content=submission)

    # 11. Safe Side Effect (Email) - Runs AFTER storage, failure is ignored
    background_tasks.add_task(send_confirmation_email, widget, cleaned_data)

    return submission