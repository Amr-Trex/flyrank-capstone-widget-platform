import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from app import submissions_repository as sub_repo
from app.config import get_settings
from app.services import clean_and_validate_submission_data

router = APIRouter(prefix="/public", tags=["public"])

settings = get_settings()


class SubmissionPayload(BaseModel):
    widget_public_id: str = Field(min_length=1, max_length=64)
    data: dict
    idempotency_key: Optional[str] = Field(default=None, max_length=100)


@router.post("/submissions", status_code=201)
async def create_submission(request: Request):
    body = await request.body()

    if len(body) > settings.max_submission_bytes:
        raise HTTPException(status_code=413, detail="Payload too large")

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Malformed JSON")

    try:
        payload = SubmissionPayload(**parsed)
    except ValidationError as validation_error:
        errors = []

        for error in validation_error.errors():
            errors.append(
                {
                    "field": ".".join(str(part) for part in error.get("loc", [])),
                    "message": error.get("msg"),
                }
            )

        raise HTTPException(status_code=400, detail=errors)

    widget = sub_repo.get_active_widget_internal(payload.widget_public_id)

    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")

    idempotency_key = None

    if payload.idempotency_key:
        idempotency_key = payload.idempotency_key.strip()

    if idempotency_key:
        existing = sub_repo.find_submission_by_idempotency(
            payload.widget_public_id,
            idempotency_key,
        )

        if existing:
            return JSONResponse(status_code=200, content=existing)

    cleaned_data, errors = clean_and_validate_submission_data(widget, payload.data)

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    ip_address = request.client.host if request.client else "unknown"

    submission, created = sub_repo.create_submission(
        widget=widget,
        data=cleaned_data,
        ip_address=ip_address,
        geo=None,
        idempotency_key=idempotency_key,
    )

    if not created:
        return JSONResponse(status_code=200, content=submission)

    return submission