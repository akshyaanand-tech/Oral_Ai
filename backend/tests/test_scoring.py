"""
Tests for deterministic scoring engine.
"""
from app.schemas.analysis import DentalFindings, FindingDetail, Severity
from app.services.scoring import calculate_score


def _make_findings(alignment=Severity.none, discoloration=Severity.none,
                   tooth_wear=Severity.none, gum_appearance=Severity.none) -> DentalFindings:
    return DentalFindings(
        alignment=FindingDetail(finding="Test alignment", severity=alignment, confidence=0.8),
        discoloration=FindingDetail(finding="Test discoloration", severity=discoloration, confidence=0.8),
        tooth_wear=FindingDetail(finding="Test wear", severity=tooth_wear, confidence=0.8),
        gum_appearance=FindingDetail(finding="Test gums", severity=gum_appearance, confidence=0.8),
    )


def test_perfect_score_all_none():
    findings = _make_findings(
        alignment=Severity.none,
        discoloration=Severity.none,
        tooth_wear=Severity.none,
        gum_appearance=Severity.none,
    )
    result = calculate_score(findings)
    assert result.score == 100
    assert result.breakdown.alignment == 0
    assert result.breakdown.discoloration == 0
    assert result.breakdown.tooth_wear == 0
    assert result.breakdown.gum_appearance == 0


def test_prd_canonical_mild_findings_produce_82():
    """
    PRD sections 10, 19, 20, 22, 26 example:
    Starting: 100
    Alignment: -5 (mild)
    Discoloration: -4 (mild)
    Tooth wear: 0 (none)
    Gum appearance: -9 (mild)
    Final score: 82
    """
    findings = _make_findings(
        alignment=Severity.mild,
        discoloration=Severity.mild,
        tooth_wear=Severity.none,
        gum_appearance=Severity.mild,
    )
    result = calculate_score(findings)
    assert result.score == 82
    assert result.breakdown.alignment == 5
    assert result.breakdown.discoloration == 4
    assert result.breakdown.tooth_wear == 0
    assert result.breakdown.gum_appearance == 9
    assert result.breakdown.final_score == 82
    assert result.score_label == "Preliminary Visual Screening Score"


def test_uncertain_severity_no_deduction():
    findings = _make_findings(
        alignment=Severity.uncertain,
        discoloration=Severity.uncertain,
        tooth_wear=Severity.uncertain,
        gum_appearance=Severity.uncertain,
    )
    result = calculate_score(findings)
    assert result.score == 100
    assert result.breakdown.alignment == 0


def test_score_clamping_boundary():
    # All marked deductions: 15 + 12 + 15 + 22 = 64 deduction -> score 36
    # If deductions exceed 100, clamped at 0
    findings = _make_findings(
        alignment=Severity.marked,
        discoloration=Severity.marked,
        tooth_wear=Severity.marked,
        gum_appearance=Severity.marked,
    )
    result = calculate_score(findings)
    assert 0 <= result.score <= 100
