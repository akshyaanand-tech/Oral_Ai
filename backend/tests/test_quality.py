"""
Tests for technical image quality service and endpoint.
"""
import io
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from app.services.quality import quality_check
from app.main import app

client = TestClient(app)


def _make_image(width=400, height=400, color=(180, 180, 180), pattern=True) -> bytes:
    """Helper to generate an in-memory JPEG image."""
    img = Image.new("RGB", (width, height), color)
    if pattern:
        # Draw high-contrast grid lines to ensure sharp edges for the Laplacian test
        arr = np.array(img)
        for i in range(0, width, 20):
            arr[:, i, :] = (20, 20, 20)
        for j in range(0, height, 20):
            arr[j, :, :] = (240, 240, 240)
        img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_quality_check_valid_image():
    img_bytes = _make_image(width=400, height=400, color=(150, 150, 150), pattern=True)
    result = quality_check(img_bytes)
    assert result.passed is True
    assert result.quality_score > 0.7
    assert len(result.issues) == 0


def test_quality_check_too_small():
    img_bytes = _make_image(width=100, height=100)
    result = quality_check(img_bytes)
    assert result.passed is False
    assert any("too small" in issue.lower() for issue in result.issues)


def test_quality_check_too_dark():
    # Mean pixel brightness < 30
    img_bytes = _make_image(width=300, height=300, color=(10, 10, 10), pattern=False)
    result = quality_check(img_bytes)
    assert result.passed is False
    assert any("dark" in issue.lower() for issue in result.issues)


def test_quality_check_corrupt_data():
    result = quality_check(b"not-an-image-data-string")
    assert result.passed is False
    assert result.quality_score == 0.0
    assert any("corrupted" in issue.lower() or "decoded" in issue.lower() for issue in result.issues)


def test_quality_endpoint():
    img_bytes = _make_image(width=300, height=300, pattern=True)
    response = client.post(
        "/api/quality-check",
        files={"image": ("test.jpg", img_bytes, "image/jpeg")},
        data={"view": "front"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "passed" in data
    assert "quality_score" in data
    assert "issues" in data
