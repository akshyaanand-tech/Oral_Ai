"""
POST /api/screen

Main screening endpoint for the AI-Powered Preventive Oral Health Screening & Monitoring system.
Coordinates the layered, decoupled architecture:
  1. 5 Oral Images Upload & Validation
  2. Technical Quality Assessment & Auto-Enhancement
  3. ML Image Analysis (Visual Findings & Confidence)
  4. Recommendation Engine (Rule-based Care Steps)
  5. Care Plan Service (Structured Care Pathway & Recall)
  6. Cost Estimation Service (Indicative Ranges from costs.json)
  7. Provider Search Service (Nearby Dental Practices by City / PIN Code)
  8. Deterministic Scoring Service (0–100 Screening Score)
  9. Optional Gemini Explanation Layer (Educational summary with template fallback)

CRITICAL SAFETY & SYSTEM RULES:
- Results are preliminary visual screenings, NOT medical diagnoses.
- External APIs are strictly optional enhancements; the core pipeline works 100% offline.
- Provider ratings/reviews never alter medical recommendations or screening score.
"""

import os
import json
import logging
import uuid
from typing import Optional, Dict

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas.screening import ScreeningResponse
from app.services.quality import quality_check
from app.services.enhancement import enhance_dental_image
from app.services.ml_service import analyze_oral_images
from app.services.recommendation_service import generate_recommendations
from app.services.care_plan_service import create_care_pathway
from app.services.cost_service import estimate_costs
from app.services.provider_service import find_providers
from app.services.scoring_service import calculate_score
from app.services.gemini_service import generate_explanation
from app.services.db import save_screening

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Screening"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIZE_BYTES = int(os.getenv("MAX_IMAGE_SIZE_BYTES", str(10 * 1024 * 1024)))  # 10 MB


async def _validate_and_read(view: str, upload: UploadFile) -> bytes:
    """Validate uploaded image file format and read bytes."""
    if upload is None or not upload.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Image for view '{view}' is missing.",
        )

    filename_lower = upload.filename.lower()
    if not any(filename_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported format for '{view}': {upload.filename}. Accepted: JPEG, PNG, WEBP.",
        )

    if upload.content_type and upload.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content-type for '{view}': {upload.content_type}.",
        )

    data = await upload.read()
    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Image for '{view}' is empty.",
        )

    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image for '{view}' exceeds size limit ({MAX_SIZE_BYTES // (1024 * 1024)} MB).",
        )

    return data


@router.post(
    "/api/screen",
    response_model=ScreeningResponse,
    summary="Screen five oral images and generate report with care pathway, costs, and providers",
    response_description="Preliminary visual screening report. Disclaimer: Not a medical diagnosis.",
)
async def screen_oral_health(
    front: UploadFile = File(..., description="Front view dental photograph"),
    left: UploadFile = File(..., description="Left side dental photograph"),
    right: UploadFile = File(..., description="Right side dental photograph"),
    upper: UploadFile = File(..., description="Upper arch dental photograph"),
    lower: UploadFile = File(..., description="Lower arch dental photograph"),
    location: Optional[str] = Form(None, description="City name or Postal/PIN code (e.g. 'Boston', '560001')"),
    questionnaire: Optional[str] = Form(None, description="Optional JSON-encoded patient questionnaire"),
    enable_gemini: Optional[bool] = Form(True, description="Whether to include optional Gemini explanation"),
):
    """
    ## AI-Powered Preventive Oral Health Screening

    Input:
      - 5 guided oral images (front, left, right, upper, lower)
      - City / PIN code (no GPS required)
      - Optional patient questionnaire answers

    Layered Architecture:
      ML Analysis -> Recommendations -> Care Pathway -> Costs & Providers -> Scoring -> Gemini Explanation
    """
    screening_id = f"scr_{uuid.uuid4().hex[:8]}"
    logger.info("Starting screening %s with location: %s", screening_id, location)

    # 0. Parse optional questionnaire
    questionnaire_dict: Optional[dict] = None
    if questionnaire:
        try:
            questionnaire_dict = json.loads(questionnaire)
        except Exception as q_err:
            logger.warning("Could not parse questionnaire JSON: %s", q_err)

    # 1. Read & validate 5 image uploads
    uploads = {"front": front, "left": left, "right": right, "upper": upper, "lower": lower}
    original_images: Dict[str, bytes] = {}
    enhanced_images: Dict[str, bytes] = {}
    quality_issues: list = []

    for view, upload in uploads.items():
        original_images[view] = await _validate_and_read(view, upload)

    # 2. Quality check & automatic enhancement
    for view, orig_bytes in original_images.items():
        q_result = quality_check(orig_bytes, auto_enhance_if_needed=True)
        if q_result.enhanced:
            try:
                enh_bytes, _, _, _ = enhance_dental_image(orig_bytes, view=view)
                enhanced_images[view] = enh_bytes
            except Exception:
                enhanced_images[view] = orig_bytes
        else:
            enhanced_images[view] = orig_bytes

        if not q_result.passed:
            quality_issues.extend(q_result.issues or [f"Low clarity in {view} view"])

    # 3. ML Image Analysis (detects alignment, discoloration, tooth_wear, gum_appearance)
    ml_output = analyze_oral_images(enhanced_images)

    # 4. Recommendation Engine (pure Python rule-based logic)
    care_steps = generate_recommendations(ml_output, questionnaire_dict)

    # 5. Care Plan Service (synthesizes structured Care Pathway)
    care_pathway = create_care_pathway(care_steps)

    # 6. Cost Estimation Service (indicative ranges from costs.json with external API hook)
    estimated_costs = estimate_costs(care_pathway, location=location)

    # 7. Provider Search Service (uses City / PIN code; live API with providers.json fallback)
    primary_specialist = care_pathway.recommended_specialists[0] if care_pathway.recommended_specialists else None
    providers = find_providers(location=location, specialty=primary_specialist, limit=5)

    # 8. Deterministic Scoring Service (0–100 Screening Score)
    screening_score, score_details = calculate_score(ml_output)

    # 9. Optional Gemini Explanation Layer (plain-language summary; template fallback on offline)
    explanation = generate_explanation(
        ml_output=ml_output,
        score=screening_score,
        care_pathway=care_pathway,
        enabled=bool(enable_gemini),
    )

    # 10. Assemble and return final response
    resp = ScreeningResponse(
        screening_score=screening_score,
        findings=ml_output.findings,
        care_pathway=care_pathway.steps,
        providers=providers,
        estimated_costs=estimated_costs,
        explanation=explanation,
        disclaimer="This is a screening tool and does not provide a diagnosis.",
        score_details=score_details,
        screening_id=screening_id,
        metadata={
            "location_queried": location,
            "quality_issues": quality_issues if quality_issues else None,
            "overall_confidence": ml_output.overall_confidence,
            "analyzed_views": ml_output.analyzed_views,
        }
    )

    # Persist screening record to SQLite for dentist report generation & referrals
    try:
        report_dict = resp.model_dump()
        report_dict["score"] = screening_score
        report_dict["score_label"] = (
            score_details.get("score_label", "Preliminary Visual Screening Score")
            if isinstance(score_details, dict)
            else "Preliminary Visual Screening Score"
        )
        report_dict["recommendation"] = care_pathway.summary
        save_screening(screening_id, report_dict, questionnaire_dict)
        logger.info("Saved screening %s to database", screening_id)
    except Exception as exc:
        logger.warning("Failed to save screening %s to db: %s", screening_id, exc)

    return resp
