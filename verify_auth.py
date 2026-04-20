import httpx
import json

def test_login():
    url = "http://127.0.0.1:8000/auth/login"
    
    # Test valid login (Policy Maker)
    payload = {
        "username": "admin",
        "password": "policy123",
        "role": "policy"
    }
    
    print(f"Testing login with: {payload}")
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Success: Login works!")
        else:
            print("❌ Error: Login failed.")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_login()
