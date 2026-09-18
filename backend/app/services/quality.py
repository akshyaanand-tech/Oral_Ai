"""
Two-Stage Image Quality Assessment Service.

Evaluates technical image usability across multiple visual signals:
- Sharpness & focus (Laplacian variance)
- Resolution & aspect ratio
- Illumination & brightness distribution
- Contrast dynamics
- Composite usability scoring

Stage 1: Basic validation (decodability, dimensions, corruptions).
Stage 2: Technical assessment pre- and post-enhancement.
"""

import io
import logging
from typing import List, Tuple
from PIL import Image, ImageStat
import numpy as np

from app.schemas.quality import QualityResult

logger = logging.getLogger(__name__)

# ── Thresholds ───────────────────────────────────────────────────────────────
MIN_WIDTH = 200
MIN_HEIGHT = 200
MAX_WIDTH = 8000
MAX_HEIGHT = 8000

BRIGHTNESS_TOO_DARK = 30       # Fatal dark threshold (mean pixel < 30)
BRIGHTNESS_DIM = 65            # Sub-optimal lighting
BRIGHTNESS_HIGH = 215          # Sub-optimal overexposure
BRIGHTNESS_TOO_BRIGHT = 240    # Fatal overexposed threshold (mean pixel > 240)

LOW_CONTRAST_STD = 18.0        # Pixel standard deviation < 18 indicates washed-out image
SEVERE_BLUR_THRESHOLD = 8.0    # Severe unrecoverable out-of-focus blur
MODERATE_BLUR_THRESHOLD = 20.0 # Sub-optimal sharpness (can be recovered via enhancement)
PASS_SCORE_THRESHOLD = 0.65    # Minimum combined quality score to pass


def _laplacian_variance(gray: np.ndarray) -> float:
    """Estimate image edge sharpness via 2D discrete Laplacian variance."""
    if gray.shape[0] < 3 or gray.shape[1] < 3:
        return 0.0
    kernel = (
        gray[:-2, 1:-1]
        + gray[2:, 1:-1]
        + gray[1:-1, :-2]
        + gray[1:-1, 2:]
        - 4 * gray[1:-1, 1:-1]
    )
    return float(np.var(kernel))


def evaluate_single_image_quality(image_bytes: bytes) -> QualityResult:
    """
    Evaluate multi-signal technical quality on a static image without enhancement.
    Checks decodability, dimensions, lighting, contrast, and edge sharpness.
    """
    issues: List[str] = []
    penalties: List[float] = []

    # 1. Decode check
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img.load()
    except Exception as exc:
        logger.warning("Image decode failed: %s", exc)
        return QualityResult(
            passed=False,
            quality_score=0.0,
            original_quality_score=0.0,
            enhanced_quality_score=0.0,
            enhanced=False,
            issues=["Image could not be decoded or is corrupted"]
        )

    width, height = img.size

    # 2. Dimensions check (Stage 1 basic validation)
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        issues.append(f"Image is too small ({width}×{height}px; minimum {MIN_WIDTH}×{MIN_HEIGHT}px)")
        penalties.append(0.50)
    elif width > MAX_WIDTH or height > MAX_HEIGHT:
        issues.append(f"Image dimensions exceed maximum allowed ({MAX_WIDTH}×{MAX_HEIGHT}px)")
        penalties.append(0.30)

    # 3. Brightness & Exposure check
    stat = ImageStat.Stat(img)
    mean_brightness = sum(stat.mean) / 3.0
    gray = img.convert("L")
    gray_array = np.array(gray, dtype=np.float32)
    contrast_std = float(np.std(gray_array))

    if mean_brightness < BRIGHTNESS_TOO_DARK:
        issues.append("Image is too dark — please ensure adequate lighting")
        penalties.append(0.40)
    elif mean_brightness < BRIGHTNESS_DIM:
        penalties.append(0.15)

    if mean_brightness > BRIGHTNESS_TOO_BRIGHT:
        issues.append("Image is overexposed or too bright")
        penalties.append(0.35)
    elif mean_brightness > BRIGHTNESS_HIGH:
        penalties.append(0.10)

    # 4. Contrast dynamics check
    if contrast_std < LOW_CONTRAST_STD:
        penalties.append(0.15)

    # 5. Multi-signal Blur & Sharpness check
    laplacian_var = _laplacian_variance(gray_array)

    if laplacian_var < SEVERE_BLUR_THRESHOLD:
        issues.append("Image appears too blurry — please hold the camera steady")
        penalties.append(0.40)
    elif laplacian_var < MODERATE_BLUR_THRESHOLD:
        # Moderate blur: mild penalty rather than fatal
        penalties.append(0.20)

    # 6. Compute multi-signal composite quality score
    total_penalty = sum(penalties)
    quality_score = max(0.0, min(1.0, round(1.0 - total_penalty, 2)))
    passed = len(issues) == 0 and quality_score >= PASS_SCORE_THRESHOLD

    return QualityResult(
        passed=passed,
        quality_score=quality_score,
        original_quality_score=quality_score,
        enhanced_quality_score=quality_score,
        enhanced=False,
        issues=issues,
    )


def quality_check(image_bytes: bytes, auto_enhance_if_needed: bool = True) -> QualityResult:
    """
    Two-Stage Technical Quality Check Pipeline.

    Stage 1: Basic validation (decode, minimum/maximum dimensions).
             If Stage 1 fails (e.g. image < 200px or corrupt), rejection is immediate.
    Stage 2: For images passing basic validation, evaluate technical quality.
             If sub-optimal or moderately blurry, apply automatic enhancement and re-evaluate.
    """
    from app.services.enhancement import enhance_dental_image

    # Stage 1: Basic validation & initial evaluation
    orig_eval = evaluate_single_image_quality(image_bytes)

    # Basic validation failures (corrupt image or dimensions violation) cannot be enhanced
    if any("too small" in iss.lower() or "exceed" in iss.lower() or "corrupt" in iss.lower() or "decode" in iss.lower() for iss in orig_eval.issues):
        return orig_eval

    # If original image easily passes with top marks and no quality issues,
    # enhancement is not needed:
    if orig_eval.passed and orig_eval.quality_score >= 0.85:
        return QualityResult(
            passed=True,
            quality_score=orig_eval.quality_score,
            original_quality_score=orig_eval.quality_score,
            enhanced_quality_score=orig_eval.quality_score,
            enhanced=False,
            issues=[]
        )

    if not auto_enhance_if_needed:
        return orig_eval

    # Stage 2: Apply automatic enhancement to improve image
    try:
        enhanced_bytes, before_q, after_q, improvements = enhance_dental_image(image_bytes)

        # Check if enhancement achieved usability threshold
        if after_q.passed and after_q.quality_score >= PASS_SCORE_THRESHOLD:
            logger.info("Image successfully enhanced: score %.2f -> %.2f",
                        orig_eval.quality_score, after_q.quality_score)
            return QualityResult(
                passed=True,
                quality_score=after_q.quality_score,
                original_quality_score=orig_eval.quality_score,
                enhanced_quality_score=after_q.quality_score,
                enhanced=True,
                issues=[]
            )
        else:
            enhanced_issues: List[str] = []
            if after_q.quality_score < PASS_SCORE_THRESHOLD or any("blurry" in i.lower() for i in after_q.issues):
                enhanced_issues.append("Image remains too blurry after automatic enhancement — please hold the camera steady and retake")
            for iss in after_q.issues:
                if "blurry" not in iss.lower() and iss not in enhanced_issues:
                    enhanced_issues.append(iss)

            logger.warning("Image remains sub-optimal after enhancement (score: %.2f)", after_q.quality_score)
            return QualityResult(
                passed=False,
                quality_score=after_q.quality_score,
                original_quality_score=orig_eval.quality_score,
                enhanced_quality_score=after_q.quality_score,
                enhanced=True,
                issues=enhanced_issues
            )
    except Exception as exc:
        logger.error("Enhancement during quality check failed: %s", exc)
        return orig_eval
