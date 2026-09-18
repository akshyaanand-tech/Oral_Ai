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
    summary="Search nearby dental practices by coordinates or location name",
    response_description="List of real matching dental providers and contact details.",
)
async def list_providers(
    location: Optional[str] = Query(None, description="City name, address, or Postal/PIN code"),
    latitude: Optional[float] = Query(None, description="User GPS latitude from browser geolocation"),
    longitude: Optional[float] = Query(None, description="User GPS longitude from browser geolocation"),
    city: Optional[str] = Query(None, description="City filter"),
    pin_code: Optional[str] = Query(None, description="PIN code filter"),
    specialty: Optional[str] = Query(None, description="Specialty filter (e.g. 'Orthodontics', 'Periodontics')"),
    query: Optional[str] = Query(None, description="Free text location query"),
    limit: int = Query(6, ge=1, le=20, description="Max providers to return"),
):
    """
    Search nearby dental clinics and providers using:
    - Real GPS coordinates (Option A: browser geolocation) OR
    - Manual location string (Option B: e.g. 'Thiruvananthapuram', 'Kochi', 'Bengaluru').

    Calculates real distances from user coordinates.
    Never fabricates dentists or returns static/Boston results.
    """
    loc_param = location or query or city or pin_code
    return find_providers(
        location=loc_param,
        latitude=latitude,
        longitude=longitude,
        specialty=specialty,
        limit=limit,
    )

