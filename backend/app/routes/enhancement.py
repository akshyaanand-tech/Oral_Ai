"""
AI Dental Image Enhancement endpoint.
POST /api/enhance-image
"""

import os
import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from fastapi.responses import Response

from app.schemas.enhancement import EnhanceImageResponse
from app.services.enhancement import enhance_dental_image, bytes_to_data_url

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Enhancement"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_SIZE_BYTES = int(os.getenv("MAX_IMAGE_SIZE_BYTES", str(10 * 1024 * 1024)))


@router.post(
    "/api/enhance-image",
    response_model=EnhanceImageResponse,
    summary="Enhance oral photo quality using AI & vision filtering",
    description=(
        "Reduces blur, enhances edge sharpness, balances lighting & contrast while "
        "preserving natural anatomy, colors, composition, and dimensions."
    ),
)
async def enhance_single_image(
    image: UploadFile = File(..., description="Dental image file to enhance"),
    view: Optional[str] = Form("front", description="Dental view angle (front, left, right, upper, lower)"),
):
    if not image or not image.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No image provided for enhancement.",
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

    try:
        enhanced_bytes, before_q, after_q, improvements = enhance_dental_image(data, view=view or "front")
    except Exception as exc:
        logger.error("Enhancement failed for image %s: %s", image.filename, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image enhancement could not be completed: {str(exc)}",
        )

    data_url = bytes_to_data_url(enhanced_bytes, mime_type="image/jpeg")

    return EnhanceImageResponse(
        success=True,
        view=view or "front",
        enhanced_image_base64=data_url,
        before_quality=before_q,
        after_quality=after_q,
        improvements=improvements,
    )
