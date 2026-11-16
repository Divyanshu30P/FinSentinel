import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"

def test_demo_user_login():
    res = client.post("/api/auth/login", json={
        "email": settings.DEMO_USER_EMAIL,
        "password": settings.DEMO_USER_PASSWORD
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["is_demo"] is True

def test_user_registration_and_isolation():
    uid = str(uuid.uuid4())[:8]
    # Register user A
    email_a = f"user_a_{uid}@test.com"
    res_a = client.post("/api/auth/register", json={
        "email": email_a,
        "username": "User A",
        "password": "PasswordA123!"
    })
    assert res_a.status_code == 200
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register user B
    email_b = f"user_b_{uid}@test.com"
    res_b = client.post("/api/auth/register", json={
        "email": email_b,
        "username": "User B",
        "password": "PasswordB123!"
    })
    assert res_b.status_code == 200
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A analyzes a phishing message
    scan_res = client.post(
        "/api/fraud/analyze-message",
        json={"message_text": "Your bank account has been blocked. Call 9876543210 immediately."},
        headers=headers_a
    )
    assert scan_res.status_code == 200
    analysis_id = scan_res.json()["id"]

    # User A can see it in history
    hist_a = client.get("/api/fraud/history", headers=headers_a)
    assert any(item["id"] == analysis_id for item in hist_a.json())

    # User B CANNOT see User A's analysis (Data Isolation Check)
    hist_b = client.get("/api/fraud/history", headers=headers_b)
    assert not any(item["id"] == analysis_id for item in hist_b.json())

def test_collect_request_api():
    res = client.post("/api/fraud/analyze-collect-request", json={
        "sender_name": "Scam Merchant",
        "sender_vpa": "lottery.win@ybl",
        "requested_amount": 4999.0,
        "request_description": "Enter UPI PIN to receive money",
        "expected_request": False,
        "sender_known": False,
        "associated_message": "Tap approve"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["risk_category"] == "HIGH"
    assert data["risk_score"] >= 75
    assert len(data["detected_indicators"]) > 0

def test_dashboard_summary_api():
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_analyses" in data
    assert "recent_analyses" in data
    assert "recent_alerts" in data
