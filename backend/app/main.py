from fastapi import FastAPI
import os
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
        allow_origins=[
        "http://localhost:3000",
        "https://bidsight-kohl.vercel.app",
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import tenders, match, bids, proposals, analytics, alerts, analysis, billing
app.include_router(tenders.router, prefix="/api/v1")
app.include_router(match.router, prefix="/api/v1")
app.include_router(bids.router, prefix="/api/v1")
app.include_router(proposals.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"status": "ok", "app": settings.app_name}


@app.get("/health")
def health():
    return {"status": "healthy"}