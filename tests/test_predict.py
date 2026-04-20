import pytest

def test_predict_success(client):
    """Test successful GDP prediction."""
    payload = {
        "gdp": 500.0,
        "inflation": 4.5,
        "population": 1400.0,
        "unemployment": 7.2,
        "interest": 6.0,
        "deficit": 3.5,
        "revenue": 120.0,
        "expenditure": 150.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "predicted_gdp" in data
    assert "future_predictions" in data
    assert len(data["future_predictions"]) == 5
    assert "anomaly" in data
    assert "risk_analysis" in data

def test_predict_invalid_input(client):
    """Test prediction failure with negative values."""
    payload = {
        "gdp": -100.0,  # Invalid
        "inflation": 4.5,
        "population": 1400.0,
        "unemployment": 7.2,
        "interest": 6.0,
        "deficit": 3.5,
        "revenue": 120.0,
        "expenditure": 150.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 400
    assert "cannot be negative" in response.json()["detail"].lower()

def test_historical_data(client):
    """Test the historical data retrieval."""
    response = client.get("/historical")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "historical_data" in data
    assert isinstance(data["historical_data"], list)
