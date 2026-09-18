"""
Tests for Retake Response when image quality check fails.
"""
from fastapi.testclient import TestClient
from PIL import Image, ImageFilter
import io
import numpy as np
from app.main import app

client = TestClient(app)


def _make_clear_image():
    arr = np.full((300, 300, 3), 150, dtype=np.uint8)
    for i in range(0, 300, 20):
        arr[:, i] = 0
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "JPEG")
    return buf.getvalue()


def _make_severe_blur_image():
    arr = np.full((300, 300, 3), 150, dtype=np.uint8)
    for i in range(0, 300, 20):
        arr[:, i] = 0
    img = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(radius=25.0))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    return buf.getvalue()


def test_analyze_retake_required_on_severe_blur():
    clear_b = _make_clear_image()
    severe_b = _make_severe_blur_image()

    files = {
        "front": ("front.jpg", clear_b, "image/jpeg"),
        "left": ("left.jpg", clear_b, "image/jpeg"),
        "right": ("right.jpg", severe_b, "image/jpeg"),  # Right view is severely blurry
        "upper": ("upper.jpg", clear_b, "image/jpeg"),
        "lower": ("lower.jpg", clear_b, "image/jpeg"),
    }

    response = client.post("/api/analyze", files=files)
    assert response.status_code == 422
    data = response.json()
    assert data.get("status") == "retake_required"
    assert "retake" in data
    assert any(item["view"] == "right" for item in data["retake"])
    assert any("blurry" in item["reason"].lower() for item in data["retake"])
