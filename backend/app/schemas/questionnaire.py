"""
Questionnaire schemas for patient-reported oral health background.
Kept strictly separate from deterministic visual AI scoring.
"""
from typing import Optional
from pydantic import BaseModel, Field


class QuestionnaireResponses(BaseModel):
    """
    Patient self-reported background information.
    Used for personalized guidance and clinical report context only.
    """
    tooth_sensitivity: Optional[str] = Field(
        default="none",
        description="Reported tooth sensitivity level (none, mild, frequent, severe)"
    )
    pain_discomfort: Optional[str] = Field(
        default="none",
        description="Reported pain or discomfort (none, occasional, chewing, constant)"
    )
    gum_bleeding: Optional[str] = Field(
        default="none",
        description="Reported gum bleeding (none, flossing, brushing, spontaneous)"
    )
    teeth_or_gum_changes: Optional[str] = Field(
        default="none",
        description="Reported visible changes in teeth or gums (none, slight, moderate, marked)"
    )
    last_dental_visit: Optional[str] = Field(
        default="6_to_12_months",
        description="Time since last professional dental examination"
    )
    specific_concern: Optional[str] = Field(
        default="",
        description="Any specific self-identified oral health concern or question"
    )
