from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/auth", tags=["auth"])

DEMO_USERS = {
    "policy": {
        "password": "policy123",
        "name": "Policy Maker",
        "landing": "/frontend/index.html",
        "permissions": ["forecast", "insights", "allocation"],
    },
    "analyst": {
        "password": "analyst123",
        "name": "Analyst",
        "landing": "/frontend/index.html",
        "permissions": ["forecast", "upload", "train", "insights"],
    },
    "public": {
        "password": "public123",
        "name": "Public User",
        "landing": "/frontend/public/public.html",
        "permissions": ["view_public_dashboard", "chat"],
    },
}


class LoginRequest(BaseModel):
    role: str
    password: str


@router.get("/roles")
def get_roles():
    return {
        "roles": [
            {"id": role, "name": profile["name"], "landing": profile["landing"]}
            for role, profile in DEMO_USERS.items()
        ]
    }


@router.post("/login")
def login(request: LoginRequest):
    role = request.role.lower()
    profile = DEMO_USERS.get(role)
    if not profile or request.password != profile["password"]:
        raise HTTPException(status_code=401, detail="Invalid role or password.")

    return {
        "role": role,
        "name": profile["name"],
        "landing": profile["landing"],
        "permissions": profile["permissions"],
    }
