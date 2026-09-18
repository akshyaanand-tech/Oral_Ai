"""
GET /api/providers

Provider search route for finding local dentists and specialists by City or PIN code.
Works offline using providers.json fallback; enhances with live API when available.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Query

from app.schemas.recommendation import ProviderInfo
from app.services.provider_service import find_providers

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Providers"])


@router.get(
    "/api/providers",
    response_model=List[ProviderInfo],
    summary="Search nearby dental practices by City or PIN code",
    response_description="List of matching dental providers and contact details.",
)
async def list_providers(
    location: Optional[str] = Query(None, description="City name or Postal/PIN code"),
    city: Optional[str] = Query(None, description="City filter"),
    pin_code: Optional[str] = Query(None, description="PIN code filter"),
    specialty: Optional[str] = Query(None, description="Specialty filter (e.g. 'Orthodontics', 'Periodontics')"),
    query: Optional[str] = Query(None, description="Free text search query"),
    limit: int = Query(6, ge=1, le=20, description="Max providers to return"),
):
    """
    Search nearby dental clinics and providers.
    Uses city/PIN code rather than requiring GPS coordinates.
    Ratings/reviews are strictly informative.
    """
    loc_param = location or city or pin_code or query
    return find_providers(location=loc_param, specialty=specialty, limit=limit)
