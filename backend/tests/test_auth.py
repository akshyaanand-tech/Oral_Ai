"""
Tests for backend Authentication routes and services.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.db import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_register_and_login_flow():
    # 1. Register a new user
    email = "testuser_auth@example.com"
    reg_payload = {
        "name": "Dr. Testing",
        "email": email,
        "password": "SecurePassword123!",
    }
    r = client.post("/api/auth/register", json=reg_payload)
    assert r.status_code in (201, 400)
    if r.status_code == 201:
        data = r.json()
        assert data["user"]["email"] == email
        assert data["user"]["name"] == "Dr. Testing"
        assert "token" in data

    # 2. Duplicate registration fails with 400
    r_dup = client.post("/api/auth/register", json=reg_payload)
    assert r_dup.status_code == 400

    # 3. Invalid credentials fail
    r_bad = client.post("/api/auth/login", json={"email": email, "password": "WrongPassword999"})
    assert r_bad.status_code == 401

    # 4. Valid login succeeds
    r_login = client.post("/api/auth/login", json={"email": email, "password": "SecurePassword123!"})
    assert r_login.status_code == 200
    login_data = r_login.json()
    token = login_data["token"]
    assert token

    # 5. Fetch profile with token
    r_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r_me.status_code == 200
    assert r_me.json()["email"] == email


def test_register_short_password_fails():
    r = client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice_short@example.com", "password": "short"}
    )
    assert r.status_code == 422


def test_forgot_password_endpoint():
    r = client.post("/api/auth/forgot-password", json={"email": "anyone@example.com"})
    assert r.status_code == 200
    assert "dispatched" in r.json()["message"]
