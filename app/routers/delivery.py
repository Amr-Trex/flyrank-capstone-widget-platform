# this script handles the "delivery" side of the widget platform
# it is used to serve the widget script and its configuration
# it is also used to serve the submission endpoint

# this router is responsible for serving the files 
# and data that actually make the widget appear on a customer's website

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from app import submissions_repository as sub_repo
from app.config import get_settings

router = APIRouter(prefix="/public", tags=["public"])

settings = get_settings()

WIDGET_JS_PATH = Path(__file__).resolve().parents[1] / "static" / "widget.v1.js"


@router.get("/widget.v1.js")
def widget_script():
    if not WIDGET_JS_PATH.exists():
        raise HTTPException(status_code=500, detail="Widget script missing")

    return FileResponse(
        WIDGET_JS_PATH,
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
        },
    )


@router.get("/widgets/{public_id}/config")
def widget_config(public_id: str):
    widget = sub_repo.get_active_widget_internal(public_id)

    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")

    config = {
        "widget_public_id": widget["public_id"],
        "title": widget["title"],
        "description": widget["description"],
        "button_text": widget["button_text"],
        "fields": widget["fields"],
        "submit_url": f"{settings.public_base_url}/public/submissions",
        "honeypot_field": "website",
    }

    return JSONResponse(
        content=config,
        headers={
            "Cache-Control": "public, max-age=60",
        },
    )


