from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="BidSight API",
    description="AI-powered tender discovery platform",
    version="0.1.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import tenders
app.include_router(tenders.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"status": "ok", "app": settings.app_name}


@app.get("/health")
def health():
    return {"status": "healthy"}