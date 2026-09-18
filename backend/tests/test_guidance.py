"""
Tests for Personalized Preventive Guidance generation.
"""
from app.schemas.analysis import DentalFindings, FindingDetail, Severity
from app.services.guidance import generate_personalized_guidance


def _sample_findings(align=Severity.none, disc=Severity.none, wear=Severity.none, gum=Severity.none):
    return DentalFindings(
        alignment=FindingDetail(finding="Alignment check", severity=align, confidence=0.8),
        discoloration=FindingDetail(finding="Discoloration check", severity=disc, confidence=0.8),
        tooth_wear=FindingDetail(finding="Tooth wear check", severity=wear, confidence=0.8),
        gum_appearance=FindingDetail(finding="Gum appearance check", severity=gum, confidence=0.8),
    )


def test_guidance_all_healthy():
    findings = _sample_findings()
    res = generate_personalized_guidance(findings)
    assert "category_guidance" in res
    assert "lifestyle_tips" in res
    assert len(res["lifestyle_tips"]) > 0
    # Cautious non-prescriptive wording
    for text in res["category_guidance"].values():
        assert "prescribe" not in text.lower()
        assert "diagnose" not in text.lower()


def test_guidance_with_indicators_and_questionnaire():
    findings = _sample_findings(
        disc=Severity.mild,
        gum=Severity.moderate,
    )
    questionnaire = {
        "tooth_sensitivity": "frequent",
        "pain_discomfort": "occasional",
        "gum_bleeding": "brushing",
        "teeth_or_gum_changes": "mild",
        "last_dental_visit": "1_to_2_years",
        "specific_concern": "Visible yellowing on lower teeth"
    }

    res = generate_personalized_guidance(findings, questionnaire)
    assert len(res["user_reported_notes"]) > 0
    # Ensure user reported context is explicitly labeled
    for note in res["user_reported_notes"]:
        assert "user-reported" in note.lower()

    assert "discoloration" in res["category_guidance"]
    assert "dental professional" in res["category_guidance"]["discoloration"].lower()
