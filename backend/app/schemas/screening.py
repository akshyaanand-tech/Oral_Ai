"""
Schemas for Endpoint POST /api/screen Request and Response.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.ml_output import MLFindingItem
from app.schemas.recommendation import CareStep, ProviderInfo, CostEstimate


class ScoreDeductionItem(BaseModel):
    category: str
    severity: str
    deduction: int


class ScoreDetails(BaseModel):
    starting_score: int = 100
    total_deductions: int
    final_score: int
    category_deductions: Dict[str, int]


class ScreeningResponse(BaseModel):
    screening_score: int = Field(..., ge=0, le=100, description="Preliminary visual screening score (0–100)")
    findings: List[MLFindingItem] = Field(default_factory=list, description="Structured visual findings with severity and confidence")
    care_pathway: List[CareStep] = Field(default_factory=list, description="Recommended care pathway steps")
    providers: List[ProviderInfo] = Field(default_factory=list, description="Relevant nearby dental providers")
    estimated_costs: List[CostEstimate] = Field(default_factory=list, description="Indicative procedure cost ranges")
    explanation: str = Field(..., description="Educational plain-language summary and guidance")
    disclaimer: str = Field(
        "This is a screening tool and does not provide a diagnosis.",
        description="Standard medical screening disclaimer"
    )
    score_details: Optional[ScoreDetails] = Field(None, description="Itemized score deductions for transparency")
    screening_id: Optional[str] = Field(None, description="Unique screening tracking ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context such as quality check or processing notes")
