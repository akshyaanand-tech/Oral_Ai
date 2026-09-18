"""
Deterministic Scoring Service.

Implements transparent, reproducible calculation of the Preliminary Visual Screening Score (0–100).
The score is strictly a screening / risk indicator and NOT a clinical dental diagnosis.

Scoring Rules Architecture:
  ML Findings + Confidence
       ↓
  Deterministic Scoring Table
       ↓
  Screening Score (0–100)
"""

import logging
from typing import Dict, Tuple
from app.schemas.ml_output import MLAnalysisOutput, FindingSeverity
from app.schemas.screening import ScoreDetails

logger = logging.getLogger(__name__)

# Category deduction lookup table
DEDUCTION_TABLE: Dict[str, Dict[FindingSeverity, int]] = {
    "alignment": {
        FindingSeverity.none: 0,
        FindingSeverity.mild: 5,
        FindingSeverity.moderate: 10,
        FindingSeverity.marked: 15,
        FindingSeverity.uncertain: 0,
    },
    "discoloration": {
        FindingSeverity.none: 0,
        FindingSeverity.mild: 4,
        FindingSeverity.moderate: 8,
        FindingSeverity.marked: 12,
        FindingSeverity.uncertain: 0,
    },
    "tooth_wear": {
        FindingSeverity.none: 0,
        FindingSeverity.mild: 5,
        FindingSeverity.moderate: 10,
        FindingSeverity.marked: 15,
        FindingSeverity.uncertain: 0,
    },
    "gum_appearance": {
        FindingSeverity.none: 0,
        FindingSeverity.mild: 9,
        FindingSeverity.moderate: 15,
        FindingSeverity.marked: 22,
        FindingSeverity.uncertain: 0,
    },
}


def calculate_score(ml_output: MLAnalysisOutput) -> Tuple[int, ScoreDetails]:
    """
    Calculate deterministic screening score from validated ML findings.

    Starting score: 100.
    Subtract itemized deductions per category based on observed severity.
    Clamp result between 0 and 100.
    Returns (final_score, ScoreDetails).
    """
    findings_map = ml_output.findings_by_category or {f.category: f for f in ml_output.findings}

    category_deductions: Dict[str, int] = {}
    total_deductions = 0

    for category, deductions_by_sev in DEDUCTION_TABLE.items():
        finding = findings_map.get(category)
        if finding:
            sev = finding.severity
            deduction = deductions_by_sev.get(sev, 0)
        else:
            deduction = 0

        category_deductions[category] = deduction
        total_deductions += deduction

    starting_score = 100
    final_score = max(0, min(100, starting_score - total_deductions))

    score_details = ScoreDetails(
        starting_score=starting_score,
        total_deductions=total_deductions,
        final_score=final_score,
        category_deductions=category_deductions,
    )

    logger.info("Screening score calculated: %d (deductions: %s)", final_score, category_deductions)
    return final_score, score_details
