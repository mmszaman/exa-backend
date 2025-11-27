"""Tests for notification endpoints."""

import pytest


def test_health_check(client):
    """Test health check endpoint returns 200 and ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "time" in response.json()


def test_notify_email_valid(client, valid_email, monkeypatch):
    """Test notify-email with valid email (mocked email send)."""
    # Mock the email service to avoid actual SMTP calls
    async def mock_send_notification_email(email: str):
        return True

    from app.services import email_service
    monkeypatch.setattr(email_service.EmailService, "send_notification_email", mock_send_notification_email)

    response = client.post("/api/notify-email", json={"email": valid_email})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "received" in response.json()["message"]


def test_notify_email_invalid_email(client):
    """Test notify-email with invalid email format."""
    response = client.post("/api/notify-email", json={"email": "not-an-email"})
    assert response.status_code == 422  # Validation error from Pydantic
