"""
Unit and Integration Tests for AI-Powered Preventive Oral Health Screening Pipeline.
Tests each service independently and validates the end-to-end POST /api/screen endpoint.
"""

import io
import os
os.environ["MOCK_AI"] = "true"
from PIL import Image, ImageDraw
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ml_output import (
    MLAnalysisOutput,
    MLFindingItem,
    FindingSeverity,
)
from app.schemas.recommendation import CareStep, CarePathway
from app.services.ml_service import analyze_oral_images
from app.services.recommendation_service import generate_recommendations
from app.services.care_plan_service import create_care_pathway
from app.services.cost_service import estimate_costs
from app.services.provider_service import find_providers
from app.services.scoring_service import calculate_score
from app.services.gemini_service import generate_explanation


def _create_synthetic_oral_image(color=(220, 180, 170), width=400, height=300) -> bytes:
    """Helper to generate a valid JPEG in memory."""
    img = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(img)
    # Draw teeth-like white rectangles and pink gum bands
    draw.rectangle([50, 50, 350, 100], fill=(210, 100, 110))  # Gum margin
    draw.rectangle([80, 110, 140, 200], fill=(245, 240, 230))  # Tooth
    draw.rectangle([150, 110, 210, 200], fill=(240, 238, 225)) # Tooth
    draw.rectangle([220, 110, 280, 200], fill=(248, 245, 235)) # Tooth
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


@pytest.fixture
def sample_five_images():
    return {
        "front": _create_synthetic_oral_image(color=(215, 170, 165)),
        "left": _create_synthetic_oral_image(color=(210, 165, 160)),
        "right": _create_synthetic_oral_image(color=(210, 165, 160)),
        "upper": _create_synthetic_oral_image(color=(200, 150, 150)),
        "lower": _create_synthetic_oral_image(color=(200, 150, 150)),
    }


# ── 1. ML Service Tests ──────────────────────────────────────────────────────
def test_ml_service_structure_and_categories(sample_five_images):
    result = analyze_oral_images(sample_five_images)

    assert isinstance(result, MLAnalysisOutput)
    assert len(result.findings) == 4
    assert result.overall_confidence > 0.0

    categories = {f.category for f in result.findings}
    assert categories == {"alignment", "discoloration", "tooth_wear", "gum_appearance"}

    for f in result.findings:
        assert isinstance(f.severity, FindingSeverity)
        assert 0.0 <= f.confidence <= 1.0
        # Check that findings do not use definitive diagnosis words
        f_lower = f.finding.lower()
        assert "diagnosed" not in f_lower
        assert "confirmed" not in f_lower


# ── 2. Recommendation Service Tests ──────────────────────────────────────────
def test_recommendation_service_rule_mappings():
    # Test case: Crowding present -> Orthodontist
    findings_crowding = [
        MLFindingItem(
            category="alignment",
            finding="Possible crowding observed in visible anterior segment",
            severity=FindingSeverity.moderate,
            confidence=0.88,
        ),
        MLFindingItem(
            category="discoloration",
            finding="No notable staining",
            severity=FindingSeverity.none,
            confidence=0.90,
        ),
        MLFindingItem(
            category="tooth_wear",
            finding="No notable wear",
            severity=FindingSeverity.none,
            confidence=0.90,
        ),
        MLFindingItem(
            category="gum_appearance",
            finding="Healthy gingival appearance",
            severity=FindingSeverity.none,
            confidence=0.90,
        ),
    ]
    ml_out = MLAnalysisOutput(
        findings=findings_crowding,
        findings_by_category={f.category: f for f in findings_crowding},
        overall_confidence=0.89,
    )
    recs = generate_recommendations(ml_out)
    assert any("orthodontic" in r.title.lower() or "alignment" in r.title.lower() for r in recs)
    assert any("orthodontist" in r.recommended_specialist.lower() for r in recs)

    # Test case: Discoloration/staining -> General Dentist / Prophylaxis
    findings_staining = [
        MLFindingItem(
            category="alignment",
            finding="Typical alignment",
            severity=FindingSeverity.none,
            confidence=0.90,
        ),
        MLFindingItem(
            category="discoloration",
            finding="Possible visible surface staining observed",
            severity=FindingSeverity.mild,
            confidence=0.85,
        ),
        MLFindingItem(
            category="tooth_wear",
            finding="No notable wear",
            severity=FindingSeverity.none,
            confidence=0.90,
        ),
        MLFindingItem(
            category="gum_appearance",
            finding="Healthy gingival appearance",
            severity=FindingSeverity.none,
            confidence=0.90,
        ),
    ]
    ml_out_stain = MLAnalysisOutput(
        findings=findings_staining,
        findings_by_category={f.category: f for f in findings_staining},
        overall_confidence=0.88,
    )
    recs_stain = generate_recommendations(ml_out_stain)
    assert any("cleaning" in r.action.lower() or "prophylaxis" in r.action.lower() or "stain" in r.action.lower() for r in recs_stain)
    assert any("general dentist" in r.recommended_specialist.lower() for r in recs_stain)


def test_recommendation_service_all_none_defaults_to_preventive():
    findings_clean = [
        MLFindingItem(category=c, finding="No concerns", severity=FindingSeverity.none, confidence=0.95)
        for c in ["alignment", "discoloration", "tooth_wear", "gum_appearance"]
    ]
    ml_out = MLAnalysisOutput(
        findings=findings_clean,
        findings_by_category={f.category: f for f in findings_clean},
        overall_confidence=0.95,
    )
    recs = generate_recommendations(ml_out)
    assert len(recs) >= 1
    assert "preventive" in recs[0].category.lower()
    assert recs[0].recommended_specialist == "General Dentist"


# ── 3. Care Plan Service Tests ───────────────────────────────────────────────
def test_care_plan_synthesis():
    steps = [
        CareStep(
            step_id="step_1",
            title="Orthodontic Evaluation",
            category="alignment",
            action="Orthodontic check",
            urgency="Recommended within 1-3 months",
            recommended_specialist="Orthodontist",
            home_care=["Use floss threaders"],
        ),
        CareStep(
            step_id="step_2",
            title="Dental Prophylaxis",
            category="discoloration",
            action="Stain cleaning",
            urgency="Routine",
            recommended_specialist="General Dentist",
            home_care=["Rinse after coffee"],
        ),
    ]
    pathway = create_care_pathway(steps)
    assert isinstance(pathway, CarePathway)
    assert "Orthodontist" in pathway.recommended_specialists
    assert "General Dentist" in pathway.recommended_specialists
    assert len(pathway.home_care_summary) >= 2
    assert "1 to 2 months" in pathway.recall_recommendation


# ── 4. Cost Service Tests ────────────────────────────────────────────────────
def test_cost_service_ranges_and_currency():
    steps = [
        CareStep(
            step_id="step_1",
            title="Orthodontic Evaluation",
            category="alignment",
            action="Orthodontic check",
            urgency="Routine",
            recommended_specialist="Orthodontist",
            home_care=[],
        )
    ]
    pathway = create_care_pathway(steps)

    # Cost query for location
    city_costs = estimate_costs(pathway, location="Boston")
    assert len(city_costs) >= 1
    for c in city_costs:
        assert c.currency == "INR"
        assert c.min_cost <= c.max_cost
        assert "₹" in c.cost_range
        assert c.indicative is True

    # India PIN query (e.g. Bengaluru 560001)
    in_costs = estimate_costs(pathway, location="560001")
    assert len(in_costs) >= 1
    for c in in_costs:
        assert c.currency == "INR"
        assert "₹" in c.cost_range


# ── 5. Provider Service Tests ────────────────────────────────────────────────
def test_provider_service_by_city_and_pin():
    # Test City Search
    boston_providers = find_providers(location="Boston")
    assert len(boston_providers) > 0
    assert any(p.city.lower() == "boston" for p in boston_providers)
    for p in boston_providers:
        assert p.source in ("fallback_database", "live_api")
        assert p.name
        assert p.specialty

    # Test PIN Search
    blr_providers = find_providers(location="560034")
    assert len(blr_providers) > 0
    assert any("bengaluru" in p.city.lower() or "560034" in str(p.pin_code) for p in blr_providers)

    # Test Unmatched location returns empty list (honest data integrity, no fabricated dentists)
    remote_providers = find_providers(location="NonExistentCity999")
    assert len(remote_providers) == 0


# ── 6. Scoring Service Tests ─────────────────────────────────────────────────
def test_scoring_service_deductions_and_bounds():
    # All marked (worst visible)
    worst_findings = [
        MLFindingItem(category="alignment", finding="f", severity=FindingSeverity.marked, confidence=0.8),
        MLFindingItem(category="discoloration", finding="f", severity=FindingSeverity.marked, confidence=0.8),
        MLFindingItem(category="tooth_wear", finding="f", severity=FindingSeverity.marked, confidence=0.8),
        MLFindingItem(category="gum_appearance", finding="f", severity=FindingSeverity.marked, confidence=0.8),
    ]
    worst_out = MLAnalysisOutput(
        findings=worst_findings,
        findings_by_category={f.category: f for f in worst_findings},
        overall_confidence=0.8,
    )
    score, details = calculate_score(worst_out)
    # Deductions: alignment 15 + discoloration 12 + tooth_wear 15 + gum_appearance 22 = 64
    # Expected: 100 - 64 = 36
    assert score == 36
    assert details.final_score == 36
    assert details.total_deductions == 64

    # All none (best)
    best_findings = [
        MLFindingItem(category=c, finding="f", severity=FindingSeverity.none, confidence=0.9)
        for c in ["alignment", "discoloration", "tooth_wear", "gum_appearance"]
    ]
    best_out = MLAnalysisOutput(
        findings=best_findings,
        findings_by_category={f.category: f for f in best_findings},
        overall_confidence=0.9,
    )
    best_score, best_details = calculate_score(best_out)
    assert best_score == 100
    assert best_details.total_deductions == 0


# ── 7. Gemini Service Tests (Template Fallback) ───────────────────────────────
def test_gemini_service_offline_template():
    findings = [
        MLFindingItem(category="alignment", finding="Possible mild crowding", severity=FindingSeverity.mild, confidence=0.85),
        MLFindingItem(category="discoloration", finding="No notable staining", severity=FindingSeverity.none, confidence=0.9),
        MLFindingItem(category="tooth_wear", finding="No notable wear", severity=FindingSeverity.none, confidence=0.9),
        MLFindingItem(category="gum_appearance", finding="Healthy gums", severity=FindingSeverity.none, confidence=0.9),
    ]
    ml_out = MLAnalysisOutput(
        findings=findings,
        findings_by_category={f.category: f for f in findings},
        overall_confidence=0.88,
    )
    pathway = create_care_pathway([
        CareStep(
            step_id="step_1",
            title="Orthodontic Consultation",
            category="alignment",
            action="Evaluate alignment",
            urgency="Elective",
            recommended_specialist="Orthodontist",
            home_care=["Floss daily"],
        )
    ])

    explanation = generate_explanation(ml_out, score=95, care_pathway=pathway, enabled=True)
    assert isinstance(explanation, str)
    assert len(explanation) > 50
    assert "95/100" in explanation or "95" in explanation


# ── 8. Integration Tests for Endpoints ────────────────────────────────────────
def test_screen_endpoint_e2e(sample_five_images):
    client = TestClient(app)

    files = {
        "front": ("front.jpg", sample_five_images["front"], "image/jpeg"),
        "left": ("left.jpg", sample_five_images["left"], "image/jpeg"),
        "right": ("right.jpg", sample_five_images["right"], "image/jpeg"),
        "upper": ("upper.jpg", sample_five_images["upper"], "image/jpeg"),
        "lower": ("lower.jpg", sample_five_images["lower"], "image/jpeg"),
    }
    data = {
        "location": "Boston",
        "questionnaire": '{"tooth_sensitivity": "none", "last_dental_visit": "6_to_12_months"}',
        "enable_gemini": "false",
    }

    response = client.post("/api/screen", files=files, data=data)
    assert response.status_code == 200

    json_resp = response.json()
    # Validate exact required keys from user specification:
    assert "screening_score" in json_resp
    assert isinstance(json_resp["screening_score"], int)
    assert 0 <= json_resp["screening_score"] <= 100

    assert "findings" in json_resp
    assert isinstance(json_resp["findings"], list)
    assert len(json_resp["findings"]) == 4

    assert "care_pathway" in json_resp
    assert isinstance(json_resp["care_pathway"], list)
    assert len(json_resp["care_pathway"]) >= 1

    assert "providers" in json_resp
    assert isinstance(json_resp["providers"], list)
    assert len(json_resp["providers"]) >= 1

    assert "estimated_costs" in json_resp
    assert isinstance(json_resp["estimated_costs"], list)
    assert len(json_resp["estimated_costs"]) >= 1

    assert "explanation" in json_resp
    assert isinstance(json_resp["explanation"], str)

    assert "disclaimer" in json_resp
    assert "not provide a diagnosis" in json_resp["disclaimer"].lower()


def test_providers_endpoint_get():
    client = TestClient(app)
    response = client.get("/api/providers?city=Boston&limit=3")
    assert response.status_code == 200
    providers = response.json()
    assert isinstance(providers, list)
    assert len(providers) <= 3
    if providers:
        p = providers[0]
        assert "name" in p
        assert "specialty" in p
        assert "address" in p
