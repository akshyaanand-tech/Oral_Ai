"""
Dental visual screening findings schemas.
Enforces structured outputs from Gemini Vision or Mock AI.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    none = "none"
    mild = "mild"
    moderate = "moderate"
    marked = "marked"
    uncertain = "uncertain"


class BoundingBox(BaseModel):
    x: float = Field(..., ge=0.0, le=1.0, description="Normalized x coordinate [0-1]")
    y: float = Field(..., ge=0.0, le=1.0, description="Normalized y coordinate [0-1]")
    width: float = Field(..., ge=0.0, le=1.0, description="Normalized width [0-1]")
    height: float = Field(..., ge=0.0, le=1.0, description="Normalized height [0-1]")


class Evidence(BaseModel):
    image: str = Field(..., description="View where observation was visible (front, left, right, upper, lower)")
    region: Optional[BoundingBox] = Field(None, description="Optional bounding box coordinates")


class FindingDetail(BaseModel):
    finding: str = Field(..., description="Cautious non-diagnostic description of visible observation")
    severity: Severity = Field(..., description="Observed severity level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in visible observation [0.0-1.0]")
    evidence: Optional[Evidence] = Field(None, description="Visual evidence location if reliably identified")


class DentalFindings(BaseModel):
    alignment: FindingDetail = Field(..., description="Visual observations regarding alignment, spacing, or crowding")
    discoloration: FindingDetail = Field(..., description="Visual observations regarding surface staining or color differences")
    tooth_wear: FindingDetail = Field(..., description="Visual observations regarding surface flattening or visible wear patterns")
    gum_appearance: FindingDetail = Field(..., description="Visual observations regarding redness, swelling, or gum margin")
