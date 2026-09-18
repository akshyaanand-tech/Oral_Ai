"""
Tests for Screenings, Tracking, Comparison, and Referral endpoints.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.services.db import init_db

client = TestClient(app)


def setup_module():
    init_db()


def test_list_screenings_returns_baseline():
    response = client.get("/api/screenings")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any("screening_id" in s for s in data)


def test_get_screening_by_id():
    # Fetch list first
    list_res = client.get("/api/screenings")
    assert list_res.status_code == 200
    scr_id = list_res.json()[0]["screening_id"]

    # Fetch individual
    res = client.get(f"/api/screenings/{scr_id}")
    assert res.status_code == 200
    record = res.json()
    assert record["screening_id"] == scr_id
    assert "findings" in record
    assert "score" in record


def test_get_screening_not_found():
    response = client.get("/api/screenings/non_existent_id")
    assert response.status_code == 404


def test_compare_screenings():
    # Fetch existing screening
    list_res = client.get("/api/screenings")
    items = list_res.json()
    if len(items) < 2:
        # Create another screening record by calling /api/analyze
        from tests.test_analyze import _make_image
        b = _make_image()
        files = {v: (f"{v}.jpg", b, "image/jpeg") for v in ["front", "left", "right", "upper", "lower"]}
        client.post("/api/analyze", files=files)
        items = client.get("/api/screenings").json()

    prev_id = items[-1]["screening_id"]
    curr_id = items[0]["screening_id"]

    comp_res = client.post(
        "/api/screenings/compare",
        json={"previous_screening_id": prev_id, "current_screening_id": curr_id}
    )
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert "overall" in comp_data
    assert "previous_score" in comp_data["overall"]
    assert "current_score" in comp_data["overall"]
    assert "change" in comp_data["overall"]
    assert "categories" in comp_data
    for cat in ["alignment", "discoloration", "tooth_wear", "gum_appearance"]:
        assert cat in comp_data["categories"]
        assert "change" in comp_data["categories"][cat]
        # Never say disease progressed
        assert "disease progressed" not in comp_data["categories"][cat]["change"].lower()


def test_dentist_html_report_endpoint():
    list_res = client.get("/api/screenings")
    scr_id = list_res.json()[0]["screening_id"]

    res = client.get(f"/api/screenings/{scr_id}/report")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Dentist Summary" in res.text or "OralAI" in res.text
    assert scr_id in res.text


def test_dental_providers_list():
    res = client.get("/api/providers")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert "name" in data[0]
    assert "specialty" in data[0]


def test_dental_referral_request():
    payload = {
        "screening_id": "scr_test123",
        "provider_id": "prov_101",
        "patient_name": "Jane Doe",
        "patient_email": "jane@example.com",
        "patient_phone": "555-0199",
        "preferred_time": "Morning",
        "notes": "Interested in preventive cleaning and check-up",
    }
    res = client.post("/api/referrals", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "inquiry_id" in data
    assert data["status"] == "pending_provider_confirmation"
    assert data["screening_id"] == "scr_test123"
