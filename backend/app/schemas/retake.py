"""
Schemas for retake response when image enhancement cannot make an image technically usable.
"""
from typing import List
from pydantic import BaseModel, Field


class RetakeItem(BaseModel):
    view: str = Field(..., description="Flagged view name (front, left, right, upper, lower)")
    reason: str = Field(..., description="Specific explanation of why retake is needed")


class RetakeResponse(BaseModel):
    status: str = Field("retake_required", description="Status code indicating retake is needed")
    retake: List[RetakeItem] = Field(..., description="List of views requiring retake and guidance")
