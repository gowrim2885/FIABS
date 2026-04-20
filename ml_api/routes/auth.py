import hmac
import hashlib
import base64
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

# Security constants
SECRET_KEY = "FIABS_SUPER_SECRET_KEY"  # In production, use environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Database setup
DB_PATH = "data/users.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL
        )
    """)
    
    # Check if demo users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        demo_users = [
            ("admin", "admin@fiabs.gov", hashlib.sha256("policy123".encode()).hexdigest(), "policy", "Policy Maker"),
            ("analyst", "analyst@fiabs.gov", hashlib.sha256("analyst123".encode()).hexdigest(), "analyst", "Financial Analyst"),
            ("public", "public@fiabs.gov", hashlib.sha256("public123".encode()).hexdigest(), "public", "Public Viewer")
        ]
        cursor.executemany("INSERT INTO users (username, email, password_hash, role, name) VALUES (?, ?, ?, ?, ?)", demo_users)
        conn.commit()
    conn.close()

# Initialize DB on import
init_db()

# Simple JWT Implementation using standard library
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire.timestamp()})
    
    # Header
    header = {"alg": ALGORITHM, "typ": "JWT"}
    header_json = json.dumps(header, separators=(',', ':')).encode()
    header_b64 = base64.urlsafe_b64encode(header_json).decode().replace('=', '')
    
    # Payload
    payload_json = json.dumps(to_encode, separators=(',', ':')).encode()
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode().replace('=', '')
    
    # Signature
    signature_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().replace('=', '')
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

@router.post("/login")
async def login(request: Dict[str, Any] = Body(...)):
    print(f"DEBUG: Login Request Received: {request}")
    username = request.get("username")
    password = request.get("password")
    role = request.get("role")
    
    if not username or not password or not role:
        raise HTTPException(status_code=400, detail="Missing username, password, or role.")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Hash password
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Find user
    cursor.execute(
        "SELECT * FROM users WHERE (username = ? OR email = ?) AND password_hash = ? AND role = ?", 
        (username, username, pwd_hash, role)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials or role mismatch.")

    # Create JWT
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )

    # Determine landing page
    landing = "/frontend/index.html"
    if user["role"] == "public":
        landing = "/frontend/public/public.html"

    # Define permissions
    permissions = []
    if user["role"] == "policy":
        permissions = ["forecast", "insights", "allocation"]
    elif user["role"] == "analyst":
        permissions = ["forecast", "upload", "train", "insights"]
    elif user["role"] == "public":
        permissions = ["view_public_dashboard", "chat"]

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "name": user["name"],
        "landing": landing,
        "permissions": permissions
    }

@router.get("/roles")
def get_roles():
    # Keep compatibility with old frontend if needed
    return {
        "roles": [
            {"id": "policy", "name": "Policy Maker", "landing": "/frontend/index.html"},
            {"id": "analyst", "name": "Analyst", "landing": "/frontend/index.html"},
            {"id": "public", "name": "Public Viewer", "landing": "/frontend/public/public.html"}
        ]
    }
