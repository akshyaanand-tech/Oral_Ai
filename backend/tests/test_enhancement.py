"""
Tests for AI dental image enhancement service and endpoint.
"""
import io
import numpy as np
from PIL import Image, ImageFilter
from fastapi.testclient import TestClient

from app.services.enhancement import enhance_dental_image, bytes_to_data_url
from app.services.quality import quality_check
from app.main import app

client = TestClient(app)


def _make_test_image(width=400, height=300, blur=False, dark=False) -> bytes:
    """Generate a test oral-like synthetic image."""
    img = Image.new("RGB", (width, height), (50, 10, 15) if dark else (140, 60, 60))
    arr = np.array(img)

    # Draw simulated teeth
    for i in range(50, width - 50, 35):
        arr[100:200, i:i + 28, :] = (245, 245, 235)  # Enamel
    img = Image.fromarray(arr)

    if blur:
        img = img.filter(ImageFilter.GaussianBlur(radius=3.5))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def test_enhance_dental_image_sharpens_blur():
    """Verify that enhancement improves sharpness and quality of blurry photos."""
    blurry_bytes = _make_test_image(blur=True)
    before_q = quality_check(blurry_bytes)

    enhanced_bytes, before_res, after_res, improvements = enhance_dental_image(blurry_bytes, view="front")

    assert len(enhanced_bytes) > 0
    assert after_res.quality_score >= before_res.quality_score
    assert len(improvements) > 0

    # Ensure enhanced image is valid JPEG with exact same dimensions
    enhanced_img = Image.open(io.BytesIO(enhanced_bytes))
    assert enhanced_img.size == (400, 300)


def test_enhance_dental_image_dark_compensation():
    """Verify enhancement handles dim oral photos."""
    dark_bytes = _make_test_image(dark=True)
    enhanced_bytes, before_res, after_res, improvements = enhance_dental_image(dark_bytes, view="upper")

    assert len(enhanced_bytes) > 0
    enhanced_img = Image.open(io.BytesIO(enhanced_bytes))
    mean_val = np.mean(np.array(enhanced_img))
    dark_val = np.mean(np.array(Image.open(io.BytesIO(dark_bytes))))
    assert mean_val > dark_val  # Brightness lifted


def test_enhance_api_endpoint_success():
    """Test POST /api/enhance-image happy path."""
    img_bytes = _make_test_image(blur=True)
    response = client.post(
        "/api/enhance-image",
        files={"image": ("front_blurry.jpg", img_bytes, "image/jpeg")},
        data={"view": "front"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["view"] == "front"
    assert data["enhanced_image_base64"].startswith("data:image/jpeg;base64,")
    assert "before_quality" in data
    assert "after_quality" in data
    assert len(data["improvements"]) > 0


def test_enhance_api_unsupported_format():
    """Test rejection of unsupported file extension."""
    response = client.post(
        "/api/enhance-image",
        files={"image": ("test.pdf", b"%PDF-1.4...", "application/pdf")},
    )
    assert response.status_code in (415, 422)


def test_bytes_to_data_url_helper():
    data = b"\xff\xd8\xff\xe0test"
    url = bytes_to_data_url(data, "image/jpeg")
    assert url.startswith("data:image/jpeg;base64,")
