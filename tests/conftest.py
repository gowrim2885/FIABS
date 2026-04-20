import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_api.app import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "policy123",
        "role": "policy"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "role": "policy"}
