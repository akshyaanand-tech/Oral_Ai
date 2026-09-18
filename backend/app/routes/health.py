"""
Health check route.
GET /health
"""

import os
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check")
@router.get("/api/health", summary="Health Check Alias")
async def health_check():
    """Returns basic system operational status."""
    mock_mode = os.getenv("MOCK_AI", "true").lower() in ("true", "1", "yes")
    return {
        "status": "ok",
        "service": "dental-screening-backend",
        "mock_ai": mock_mode,
        "version": "1.0.0",
    }
