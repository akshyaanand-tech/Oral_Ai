"""
Smart Dentist Referral & Provider Connection Service.

Abstracts the patient-to-care workflow:
Patient -> Screening -> Report -> Professional Evaluation -> Dental Provider Connection.
Provides generic provider directory and appointment inquiry management structured
for easy extension to practice management systems (PMS) such as CareStack or open dental APIs.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Sample realistic dental practices for demonstration
DEMO_PROVIDERS = [
    {
        "id": "prov_101",
        "name": "Beacon Dental Care & Preventive Clinic",
        "specialty": "General & Preventive Dentistry",
        "doctor": "Dr. Sarah Jenkins, DDS",
        "address": "142 Commonwealth Ave, Suite 300",
        "distance": "0.8 miles away",
        "rating": 4.9,
        "review_count": 128,
        "accepting_new_patients": True,
        "next_available": "Tomorrow at 10:00 AM",
        "phone": "(555) 234-5678",
        "integration_type": "carestack_compatible"
    },
    {
        "id": "prov_102",
        "name": "Metro Family & Cosmetic Dentistry",
        "specialty": "Preventive Care & Orthodontics",
        "doctor": "Dr. Michael Chen, DMD",
        "address": "85 Newbury Street, 2nd Floor",
        "distance": "1.4 miles away",
        "rating": 4.8,
        "review_count": 94,
        "accepting_new_patients": True,
        "next_available": "Thursday at 2:30 PM",
        "phone": "(555) 345-6789",
        "integration_type": "generic_pms"
    },
    {
        "id": "prov_103",
        "name": "Apex Periodontics & Oral Wellness",
        "specialty": "Gingival & Periodontal Specialist",
        "doctor": "Dr. Emily Rodriguez, DDS, MS",
        "address": "400 Atlantic Ave",
        "distance": "2.1 miles away",
        "rating": 5.0,
        "review_count": 67,
        "accepting_new_patients": True,
        "next_available": "Friday at 11:15 AM",
        "phone": "(555) 456-7890",
        "integration_type": "generic_pms"
    },
]


def list_dental_providers(query: Optional[str] = None) -> List[Dict[str, Any]]:
    """List available dental care providers."""
    if not query:
        return DEMO_PROVIDERS
    q = query.lower()
    return [
        p for p in DEMO_PROVIDERS
        if q in p["name"].lower() or q in p["specialty"].lower() or q in p["doctor"].lower()
    ]


def submit_referral_request(
    screening_id: str,
    provider_id: str,
    patient_name: str,
    patient_email: str,
    patient_phone: Optional[str] = None,
    preferred_time: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Register an appointment inquiry linking the patient's preliminary screening report
    with a dental practice provider.
    """
    inquiry_id = f"inq_{uuid.uuid4().hex[:8]}"
    provider = next((p for p in DEMO_PROVIDERS if p["id"] == provider_id), None)
    provider_name = provider["name"] if provider else "Selected Dental Clinic"

    record = {
        "inquiry_id": inquiry_id,
        "screening_id": screening_id,
        "provider_id": provider_id,
        "provider_name": provider_name,
        "patient_name": patient_name,
        "patient_email": patient_email,
        "patient_phone": patient_phone or "",
        "preferred_time": preferred_time or "Any available time",
        "notes": notes or "",
        "status": "pending_provider_confirmation",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "report_attached": True,
    }

    logger.info("Created referral inquiry '%s' for screening '%s' -> provider '%s'",
                inquiry_id, screening_id, provider_name)
    return record
