from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_health_check():
    """Ensure the User Service is responding."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "User Service API v1 is fully healthy"}

def test_register_user_validation():
    """
    Test validation of Pydantic models by sending incomplete data.
    Ensures that empty payloads are rejected safely with a 422 Unprocessable Entity.
    """
    response = client.post("/api/v1/users/register", json={"email": "not_an_email"})
    assert response.status_code == 422 

def test_unauthorized_access():
    """Ensure protected routes reject missing JWT tokens."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
