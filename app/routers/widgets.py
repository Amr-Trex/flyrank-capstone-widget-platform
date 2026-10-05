from fastapi import APIRouter, Depends, HTTPException, status

from app import repositories as repo
from app.auth import get_current_owner
from app.schemas import WidgetCreate, WidgetOut, WidgetUpdate

router = APIRouter(prefix="/widgets", tags=["widgets"])


@router.post("", response_model=WidgetOut, status_code=status.HTTP_201_CREATED)
def create_widget(payload: WidgetCreate, owner=Depends(get_current_owner)):
    return repo.create_widget(owner["id"], payload.model_dump())


@router.get("", response_model=list[WidgetOut])
def list_widgets(owner=Depends(get_current_owner)):
    return repo.list_widgets(owner["id"])


@router.get("/{public_id}", response_model=WidgetOut)
def get_widget(public_id: str, owner=Depends(get_current_owner)):
    widget = repo.get_widget_by_public_id(owner["id"], public_id)

    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")

    return widget


@router.patch("/{public_id}", response_model=WidgetOut)
def update_widget(public_id: str, payload: WidgetUpdate, owner=Depends(get_current_owner)):
    existing = repo.get_widget_by_public_id(owner["id"], public_id)

    if existing is None:
        raise HTTPException(status_code=404, detail="Widget not found")

    updated = repo.update_widget(
        owner["id"],
        public_id,
        payload.model_dump(exclude_unset=True),
    )

    return updated


@router.delete("/{public_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_widget(public_id: str, owner=Depends(get_current_owner)):
    deleted = repo.delete_widget(owner["id"], public_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Widget not found")

    return None