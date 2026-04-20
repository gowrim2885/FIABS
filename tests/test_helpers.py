import sys
import os
import json
import base64

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_api.routes.auth import create_access_token, SECRET_KEY

def test_create_access_token():
    """Unit test for custom JWT implementation."""
    data = {"sub": "testuser", "role": "admin"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    parts = token.split(".")
    assert len(parts) == 3
    
    # Decode payload
    payload_b64 = parts[1]
    # Add padding if needed
    missing_padding = len(payload_b64) % 4
    if missing_padding:
        payload_b64 += '=' * (4 - missing_padding)
        
    decoded_payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
    assert decoded_payload["sub"] == "testuser"
    assert decoded_payload["role"] == "admin"
    assert "exp" in decoded_payload
