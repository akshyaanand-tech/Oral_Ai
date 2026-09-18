"""
AI & Computational Vision Dental Image Enhancement Service.

Improves clarity, sharpness, exposure, and illumination of smartphone dental photos
while strictly preserving composition, natural anatomy, tooth morphology, and color fidelity.
Does NOT generate artificial dental structures or hallucinate clinical features.
"""

import io
import base64
import logging
from typing import Tuple, List, Optional
from PIL import Image, ImageEnhance, ImageFilter, ImageStat
import numpy as np

from app.schemas.quality import QualityResult

logger = logging.getLogger(__name__)


def enhance_image(image_bytes: bytes) -> bytes:
    """
    Standard enhancement entry point:
    enhance_image(image_bytes) -> enhanced_image_bytes

    Applies deterministic multi-stage enhancement:
    - exposure & brightness balance
    - gamma correction for shadowed arches
    - local contrast enhancement
    - multi-scale unsharp masking & edge sharpening
    - mucosal color normalization
    """
    enhanced_bytes, _, _, _ = enhance_dental_image(image_bytes, view="front")
    return enhanced_bytes


def _apply_gamma(img: Image.Image, gamma: float = 1.0) -> Image.Image:
    """Apply gamma correction via lookup table to reveal shadowed oral structures."""
    if abs(gamma - 1.0) < 0.02:
        return img
    inv_gamma = 1.0 / max(gamma, 0.1)
    lut = [min(255, int(((i / 255.0) ** inv_gamma) * 255 + 0.5)) for i in range(256)] * 3
    return img.point(lut)


def _apply_local_contrast(img: Image.Image, radius: int = 15, amount: float = 0.35) -> Image.Image:
    """
    Local contrast enhancement (unsharp mask on low-frequency components).
    Increases visibility of tooth margins and gingival contours without global clipping.
    """
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
    arr_orig = np.array(img, dtype=np.float32)
    arr_blur = np.array(blurred, dtype=np.float32)
    diff = arr_orig - arr_blur
    enhanced_arr = np.clip(arr_orig + diff * amount, 0, 255).astype(np.uint8)
    return Image.fromarray(enhanced_arr)


def enhance_dental_image(
    image_bytes: bytes,
    view: str = "front",
) -> Tuple[bytes, QualityResult, QualityResult, List[str]]:
    """
    Enhance an oral photograph to reduce blur, improve sharpness, balance lighting,
    and expand local contrast while strictly preserving dimensions and anatomy.

    Returns:
        tuple of (enhanced_image_bytes, before_quality, after_quality, improvements_list)
    """
    from app.services.quality import evaluate_single_image_quality

    # 1. Baseline technical quality evaluation
    before_quality = evaluate_single_image_quality(image_bytes)

    # 2. Decode original image
    try:
        orig_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        orig_img.load()
    except Exception as exc:
        logger.error("Failed to decode image for enhancement: %s", exc)
        raise ValueError("Image could not be decoded.") from exc

    orig_width, orig_height = orig_img.size
    improvements: List[str] = []
    current_img = orig_img

    # 3. Exposure & Brightness Analysis
    stat = ImageStat.Stat(current_img)
    mean_brightness = sum(stat.mean) / 3.0

    # Adaptive brightness compensation
    if mean_brightness < 90:
        boost_factor = min(1.65, max(1.15, 120.0 / max(mean_brightness, 25.0)))
        current_img = ImageEnhance.Brightness(current_img).enhance(boost_factor)
        improvements.append(f"Adjusted brightness (+{int((boost_factor - 1.0) * 100)}%) for shadowed oral regions")
    elif mean_brightness > 210:
        dim_factor = max(0.80, 190.0 / mean_brightness)
        current_img = ImageEnhance.Brightness(current_img).enhance(dim_factor)
        improvements.append("Reduced over-exposure to recover tooth enamel surface detail")

    # 4. Gamma Correction for deep dental shadows
    if mean_brightness < 110:
        current_img = _apply_gamma(current_img, gamma=1.25)
        improvements.append("Applied gamma curve adjustment to reveal interior arch structures")

    # 5. Local & Global Contrast Enhancement
    current_img = _apply_local_contrast(current_img, radius=12, amount=0.30)
    current_img = ImageEnhance.Contrast(current_img).enhance(1.22)
    improvements.append("Enhanced local contrast to clearly delineate tooth boundaries and gingival margins")

    # 6. Multi-scale Edge Sharpening & Unsharp Masking
    # Stage A: Edge unsharp mask
    current_img = current_img.filter(ImageFilter.UnsharpMask(radius=2.0, percent=175, threshold=2))
    # Stage B: Fine micro-structure sharpness tuning
    current_img = ImageEnhance.Sharpness(current_img).enhance(1.50)
    improvements.append("Applied edge deblurring and sharpness enhancement to clarify fine enamel contours")

    # 7. Natural Mucosal & Enamel Color Tone Normalization
    current_img = ImageEnhance.Color(current_img).enhance(1.03)
    improvements.append("Balanced natural mucosal and dental color tones without artificial discoloration")

    # 8. Strict composition and dimension preservation
    assert current_img.size == (orig_width, orig_height), "Dimensions must match exactly"
    improvements.append("Preserved 100% original composition, aspect ratio, and framing (no crop or shift)")

    # 9. Encode output to high-quality JPEG
    out_buf = io.BytesIO()
    current_img.save(out_buf, format="JPEG", quality=95, subsampling=0)
    enhanced_bytes = out_buf.getvalue()

    # 10. Evaluate quality post-enhancement
    after_quality = evaluate_single_image_quality(enhanced_bytes)

    # Format quality metrics with enhancement tracking
    before_quality.original_quality_score = before_quality.quality_score
    before_quality.enhanced_quality_score = after_quality.quality_score
    before_quality.enhanced = False

    after_quality.original_quality_score = before_quality.quality_score
    after_quality.enhanced_quality_score = after_quality.quality_score
    after_quality.enhanced = True

    logger.info(
        "Enhanced image '%s': quality %.2f -> %.2f (passed: %s -> %s)",
        view, before_quality.quality_score, after_quality.quality_score,
        before_quality.passed, after_quality.passed
    )

    return enhanced_bytes, before_quality, after_quality, improvements


def bytes_to_data_url(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Convert binary image bytes to a browser-ready base64 data URL."""
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"
