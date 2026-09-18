"""
Tests for Two-Stage Quality Pipeline and Automatic Enhancement.
"""
import io
import numpy as np
from PIL import Image, ImageFilter
from app.services.quality import quality_check, evaluate_single_image_quality
from app.services.enhancement import enhance_image


def _generate_synthetic_photo(width=400, height=300, blur_radius=0.0, dark=False) -> bytes:
    """Generate in-memory test image with dental-like structure."""
    img = Image.new("RGB", (width, height), (40, 15, 20) if dark else (145, 65, 65))
    arr = np.array(img)
    # Add high-contrast tooth-like bars
    for x in range(60, width - 60, 40):
        arr[90:210, x:x + 30, :] = (240, 240, 230)
    img = Image.fromarray(arr)

    if blur_radius > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def test_quality_score_enhancement_not_needed():
    """Clear, high-sharpness image does not need enhancement (enhanced=False)."""
    img_bytes = _generate_synthetic_photo(width=400, height=300, blur_radius=0.0)
    res = quality_check(img_bytes)
    assert res.passed is True
    assert res.enhanced is False
    assert res.quality_score >= 0.85
    assert res.original_quality_score == res.quality_score
    assert len(res.issues) == 0


def test_quality_score_moderately_blurry_recovers_after_enhancement():
    """Moderately blurry image is enhanced and passes quality check."""
    blurry_bytes = _generate_synthetic_photo(width=400, height=300, blur_radius=2.5)
    res = quality_check(blurry_bytes)
    assert res.enhanced is True
    assert res.passed is True
    assert res.enhanced_quality_score >= res.original_quality_score


def test_quality_score_severely_blurry_fails_with_retake_advice():
    """Severely blurry image cannot be recovered and fails with retake advice."""
    severe_blurry = _generate_synthetic_photo(width=400, height=300, blur_radius=18.0)
    res = quality_check(severe_blurry)
    assert res.passed is False
    assert any("blurry" in iss.lower() or "retake" in iss.lower() for iss in res.issues)


def test_enhance_image_function():
    """Test the canonical enhance_image(image_bytes) entry point."""
    img_bytes = _generate_synthetic_photo(width=400, height=300, blur_radius=2.0)
    enhanced = enhance_image(img_bytes)
    assert len(enhanced) > 0
    img = Image.open(io.BytesIO(enhanced))
    assert img.size == (400, 300)
