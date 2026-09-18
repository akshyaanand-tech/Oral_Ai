"""
Care Plan Service.

Synthesizes rule-based recommendations into a cohesive, structured Care Pathway.
Aggregates recommended dental specialists, daily home-care routines,
and suggested professional follow-up recall schedule.
"""

from typing import List
from app.schemas.recommendation import CareStep, CarePathway


def create_care_pathway(steps: List[CareStep]) -> CarePathway:
    """
    Synthesizes a list of care steps into a unified CarePathway.
    """
    if not steps:
        steps = [
            CareStep(
                step_id="step_1",
                title="Routine Preventive Dental Maintenance",
                category="preventive",
                action="Biannual dental check-up and prophylaxis",
                urgency="Routine (within 6 months)",
                recommended_specialist="General Dentist",
                home_care=["Brush twice daily", "Floss daily"],
            )
        ]

    # Collect distinct recommended specialists preserving order
    specialists = []
    for s in steps:
        if s.recommended_specialist and s.recommended_specialist not in specialists:
            specialists.append(s.recommended_specialist)

    # Collect distinct home care guidance points
    home_care_all = []
    for s in steps:
        for tip in s.home_care:
            if tip not in home_care_all:
                home_care_all.append(tip)

    # Determine recall recommendation based on urgency of steps
    has_urgent = any("1-2 weeks" in s.urgency or "2-3 weeks" in s.urgency for s in steps)
    has_moderate = any("month" in s.urgency for s in steps)

    if has_urgent:
        recall = "Prompt evaluation recommended within 1 to 2 weeks"
        summary = "Based on your screening findings, prompt professional evaluation is advised to address noticeable visible indicators."
    elif has_moderate:
        recall = "Schedule consultation within 1 to 2 months"
        summary = "Mild to moderate visible indicators suggest scheduling a professional visit in the coming month."
    else:
        recall = "Routine biannual check-up (within 6 months)"
        summary = "No immediate urgent concerns detected. Maintain excellent home care and schedule routine preventive visits."

    return CarePathway(
        steps=steps,
        summary=summary,
        recommended_specialists=specialists,
        home_care_summary=home_care_all[:6],  # top actionable tips
        recall_recommendation=recall,
    )
