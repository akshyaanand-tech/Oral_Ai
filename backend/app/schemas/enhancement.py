"""
Pydantic schemas for dental image enhancement.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.quality import QualityResult


class EnhanceImageResponse(BaseModel):
    """Result of an AI dental image enhancement operation."""
    success: bool = Field(..., description="Whether enhancement succeeded")
    view: str = Field(default="front", description="Dental view angle (front, left, right, upper, lower)")
    enhanced_image_base64: str = Field(..., description="Base64 data URL of the enhanced JPEG image")
    before_quality: QualityResult = Field(..., description="Quality metrics prior to enhancement")
    after_quality: QualityResult = Field(..., description="Quality metrics following enhancement")
    improvements: List[str] = Field(default_factory=list, description="List of visual corrections performed")
