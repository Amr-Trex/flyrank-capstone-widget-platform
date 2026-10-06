from fastapi import APIRouter, Depends, Query

from app.repositories import dashboard as dash_repo
from app.auth import get_current_owner

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/submissions")
def list_submissions(
    widget_public_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    owner=Depends(get_current_owner),
):
    return dash_repo.list_owner_submissions(
        owner_id=owner["id"],
        widget_public_id=widget_public_id,
        limit=limit,
    )


@router.get("/stats")
def stats(
    days: int = Query(default=7, ge=1, le=90),
    owner=Depends(get_current_owner),
):
    return dash_repo.get_owner_stats(
        owner_id=owner["id"],
        days=days,
    )