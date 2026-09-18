"""
Cost Estimation Service.

Provides indicative procedure cost ranges based on the care pathway steps.
Maintains backend/data/costs.json as the local fallback database.
Optionally integrates with external regional cost API when configured.
Application NEVER depends on live cost data and seamlessly falls back to local data.
Always displays costs as indicative ranges, not guaranteed prices.
"""

import os
import json
import logging
import re
from typing import List, Optional, Dict, Any

from app.schemas.recommendation import CarePathway, CostEstimate

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
COSTS_FILE = os.path.join(DATA_DIR, "costs.json")

# In-memory default procedure costs if costs.json is unavailable
DEFAULT_PROCEDURES = [
    {
        "code": "routine_exam",
        "service": "Comprehensive Oral Examination",
        "category": "preventive",
        "min_cost": 500.0,
        "max_cost": 1200.0,
        "currency": "INR",
        "unit": "visit",
        "notes": "Visual clinical examination by general dental practitioner."
    },
    {
        "code": "prophylaxis_cleaning",
        "service": "Professional Dental Cleaning / Prophylaxis",
        "category": "discoloration",
        "min_cost": 1000.0,
        "max_cost": 2500.0,
        "currency": "INR",
        "unit": "session",
        "notes": "Removal of plaque, calculus, and external surface stains."
    },
    {
        "code": "orthodontic_consult",
        "service": "Orthodontic Evaluation & Consultation",
        "category": "alignment",
        "min_cost": 800.0,
        "max_cost": 2000.0,
        "currency": "INR",
        "unit": "consultation",
        "notes": "Specialist orthodontic assessment for crowding, spacing, or bite."
    },
    {
        "code": "periodontal_exam",
        "service": "Periodontal Health Evaluation",
        "category": "gum_appearance",
        "min_cost": 600.0,
        "max_cost": 1500.0,
        "currency": "INR",
        "unit": "visit",
        "notes": "Detailed gingival pocket depth measurement and tissue review."
    },
    {
        "code": "occlusal_guard",
        "service": "Custom Night Guard / Splint Evaluation",
        "category": "tooth_wear",
        "min_cost": 3000.0,
        "max_cost": 7000.0,
        "currency": "INR",
        "unit": "appliance",
        "notes": "Custom lab-fabricated protective dental appliance for tooth wear or clenching."
    },
    {
        "code": "dental_xrays",
        "service": "Diagnostic Bitewing / Periapical Radiographs",
        "category": "diagnostic",
        "min_cost": 350.0,
        "max_cost": 1000.0,
        "currency": "INR",
        "unit": "series",
        "notes": "Digital X-ray imaging recommended during initial clinical evaluation."
    }
]


def _load_costs_data() -> Dict[str, Any]:
    """Safely loads costs.json fallback database."""
    if os.path.exists(COSTS_FILE):
        try:
            with open(COSTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.warning("Could not read %s: %s; using in-memory costs", COSTS_FILE, exc)
    return {"procedures": DEFAULT_PROCEDURES, "regional_multipliers": {}}


def _detect_region(location_str: Optional[str]) -> str:
    """Detect whether location is India (IN), UK (UK), or US default."""
    if not location_str:
        return "US"
    loc = location_str.strip().lower()

    # 6-digit PIN code or Indian city names
    if re.search(r"^[1-9][0-9]{5}$", loc) or any(
        city in loc for city in ["bengaluru", "bangalore", "mumbai", "delhi", "chennai", "kolkata", "hyderabad", "pune"]
    ):
        return "IN"

    # UK postal code or London
    if any(city in loc for city in ["london", "manchester", "birmingham"]) or re.search(r"^[a-z]{1,2}[0-9][a-z0-9]?\s?[0-9][a-z]{2}$", loc):
        return "UK"

    return "US"


def _fetch_external_costs(region: str) -> Optional[List[dict]]:
    """
    Attempt to fetch from external regional cost API if configured.
    Always returns None on failure without throwing exceptions.
    """
    api_url = os.getenv("EXTERNAL_COST_API_URL", "").strip()
    if not api_url:
        return None

    try:
        import httpx
        with httpx.Client(timeout=2.0) as client:
            resp = client.get(f"{api_url}?region={region}")
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    logger.info("Retrieved external live cost data for region: %s", region)
                    return data
    except Exception as exc:
        logger.warning("External cost API call failed (%s); falling back to local costs.json", exc)

    return None


def estimate_costs(
    care_pathway: CarePathway,
    location: Optional[str] = None,
) -> List[CostEstimate]:
    """
    Derives indicative cost ranges for procedures corresponding to the care pathway steps.

    Uses:
      1. External Cost API (if available and healthy)
      2. Local costs.json fallback database (always available)
    """
    costs_data = _load_costs_data()
    procedures = costs_data.get("procedures", DEFAULT_PROCEDURES)
    multipliers = costs_data.get("regional_multipliers", {})

    region = _detect_region(location)

    # Check optional live external API
    external_data = _fetch_external_costs(region)
    if external_data:
        procedures = external_data

    # Currency and multiplier - strictly Indian Rupees (₹)
    currency = "INR"
    sym = "₹"
    multiplier = 1.0

    # Identify categories needed in care pathway
    pathway_categories = {s.category for s in care_pathway.steps}
    # Always include preventive/exam as foundational
    pathway_categories.add("preventive")

    estimates: List[CostEstimate] = []
    seen_codes = set()

    for proc in procedures:
        cat = proc.get("category", "")
        code = proc.get("code", proc.get("service", ""))

        if (cat in pathway_categories or cat == "preventive") and code not in seen_codes:
            seen_codes.add(code)
            base_min = float(proc.get("min_cost", 500))
            base_max = float(proc.get("max_cost", 1200))

            adj_min = round(base_min * multiplier)
            adj_max = round(base_max * multiplier)

            range_str = f"{sym}{adj_min:,} - {sym}{adj_max:,}"

            estimates.append(
                CostEstimate(
                    service=proc.get("service", "Dental Service"),
                    category=cat,
                    min_cost=float(adj_min),
                    max_cost=float(adj_max),
                    currency=currency,
                    cost_range=range_str,
                    notes=proc.get("notes", "Indicative cost range in INR; actual charges vary by clinic."),
                    indicative=True,
                )
            )

    # Guarantee at least comprehensive exam if estimates list was empty
    if not estimates:
        estimates.append(
            CostEstimate(
                service="Comprehensive Oral Examination",
                category="preventive",
                min_cost=500.0,
                max_cost=1200.0,
                currency="INR",
                cost_range="₹500 - ₹1,200",
                notes="Initial comprehensive clinical examination and consultation.",
                indicative=True,
            )
        )

    return estimates
