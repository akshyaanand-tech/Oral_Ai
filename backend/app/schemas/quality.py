"""
Image quality check schemas.
Supports two-stage quality assessment and enhancement tracking.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class QualityResult(BaseModel):
    """
    Technical quality check outcome for a single image.
    Note: Evaluates technical image usability, not clinical dental validity.
    """
    passed: bool = Field(
        ...,
        description="True if the image meets technical usability thresholds"
    )
    quality_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Computed effective quality score between 0.0 and 1.0"
    )
    original_quality_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Quality score prior to enhancement"
    )
    enhanced_quality_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Quality score following enhancement"
    )
    enhanced: bool = Field(
        default=False,
        description="Whether automatic enhancement was applied to improve this image"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of human-readable issues if the image fails checks or needs retake"
    )
