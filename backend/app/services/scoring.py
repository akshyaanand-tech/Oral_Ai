"""
Deterministic screening score calculator service.

Derives a preliminary visual screening indicator score (0–100) from
structured findings. The score is calculated deterministically in Python
using an auditable ruleset — the AI never chooses the final score.

IMPORTANT: This score is a PRELIMINARY VISUAL SCREENING INDICATOR only.
It is NOT a medically validated dental diagnostic risk score.
"""

import logging
from app.schemas.analysis import DentalFindings, Severity
from app.schemas.score import ScreeningScore, ScoreBreakdown, CategoryBreakdown

logger = logging.getLogger(__name__)

# Category deduction lookup table based on PRD specifications
DEDUCTION_TABLE: dict[str, dict[Severity, int]] = {
    "alignment": {
        Severity.none: 0,
        Severity.mild: 5,
        Severity.moderate: 10,
        Severity.marked: 15,
        Severity.uncertain: 0,
    },
    "discoloration": {
        Severity.none: 0,
        Severity.mild: 4,
        Severity.moderate: 8,
        Severity.marked: 12,
        Severity.uncertain: 0,
    },
    "tooth_wear": {
        Severity.none: 0,
        Severity.mild: 5,
        Severity.moderate: 10,
        Severity.marked: 15,
        Severity.uncertain: 0,
    },
    "gum_appearance": {
        Severity.none: 0,
        Severity.mild: 9,
        Severity.moderate: 15,
        Severity.marked: 22,
        Severity.uncertain: 0,
    },
}


def calculate_score(findings: DentalFindings) -> ScreeningScore:
    """
    Calculate a deterministic screening score from validated findings.

    Starting score: 100.
    Subtract itemized deductions per category based on observed severity.
    Clamp result between 0 and 100.
    """
    categories = {
        "alignment": findings.alignment,
        "discoloration": findings.discoloration,
        "tooth_wear": findings.tooth_wear,
        "gum_appearance": findings.gum_appearance,
    }

    category_deductions: dict[str, int] = {}
    details: dict[str, CategoryBreakdown] = {}
    total_deductions = 0

    for cat_name, finding in categories.items():
        deduction = DEDUCTION_TABLE.get(cat_name, {}).get(finding.severity, 0)
        category_deductions[cat_name] = deduction
        total_deductions += deduction

        details[cat_name] = CategoryBreakdown(
            severity=finding.severity.value,
            deduction=deduction,
        )

    starting_score = 100
    computed_score = max(0, min(100, starting_score - total_deductions))

    breakdown = ScoreBreakdown(
        starting_score=starting_score,
        alignment=category_deductions.get("alignment", 0),
        discoloration=category_deductions.get("discoloration", 0),
        tooth_wear=category_deductions.get("tooth_wear", 0),
        gum_appearance=category_deductions.get("gum_appearance", 0),
        final_score=computed_score,
        details=details,
    )

    return ScreeningScore(
        score=computed_score,
        score_label="Preliminary Visual Screening Score",
        breakdown=breakdown,
    )
