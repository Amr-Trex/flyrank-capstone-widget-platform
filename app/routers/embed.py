# endpoint used to generate the embed snippet

from fastapi import APIRouter, Depends, HTTPException

from app.repositories import widgets as repo
from app.auth import get_current_owner
from app.config import get_settings

router = APIRouter(prefix="/widgets", tags=["widgets"])

settings = get_settings()


@router.get("/{public_id}/embed")
def get_embed_snippet(public_id: str, owner=Depends(get_current_owner)):
    widget = repo.get_widget_by_public_id(owner["id"], public_id)

    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")

    snippet = (
        f'<script src="{settings.public_base_url}/public/widget.v1.js'
        f'?id={public_id}"></script>'
    )

    return {
        "public_id": public_id,
        "embed_snippet": snippet,
    }


