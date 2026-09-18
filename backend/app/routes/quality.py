"""
Image technical quality check endpoint.
POST /api/quality-check
"""

import os
import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status

from app.schemas.quality import QualityResult
from app.services.quality import quality_check

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Quality"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_SIZE_BYTES = int(os.getenv("MAX_IMAGE_SIZE_BYTES", str(10 * 1024 * 1024)))


@router.post(
    "/api/quality-check",
    response_model=QualityResult,
    summary="Check technical quality of a single dental image",
    description="Evaluates brightness, blur, dimensions, and decodability before full submission.",
)
async def check_single_image(
    image: UploadFile = File(..., description="Image file to check"),
    view: Optional[str] = Form(None, description="Optional view name (front, left, right, upper, lower)"),
):
    if not image or not image.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No image uploaded.",
        )

    filename_lower = image.filename.lower()
    if not any(filename_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported format '{image.filename}'. Accepted formats: JPEG, PNG, WEBP.",
        )

    if image.content_type and image.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content-type '{image.content_type}'.",
        )

    data = await image.read()
    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded image is empty.",
        )

    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds maximum allowed size of {MAX_SIZE_BYTES // (1024 * 1024)} MB.",
        )

    result = quality_check(data)
    logger.info("Quality check for '%s' (view=%s): passed=%s score=%.2f",
                image.filename, view, result.passed, result.quality_score)
    return result
