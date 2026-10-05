from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import widgets

settings = get_settings()

app = FastAPI(title="Widget Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(widgets.router)


@app.get("/health")
def health():
    return {"status": "ok"}