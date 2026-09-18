"""
Location-Aware Dental Provider Search Service.

Searches for real dental clinics and practitioners based on user-provided coordinates
(browser geolocation) or manual location (e.g. "Thiruvananthapuram", "Kochi", "Bengaluru").

Data integrity rules:
  1. DO NOT invent dentists, doctor names, addresses, ratings, or distances.
  2. DO NOT return a static or hardcoded list for all locations.
  3. Distance is ONLY displayed when calculated from real coordinates.
  4. If a location has no results or the API is unavailable, return an empty list ([])
     so the UI displays an honest "No dentists found" / "Search unavailable" message.
"""

import os
import math
import logging
import re
from typing import List, Optional, Dict, Any

import httpx

from app.schemas.recommendation import ProviderInfo

logger = logging.getLogger(__name__)

USER_AGENT = "OralScreenAI/1.0 (preventive-oral-health-screening; contact: health@oralscreen.example.com)"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two coordinate pairs in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


def _geocode_location(location_name: str) -> Optional[tuple[float, float, str]]:
    """
    Geocodes a location query (e.g., 'Thiruvananthapuram', 'Kochi') to (lat, lon, display_name).
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location_name.strip(),
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=8.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                results = resp.json()
                if results and len(results) > 0:
                    lat = float(results[0]["lat"])
                    lon = float(results[0]["lon"])
                    display = results[0].get("display_name", location_name)
                    return lat, lon, display
    except Exception as exc:
        logger.warning("Geocoding failed for '%s': %s", location_name, exc)
    return None


def _fetch_from_places_api(
    location_query: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    specialty: Optional[str] = None,
    limit: int = 6,
) -> Optional[List[ProviderInfo]]:
    """
    Search using external Google Places API or DENTIST_API_URL if configured.
    """
    api_key = os.getenv("DENTIST_API_KEY") or os.getenv("GOOGLE_PLACES_API_KEY", "").strip()
    if not api_key:
        return None

    api_url = os.getenv("DENTIST_API_URL") or "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    try:
        with httpx.Client(timeout=4.0) as client:
            if lat is not None and lon is not None:
                params = {
                    "location": f"{lat},{lon}",
                    "radius": 15000,
                    "type": "dentist",
                    "keyword": specialty or "dentist dental clinic",
                    "key": api_key,
                }
            else:
                api_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                params = {
                    "query": f"dentist {specialty or ''} in {location_query}".strip(),
                    "key": api_key,
                }

            resp = client.get(api_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results:
                    providers: List[ProviderInfo] = []
                    for idx, p in enumerate(results[:limit]):
                        p_geom = p.get("geometry", {}).get("location", {})
                        p_lat = p_geom.get("lat")
                        p_lng = p_geom.get("lng")

                        dist_str = None
                        if lat is not None and lon is not None and p_lat and p_lng:
                            d_km = haversine_km(lat, lon, p_lat, p_lng)
                            dist_str = f"{d_km} km away"

                        providers.append(
                            ProviderInfo(
                                provider_id=f"live_{p.get('place_id', f'p_{idx}')}",
                                name=p.get("name", "Dental Clinic"),
                                specialty=specialty or "General Dentistry",
                                doctor=None,
                                address=p.get("vicinity") or p.get("formatted_address", ""),
                                city=location_query or "Local Area",
                                pin_code=None,
                                rating=float(p["rating"]) if p.get("rating") else None,
                                review_count=int(p["user_ratings_total"]) if p.get("user_ratings_total") else None,
                                phone=None,
                                website=None,
                                accepting_new_patients=True,
                                next_available="Contact clinic for availability",
                                distance=dist_str,
                                latitude=p_lat,
                                longitude=p_lng,
                                source="live_api",
                            )
                        )
                    logger.info("Retrieved %d providers from live Places API", len(providers))
                    return providers
    except Exception as exc:
        logger.warning("Places API search error: %s", exc)
    return None


def _fetch_from_osm_live(
    location_query: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    specialty: Optional[str] = None,
    limit: int = 6,
) -> List[ProviderInfo]:
    """
    Search real dental clinics from OpenStreetMap live services (Nominatim & Overpass).
    Does NOT invent dentists or fall back to unrelated cities.
    """
    providers: List[ProviderInfo] = []

    # If coordinates are missing but location query is present, geocode first
    user_lat, user_lon = lat, lon
    resolved_city = location_query or "Local Area"

    if (user_lat is None or user_lon is None) and location_query:
        geo = _geocode_location(location_query)
        if geo:
            user_lat, user_lon, _ = geo

    # Approach 1: Nominatim amenity search for dentist
    try:
        url = "https://nominatim.openstreetmap.org/search"
        search_term = f"dentist in {location_query}" if location_query else "dentist"
        params: Dict[str, Any] = {
            "q": search_term,
            "format": "json",
            "limit": limit,
            "addressdetails": 1,
        }

        # If we have coordinates, bound search near user
        if user_lat is not None and user_lon is not None and not location_query:
            delta = 0.2  # roughly 20km
            params["viewbox"] = f"{user_lon-delta},{user_lat+delta},{user_lon+delta},{user_lat-delta}"
            params["bounded"] = 1

        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=8.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                elements = resp.json()
                for idx, el in enumerate(elements):
                    # Filter out non-amenity results (like streets with the word dentist)
                    category = el.get("class") or el.get("type")
                    if category and category not in ("amenity", "healthcare", "office", "shop"):
                        continue

                    p_lat = float(el["lat"]) if "lat" in el else None
                    p_lon = float(el["lon"]) if "lon" in el else None

                    dist_str = None
                    if user_lat is not None and user_lon is not None and p_lat is not None and p_lon is not None:
                        d_km = haversine_km(user_lat, user_lon, p_lat, p_lon)
                        # Sanity check: if searching a specific city/coords, ignore clinics > 45km away
                        if d_km > 45.0:
                            continue
                        dist_str = f"{d_km} km away"

                    raw_name = el.get("name") or el.get("display_name", "").split(",")[0]
                    # Ensure name is reasonable
                    if not raw_name or len(raw_name) < 3:
                        raw_name = "Dental Clinic"

                    addr_dict = el.get("address", {})
                    road = addr_dict.get("road") or addr_dict.get("suburb") or ""
                    city = addr_dict.get("city") or addr_dict.get("town") or addr_dict.get("county") or resolved_city
                    postcode = addr_dict.get("postcode")
                    full_address = el.get("display_name", f"{road}, {city}")

                    providers.append(
                        ProviderInfo(
                            provider_id=f"osm_{el.get('place_id', idx+1)}",
                            name=raw_name,
                            specialty=specialty or "General Dentistry",
                            doctor=None,
                            address=full_address,
                            city=city,
                            pin_code=postcode,
                            rating=None,  # Do NOT invent ratings
                            review_count=None,
                            phone=None,
                            website=None,
                            accepting_new_patients=True,
                            next_available="Contact clinic directly",
                            distance=dist_str,
                            latitude=p_lat,
                            longitude=p_lon,
                            source="live_api",
                        )
                    )
    except Exception as exc:
        logger.warning("OSM Nominatim dentist search failed: %s", exc)

    # Approach 2: If Nominatim returned empty and we have coordinates, try Overpass API
    if not providers and user_lat is not None and user_lon is not None:
        try:
            overpass_url = "https://overpass-api.de/api/interpreter"
            query = f"""[out:json][timeout:8];(node["amenity"="dentist"](around:25000, {user_lat}, {user_lon});node["healthcare"="dentist"](around:25000, {user_lat}, {user_lon});way["amenity"="dentist"](around:25000, {user_lat}, {user_lon}););out center {limit};"""
            with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=9.0) as client:
                r2 = client.post(overpass_url, data={"data": query})
                if r2.status_code == 200:
                    op_data = r2.json()
                    for idx, node in enumerate(op_data.get("elements", [])):
                        tags = node.get("tags", {})
                        raw_name = tags.get("name") or tags.get("operator") or "Dental Care Clinic"
                        p_lat = node.get("lat") or node.get("center", {}).get("lat")
                        p_lon = node.get("lon") or node.get("center", {}).get("lon")

                        dist_str = None
                        if p_lat and p_lon:
                            d_km = haversine_km(user_lat, user_lon, p_lat, p_lon)
                            dist_str = f"{d_km} km away"

                        street = tags.get("addr:street") or tags.get("addr:full") or ""
                        city = tags.get("addr:city") or resolved_city

                        providers.append(
                            ProviderInfo(
                                provider_id=f"overpass_{node.get('id', idx+1)}",
                                name=raw_name,
                                specialty=tags.get("healthcare:speciality") or specialty or "General Dentistry",
                                doctor=tags.get("operator"),
                                address=f"{street} {city}".strip() or resolved_city,
                                city=city,
                                pin_code=tags.get("addr:postcode"),
                                rating=None,
                                review_count=None,
                                phone=tags.get("phone") or tags.get("contact:phone"),
                                website=tags.get("website") or tags.get("contact:website"),
                                accepting_new_patients=True,
                                next_available="Contact clinic directly",
                                distance=dist_str,
                                latitude=p_lat,
                                longitude=p_lon,
                                source="live_api",
                            )
                        )
        except Exception as exc:
            logger.warning("Overpass dentist search failed: %s", exc)

    return providers[:limit]


def find_providers(
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    specialty: Optional[str] = None,
    limit: int = 6,
) -> List[ProviderInfo]:
    """
    Location-Aware Dental Provider Search.

    Accepts:
      - latitude & longitude (from browser geolocation) OR
      - location string (manual search like "Thiruvananthapuram", "Kochi", "Bengaluru")

    Never fabricates dentists or returns static/Boston results for unrelated locations.
    """
    cleaned_loc = (location or "").strip()

    # 1. Try external Places API if key is present
    places_res = _fetch_from_places_api(
        location_query=cleaned_loc,
        lat=latitude,
        lon=longitude,
        specialty=specialty,
        limit=limit,
    )
    if places_res is not None and len(places_res) > 0:
        return places_res

    # 2. Query real live OpenStreetMap directory
    osm_results = _fetch_from_osm_live(
        location_query=cleaned_loc,
        lat=latitude,
        lon=longitude,
        specialty=specialty,
        limit=limit,
    )
    if osm_results:
        return osm_results

    # 3. If no real clinics were found for the requested location/coordinates,
    # return an EMPTY list so the UI can display an honest "No dentists found" state.
    logger.info("No real dental clinics found for location='%s', lat=%s, lon=%s", cleaned_loc, latitude, longitude)
    return []
