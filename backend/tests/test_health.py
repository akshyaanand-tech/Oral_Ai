"""
Tests for GET /health endpoint.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "mock_ai" in data
    assert data["version"] == "1.0.0"
