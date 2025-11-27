"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Provides a test client for API endpoints."""
    return TestClient(app)


@pytest.fixture
def valid_email():
    """Provides a valid test email."""
    return "test@example.com"
