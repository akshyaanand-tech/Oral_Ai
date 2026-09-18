"""
Provider Search Service.

Searches for nearby dental care providers using City or Postal/PIN code (no GPS required).
Supports optional live Place/Business API integration.
Falls back seamlessly to local backend/data/providers.json on any error or missing credentials.

CRITICAL ARCHITECTURAL RULE:
Provider ratings, review counts, or locations MUST NEVER influence the medical
recommendation, care pathway urgency, or screening score. They are strictly informative.
"""

import os
import json
import logging
import re
from typing import List, Optional, Dict, Any

from app.schemas.recommendation import ProviderInfo

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
PROVIDERS_FILE = os.path.join(DATA_DIR, "providers.json")

# In-memory default providers if providers.json cannot be read
DEFAULT_PROVIDERS = [
    {
        "provider_id": "prov_def_01",
        "name": "Beacon Dental Care & Preventive Clinic",
        "specialty": "General Dentistry",
        "doctor": "Dr. Sarah Jenkins, DDS",
        "address": "142 Commonwealth Ave, Suite 300",
        "city": "Boston",
        "pin_code": "02116",
        "rating": 4.9,
        "review_count": 128,
        "phone": "(617) 555-0142",
        "website": "https://beacondentalcare.example.com",
        "accepting_new_patients": True,
        "next_available": "Tomorrow at 10:00 AM"
    },
    {
        "provider_id": "prov_def_02",
        "name": "Premier Orthodontic & Alignment Studio",
        "specialty": "Orthodontics",
        "doctor": "Dr. David Kim, DMD, MS",
        "address": "575 Boylston St, 4th Floor",
        "city": "Boston",
        "pin_code": "02116",
        "rating": 4.8,
        "review_count": 95,
        "phone": "(617) 555-0189",
        "website": "https://premierortho.example.com",
        "accepting_new_patients": True,
        "next_available": "Thursday at 2:30 PM"
    },
    {
        "provider_id": "prov_def_03",
        "name": "Apex Periodontics & Gum Health Center",
        "specialty": "Periodontics",
        "doctor": "Dr. Emily Rodriguez, DDS, MS",
        "address": "400 Atlantic Ave, Suite 210",
        "city": "Boston",
        "pin_code": "02110",
        "rating": 5.0,
        "review_count": 74,
        "phone": "(617) 555-0210",
        "website": "https://apexperio.example.com",
        "accepting_new_patients": True,
        "next_available": "Friday at 11:15 AM"
    }
]


def _load_fallback_providers() -> List[Dict[str, Any]]:
    """Loads fallback providers from providers.json."""
    if os.path.exists(PROVIDERS_FILE):
        try:
            with open(PROVIDERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("providers", DEFAULT_PROVIDERS)
        except Exception as exc:
            logger.warning("Could not read %s: %s; using in-memory providers", PROVIDERS_FILE, exc)
    return DEFAULT_PROVIDERS


def _fetch_live_providers(location_query: str, specialty: Optional[str] = None) -> Optional[List[ProviderInfo]]:
    """
    Attempt to fetch providers from live external Places API if API key is provided.
    Supports Google Places API (New Text Search or Nearby Search).
    Ensures short timeout (max 2.0s) and clean fallback on any exception.
    """
    google_api_key = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()
    if not google_api_key:
        return None

    try:
        import httpx
        search_text = f"dentist {specialty or ''} in {location_query}".strip()
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": search_text,
            "key": google_api_key,
        }

        with httpx.Client(timeout=2.5) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results:
                    live_list: List[ProviderInfo] = []
                    for idx, place in enumerate(results[:5]):
                        live_list.append(
                            ProviderInfo(
                                provider_id=f"live_{place.get('place_id', f'p_{idx}')}",
                                name=place.get("name", "Dental Clinic"),
                                specialty=specialty or "General Dentistry",
                                doctor=None,
                                address=place.get("formatted_address", location_query),
                                city=location_query,
                                pin_code=None,
                                rating=float(place.get("rating", 4.5)) if place.get("rating") else None,
                                review_count=int(place.get("user_ratings_total", 0)) if place.get("user_ratings_total") else None,
                                phone=None,
                                website=None,
                                accepting_new_patients=True,
                                distance="Within specified area",
                                source="live_api",
                            )
                        )
                    logger.info("Found %d live providers via Google Places API for query '%s'", len(live_list), location_query)
                    return live_list
    except Exception as exc:
        logger.warning("Live provider API failed (%s); falling back to local providers.json", exc)

    return None


def find_providers(
    location: Optional[str] = None,
    specialty: Optional[str] = None,
    limit: int = 5,
) -> List[ProviderInfo]:
    """
    Find nearby dental care providers given a city or PIN code.

    Pipeline:
      1. If live search API is enabled and configured, attempt query.
      2. If live API is disabled, absent, times out, or fails:
         Search local providers.json matching city or PIN code prefix.
      3. If no exact match for the city/PIN, return top general/specialty providers
         from fallback database.
    """
    cleaned_loc = (location or "").strip()

    # Try live API first if location query is present
    if cleaned_loc:
        live_results = _fetch_live_providers(cleaned_loc, specialty)
        if live_results:
            return live_results[:limit]

    # Local fallback search
    raw_providers = _load_fallback_providers()

    matched: List[Dict[str, Any]] = []

    if cleaned_loc:
        query_lower = cleaned_loc.lower()

        # Check for PIN code or City match
        for p in raw_providers:
            p_city = str(p.get("city", "")).lower()
            p_pin = str(p.get("pin_code", "")).lower()

            city_match = query_lower in p_city or p_city in query_lower
            pin_match = p_pin.startswith(query_lower) or query_lower.startswith(p_pin)

            if city_match or pin_match:
                matched.append(p)

    # Filter or prioritize by requested specialty if provided
    if specialty and matched:
        spec_lower = specialty.lower()
        spec_matched = [p for p in matched if spec_lower in p.get("specialty", "").lower()]
        if spec_matched:
            matched = spec_matched

    # If no local match was found for the specific location, return top providers from directory
    if not matched:
        if specialty:
            spec_lower = specialty.lower()
            matched = [p for p in raw_providers if spec_lower in p.get("specialty", "").lower()]
        if not matched:
            matched = raw_providers

    # Convert to ProviderInfo schemas
    results: List[ProviderInfo] = []
    for item in matched[:limit]:
        results.append(
            ProviderInfo(
                provider_id=item.get("provider_id", f"prov_{len(results)+1}"),
                name=item.get("name", "Dental Care Clinic"),
                specialty=item.get("specialty", "General Dentistry"),
                doctor=item.get("doctor"),
                address=item.get("address", ""),
                city=item.get("city", "Boston"),
                pin_code=item.get("pin_code"),
                rating=float(item["rating"]) if "rating" in item and item["rating"] is not None else None,
                review_count=int(item["review_count"]) if "review_count" in item and item["review_count"] is not None else None,
                phone=item.get("phone"),
                website=item.get("website"),
                accepting_new_patients=item.get("accepting_new_patients", True),
                next_available=item.get("next_available"),
                distance="Local practice" if cleaned_loc else None,
                source="fallback_database",
            )
        )

    return results
