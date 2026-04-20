import httpx
import json

def test_login():
    url = "http://127.0.0.1:8001/auth/login"
    payload = {
        "username": "admin",
        "password": "policy123",
        "role": "policy"
    }
    
    print(f"Testing login with payload: {json.dumps(payload)}")
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
