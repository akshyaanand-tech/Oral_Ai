"""
Schemas for Recommendation Engine, Care Pathway, Cost Estimation, and Provider Directory.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class CareStep(BaseModel):
    step_id: str = Field(..., description="Unique step identifier")
    title: str = Field(..., description="Actionable title for this care pathway step")
    category: str = Field(..., description="Clinical or visual indicator category")
    action: str = Field(..., description="Recommended action or assessment")
    urgency: str = Field(..., description="Recommended urgency (e.g. Routine, Recommended within 2-4 weeks)")
    recommended_specialist: str = Field(..., description="Suggested dental professional (e.g. General Dentist, Orthodontist, Periodontist)")
    home_care: List[str] = Field(default_factory=list, description="Targeted home hygiene recommendations")


class CarePathway(BaseModel):
    steps: List[CareStep] = Field(..., description="Prioritized list of care pathway steps")
    summary: str = Field(..., description="Overview summary of the suggested care pathway")
    recommended_specialists: List[str] = Field(default_factory=list, description="Distinct dental specialties suggested")
    home_care_summary: List[str] = Field(default_factory=list, description="Consolidated daily oral care actions")
    recall_recommendation: str = Field(..., description="Suggested professional recall timeframe")


class CostEstimate(BaseModel):
    service: str = Field(..., description="Name of the dental service or procedure")
    category: str = Field(..., description="Relevant clinical category")
    min_cost: float = Field(..., description="Lower bound indicative estimate")
    max_cost: float = Field(..., description="Upper bound indicative estimate")
    currency: str = Field("INR", description="Currency ISO code")
    cost_range: str = Field(..., description="Formatted indicative range string (e.g. '₹500 - ₹1,200')")
    notes: str = Field(..., description="Transparency notes and procedure description")
    indicative: bool = Field(True, description="Always true; costs are non-guaranteed estimates")


class ProviderInfo(BaseModel):
    provider_id: str = Field(..., description="Unique provider ID")
    name: str = Field(..., description="Clinic or practice name")
    specialty: str = Field(..., description="Primary specialty (General Dentistry, Orthodontics, Periodontics)")
    doctor: Optional[str] = Field(None, description="Doctor or clinical director name")
    address: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    pin_code: Optional[str] = Field(None, description="Postal/PIN code")
    rating: Optional[float] = Field(None, description="Patient rating (1.0 to 5.0) for informational purposes only")
    review_count: Optional[int] = Field(None, description="Number of reviews")
    phone: Optional[str] = Field(None, description="Contact telephone number")
    website: Optional[str] = Field(None, description="Official practice website")
    accepting_new_patients: bool = Field(True, description="Whether practice is accepting new patients")
    next_available: Optional[str] = Field(None, description="Estimated next available appointment slot")
    distance: Optional[str] = Field(None, description="Approximate distance if location-matched")
    latitude: Optional[float] = Field(None, description="Clinic latitude")
    longitude: Optional[float] = Field(None, description="Clinic longitude")
    source: str = Field("live_api", description="'live_api' or 'location_provider'")
