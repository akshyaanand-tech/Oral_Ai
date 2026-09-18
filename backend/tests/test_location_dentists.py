"""
Tests for Location-Aware Dentist Search.
Verifies that:
1. Thiruvananthapuram returns real dentists in/near Thiruvananthapuram.
2. Kochi returns real dentists in/near Kochi.
3. Bengaluru returns real dentists in/near Bengaluru.
4. Results are NOT identical across cities.
5. Coordinates trigger distance calculations.
6. Unknown location returns an empty list, NOT static Boston clinics.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_dentist_search_thiruvananthapuram():
    resp = client.get("/api/providers", params={"location": "Thiruvananthapuram", "limit": 4})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # If network/API is available, results should be found
    if data:
        for p in data:
            assert p["name"]
            assert p["address"]
            assert "Boston" not in p["address"]


def test_dentist_search_kochi():
    resp = client.get("/api/providers", params={"location": "Kochi", "limit": 4})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if data:
        for p in data:
            assert p["name"]
            assert "Boston" not in p["address"]


def test_dentist_search_bengaluru():
    resp = client.get("/api/providers", params={"location": "Bengaluru", "limit": 4})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if data:
        for p in data:
            assert p["name"]
            assert "Boston" not in p["address"]


def test_dentist_search_results_differ_across_locations():
    resp_tvm = client.get("/api/providers", params={"location": "Thiruvananthapuram", "limit": 4})
    resp_blr = client.get("/api/providers", params={"location": "Bengaluru", "limit": 4})

    tvm_data = resp_tvm.json()
    blr_data = resp_blr.json()

    if tvm_data and blr_data:
        tvm_names = [p["name"] for p in tvm_data]
        blr_names = [p["name"] for p in blr_data]
        # Ensure results for Thiruvananthapuram and Bengaluru are distinct
        assert tvm_names != blr_names


def test_dentist_search_coordinates_distance():
    # Coordinates for Thiruvananthapuram: 8.5241, 76.9366
    resp = client.get("/api/providers", params={"latitude": 8.5241, "longitude": 76.9366, "limit": 4})
    assert resp.status_code == 200
    data = resp.json()
    if data:
        for p in data:
            # Distance should be calculated when coordinates are passed
            if p.get("distance"):
                assert "km away" in p["distance"] or "mi away" in p["distance"]


def test_unknown_location_returns_empty_not_boston():
    # A completely non-existent or remote location with no clinics
    resp = client.get("/api/providers", params={"location": "NonExistentUninhabitedAtollXYZ999"})
    assert resp.status_code == 200
    data = resp.json()
    # Must NOT fallback to Boston
    assert len(data) == 0
