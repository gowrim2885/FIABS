import pytest

def test_login_success(client):
    """Test successful login for all roles."""
    roles = [
        ("admin", "policy123", "policy"),
        ("analyst", "analyst123", "analyst"),
        ("public", "public123", "public")
    ]
    for username, password, role in roles:
        response = client.post("/auth/login", json={
            "username": username,
            "password": password,
            "role": role
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] == role
        assert "permissions" in data

def test_login_invalid_credentials(client):
    """Test login failure with wrong password."""
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "wrongpassword",
        "role": "policy"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials or role mismatch."

def test_login_missing_fields(client):
    """Test login failure with missing fields."""
    # Missing role
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "policy123"
    })
    assert response.status_code == 400
    assert "Missing" in response.json()["detail"]

def test_roles_endpoint(client):
    """Test the /auth/roles helper endpoint."""
    response = client.get("/auth/roles")
    assert response.status_code == 200
    data = response.json()
    assert "roles" in data
    assert len(data["roles"]) == 3
