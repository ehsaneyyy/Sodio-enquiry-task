from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.batches import router as batches_router
from app.api.enquiries import router as enquiries_router
from app.core.config import get_settings
from app.core.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


settings = get_settings()

app = FastAPI(title="Sodio Enquiry Triage", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(enquiries_router)
app.include_router(batches_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
