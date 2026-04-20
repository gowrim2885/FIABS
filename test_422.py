import httpx
import json

def test_login_422():
    url = "http://127.0.0.1:8000/auth/login"
    # Intentionally missing 'role' to trigger 422
    payload = {
        "username": "admin",
        "password": "policy123"
    }
    
    print(f"Testing 422 with payload: {json.dumps(payload)}")
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login_422()
