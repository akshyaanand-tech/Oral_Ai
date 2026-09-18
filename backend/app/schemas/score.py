"""
Screening score schemas.
"""
from typing import Dict, Any
from pydantic import BaseModel, Field


class CategoryBreakdown(BaseModel):
    severity: str = Field(..., description="Observed severity string")
    deduction: int = Field(..., ge=0, description="Deduction points subtracted from 100")


class ScoreBreakdown(BaseModel):
    starting_score: int = Field(100, description="Initial reference score")
    alignment: int = Field(0, description="Deduction for alignment observation")
    discoloration: int = Field(0, description="Deduction for discoloration observation")
    tooth_wear: int = Field(0, description="Deduction for tooth wear observation")
    gum_appearance: int = Field(0, description="Deduction for gum appearance observation")
    final_score: int = Field(..., ge=0, le=100, description="Computed final score")
    details: Dict[str, CategoryBreakdown] = Field(
        default_factory=dict,
        description="Per-category severity and deduction details"
    )


class ScreeningScore(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Deterministic visual screening score")
    score_label: str = Field("Preliminary Visual Screening Score", description="Standard score label")
    breakdown: ScoreBreakdown = Field(..., description="Itemized calculation breakdown")
