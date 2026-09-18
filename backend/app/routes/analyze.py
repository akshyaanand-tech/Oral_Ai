"""
POST /api/analyze

Accepts five dental images and optional patient questionnaire responses.
Executes the complete preventive screening pipeline:
  Upload → Validate → Automatic Enhancement → Multi-Signal Quality Check →
  [Retake if unusable] → Gemini Vision AI → Structured Findings →
  Deterministic 0-100 Score → Personalized Guidance → SQLite Persistence →
  Dentist-Ready Report
"""

import os
import json
import logging
from typing import Dict, Optional, List

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse

from app.services.quality import quality_check
from app.services.enhancement import enhance_dental_image
from app.services.gemini import analyze_images
from app.services.scoring import calculate_score
from app.services.guidance import generate_personalized_guidance
from app.services.report import generate_report
from app.services.db import save_screening
from app.schemas.retake import RetakeResponse, RetakeItem

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Screening"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIZE_BYTES = int(os.getenv("MAX_IMAGE_SIZE_BYTES", str(10 * 1024 * 1024)))  # 10 MB
IMAGE_VIEWS = ["front", "left", "right", "upper", "lower"]


async def _read_and_validate(view: str, upload: UploadFile) -> bytes:
    """Read an UploadFile and enforce format and size constraints."""
    if upload is None or not upload.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Image for view '{view}' is missing.",
        )

    filename_lower = upload.filename.lower()
    if not any(filename_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file format for '{view}': '{upload.filename}'. "
                f"Accepted formats: JPEG, PNG, WEBP."
            ),
        )

    if upload.content_type and upload.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported content-type for '{view}': '{upload.content_type}'. "
                f"Accepted types: image/jpeg, image/png, image/webp."
            ),
        )

    data = await upload.read()

    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Image for view '{view}' is empty.",
        )

    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Image '{view}' exceeds maximum allowed size of "
                f"{MAX_SIZE_BYTES // (1024 * 1024)} MB."
            ),
        )

    return data


@router.post(
    "/api/analyze",
    summary="Submit five dental images for preliminary visual screening",
    response_description=(
        "Structured preliminary visual screening report. "
        "NOT a medical diagnosis. Score is a visual indicator only."
    ),
)
async def analyze(
    front: UploadFile = File(..., description="Front view dental photograph"),
    left:  UploadFile = File(..., description="Left side dental photograph"),
    right: UploadFile = File(..., description="Right side dental photograph"),
    upper: UploadFile = File(..., description="Upper arch dental photograph"),
    lower: UploadFile = File(..., description="Lower arch dental photograph"),
    questionnaire: Optional[str] = Form(None, description="Optional JSON-encoded questionnaire answers"),
):
    """
    ## Preliminary Oral Health Screening

    Submit five dental images for a visual screening evaluation.
    Optional patient questionnaire context is preserved for guidance and report context,
    strictly separate from deterministic visual AI scoring.

    **Disclaimer:** This is NOT a dental diagnosis. Results are based on visual
    observations only and should be discussed with a qualified dental professional.
    """
    # ── 0. Parse optional questionnaire ──────────────────────────────────────
    questionnaire_dict: Optional[dict] = None
    if questionnaire:
        try:
            questionnaire_dict = json.loads(questionnaire)
        except Exception as q_err:
            logger.warning("Could not parse questionnaire JSON: %s", q_err)

    # ── 1. Read & validate uploads ───────────────────────────────────────────
    uploads = {
        "front": front,
        "left": left,
        "right": right,
        "upper": upper,
        "lower": lower,
    }
    original_images: Dict[str, bytes] = {}
    enhanced_images: Dict[str, bytes] = {}
    views_metadata: Dict[str, dict] = {}

    for view, upload in uploads.items():
        original_images[view] = await _read_and_validate(view, upload)

    logger.info("All 5 views uploaded and validated (sizes: %s)",
                {v: len(b) for v, b in original_images.items()})

    # ── 2. Automatic Enhancement & Two-Stage Quality Assessment ───────────────
    retake_items: List[RetakeItem] = []
    quality_warnings: List[str] = []

    for view, orig_bytes in original_images.items():
        # Evaluate quality using two-stage pipeline (auto-enhances sub-optimal images)
        q_result = quality_check(orig_bytes, auto_enhance_if_needed=True)

        if q_result.enhanced:
            # Re-generate or fetch enhanced bytes for model analysis
            try:
                enhanced_bytes, _, _, improvements = enhance_dental_image(orig_bytes, view=view)
                enhanced_images[view] = enhanced_bytes
            except Exception as enh_err:
                logger.warning("Enhancement byte retrieval failed for '%s': %s", view, enh_err)
                enhanced_images[view] = orig_bytes
        else:
            enhanced_images[view] = orig_bytes

        views_metadata[view] = {
            "passed": q_result.passed,
            "quality_score": q_result.quality_score,
            "original_quality_score": q_result.original_quality_score,
            "enhanced_quality_score": q_result.enhanced_quality_score,
            "enhanced": q_result.enhanced,
            "issues": q_result.issues,
        }

        if not q_result.passed:
            reason = (
                q_result.issues[0]
                if q_result.issues
                else f"Image for {view} view remains sub-optimal after automatic enhancement. Please retake with better lighting."
            )
            retake_items.append(RetakeItem(view=view, reason=reason))
            quality_warnings.append(f"{view.capitalize()} view: {reason}")

    # If any image remains unusable after enhancement, return structured retake response
    if retake_items:
        logger.warning("Screening aborted — %d view(s) require retake: %s",
                       len(retake_items), [r.view for r in retake_items])
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "retake_required",
                "retake": [r.model_dump() for r in retake_items],
                "message": "One or more images could not be made technically usable. Please retake the indicated views."
            }
        )

    # ── 3. AI visual analysis (uses enhanced images for optimal clarity) ──────
    try:
        findings = analyze_images(enhanced_images)
    except ValueError as exc:
        logger.error("AI analysis returned invalid output: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI analysis returned an unexpected structure. Please try again.",
        ) from exc
    except RuntimeError as exc:
        logger.error("AI service error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during AI analysis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during visual analysis.",
        ) from exc

    # ── 4. Deterministic scoring ─────────────────────────────────────────────
    score_result = calculate_score(findings)
    logger.info("Screening score: %d (%s)", score_result.score, score_result.score_label)

    # ── 5. Personalized preventive guidance ──────────────────────────────────
    guidance = generate_personalized_guidance(findings, questionnaire_dict)

    # ── 6. Assemble complete dentist-ready report ─────────────────────────────
    report = generate_report(
        findings=findings,
        score_result=score_result,
        quality_issues=quality_warnings or None,
        questionnaire=questionnaire_dict,
        guidance=guidance,
        views_metadata=views_metadata,
    )

    # ── 7. Persist to SQLite for longitudinal tracking ────────────────────────
    save_screening(report["screening_id"], report, questionnaire_dict)

    return report
