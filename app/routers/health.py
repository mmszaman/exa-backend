"""Health check endpoint."""

from datetime import datetime
from fastapi import APIRouter

from app.schemas.notification import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - confirms API is running."""
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat(),
    }
