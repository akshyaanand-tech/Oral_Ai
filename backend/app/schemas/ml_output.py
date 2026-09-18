"""
Schemas for Machine Learning Image Analysis Output.
Enforces structured findings with severity, confidence, and visual observations.
Results are strictly non-diagnostic visual screening observations.
"""

from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class FindingSeverity(str, Enum):
    none = "none"
    mild = "mild"
    moderate = "moderate"
    marked = "marked"
    uncertain = "uncertain"


class FindingCategory(str, Enum):
    alignment = "alignment"
    discoloration = "discoloration"
    tooth_wear = "tooth_wear"
    gum_appearance = "gum_appearance"


class BoundingRegion(BaseModel):
    x: float = Field(..., ge=0.0, le=1.0, description="Normalized x coordinate")
    y: float = Field(..., ge=0.0, le=1.0, description="Normalized y coordinate")
    width: float = Field(..., ge=0.0, le=1.0, description="Normalized width")
    height: float = Field(..., ge=0.0, le=1.0, description="Normalized height")


class FindingEvidence(BaseModel):
    image: str = Field(..., description="View where observation was visible (front, left, right, upper, lower)")
    region: Optional[BoundingRegion] = Field(None, description="Optional bounding coordinates")


class MLFindingItem(BaseModel):
    category: str = Field(..., description="Visual indicator category (alignment, discoloration, tooth_wear, gum_appearance)")
    finding: str = Field(..., description="Cautious non-diagnostic description of visible observation")
    severity: FindingSeverity = Field(..., description="Observed severity level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in visible observation [0.0-1.0]")
    evidence: Optional[FindingEvidence] = Field(None, description="Image view and region supporting observation")


class MLAnalysisOutput(BaseModel):
    findings: List[MLFindingItem] = Field(..., description="List of structured findings across categories")
    findings_by_category: Dict[str, MLFindingItem] = Field(default_factory=dict, description="Findings keyed by category name")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall image quality and detection confidence")
    analyzed_views: List[str] = Field(default_factory=lambda: ["front", "left", "right", "upper", "lower"])
