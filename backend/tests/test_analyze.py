"""
Integration tests for POST /api/analyze endpoint.
"""
import io
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _make_image(width=400, height=400) -> bytes:
    """Helper to generate a valid test image."""
    img = Image.new("RGB", (width, height), (180, 180, 180))
    arr = np.array(img)
    for i in range(0, width, 25):
        arr[:, i, :] = (20, 20, 20)
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_analyze_full_pipeline_mock_ai():
    img_data = _make_image()
    files = {
        "front": ("front.jpg", img_data, "image/jpeg"),
        "left":  ("left.jpg",  img_data, "image/jpeg"),
        "right": ("right.jpg", img_data, "image/jpeg"),
        "upper": ("upper.jpg", img_data, "image/jpeg"),
        "lower": ("lower.jpg", img_data, "image/jpeg"),
    }

    response = client.post("/api/analyze", files=files)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "completed"
    assert "screening_id" in data
    assert data["screening_id"].startswith("scr_")
    assert "score" in data
    assert 0 <= data["score"] <= 100
    assert data["score_label"] == "Preliminary Visual Screening Score"

    # Verify 4 finding categories
    assert "findings" in data
    findings = data["findings"]
    for cat in ["alignment", "discoloration", "tooth_wear", "gum_appearance"]:
        assert cat in findings
        assert "finding" in findings[cat]
        assert "severity" in findings[cat]
        assert "confidence" in findings[cat]

    # Verify score breakdown
    assert "score_breakdown" in data
    sb = data["score_breakdown"]
    assert sb["starting_score"] == 100
    assert "alignment" in sb
    assert "discoloration" in sb
    assert "tooth_wear" in sb
    assert "gum_appearance" in sb
    assert "final_score" in sb
    assert sb["final_score"] == data["score"]

    # Verify recommendation & disclaimer
    assert "recommendation" in data
    assert len(data["recommendation"]) > 10
    assert "disclaimer" in data
    assert "preliminary visual screening" in data["disclaimer"].lower()


def test_analyze_missing_image_returns_422():
    img_data = _make_image()
    files = {
        "front": ("front.jpg", img_data, "image/jpeg"),
        "left":  ("left.jpg",  img_data, "image/jpeg"),
        "right": ("right.jpg", img_data, "image/jpeg"),
        "upper": ("upper.jpg", img_data, "image/jpeg"),
        # 'lower' missing
    }
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 422


def test_analyze_unsupported_format_returns_415():
    img_data = _make_image()
    files = {
        "front": ("front.txt", b"plain text", "text/plain"),
        "left":  ("left.jpg",  img_data, "image/jpeg"),
        "right": ("right.jpg", img_data, "image/jpeg"),
        "upper": ("upper.jpg", img_data, "image/jpeg"),
        "lower": ("lower.jpg", img_data, "image/jpeg"),
    }
    response = client.post("/api/analyze", files=files)
    assert response.status_code in (415, 422)
