import pytest

def test_allocate_logic(client):
    """Test the MCDM resource allocation logic."""
    payload = {
        "departments": [
            {"name": "Education", "roi": 80, "impact": 90, "risk": 20},
            {"name": "Defense", "roi": 40, "impact": 70, "risk": 50},
            {"name": "Healthcare", "roi": 85, "impact": 95, "risk": 15}
        ]
    }
    response = client.post("/allocate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "ranking" in data
    
    # Healthcare should be #1 based on the formula: 0.4*ROI + 0.3*Impact - 0.3*Risk
    # Healthcare: 0.4*85 + 0.3*95 - 0.3*15 = 34 + 28.5 - 4.5 = 58
    # Education: 0.4*80 + 0.3*90 - 0.3*20 = 32 + 27 - 6 = 53
    # Defense: 0.4*40 + 0.3*70 - 0.3*50 = 16 + 21 - 15 = 22
    
    assert data["ranking"][0]["name"] == "Healthcare"
    assert data["ranking"][1]["name"] == "Education"
    assert data["ranking"][2]["name"] == "Defense"

def test_allocate_empty_data(client):
    """Test allocation with no departments."""
    response = client.post("/allocate", json={"departments": []})
    assert response.status_code == 200
    assert response.json()["ranking"] == []
