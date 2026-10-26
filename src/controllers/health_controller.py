from datetime import timezone
from datetime import datetime
from schemas.api import HealthResponse
from fastapi import APIRouter

router=APIRouter(
    prefix="/health",
    tags=["health"]
)

@router.get("", response_model=HealthResponse, summary="Basic health check endpoint")
async def health_check()->HealthResponse:
    """Basic health check endpoint"""
    return HealthResponse(
        status="ok/healthy",
        timestamp=datetime.now(timezone.utc)
    )