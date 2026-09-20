"""
Authentication routes.

Replaces the previously-planned Rust auth service (localhost:8080) with a
simple Python implementation on the same FastAPI backend, so the whole
app runs from a single service.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Header, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel

from src.db.mongo_client import db

router = APIRouter(prefix="/api")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 1 day

# In-memory set of issued API tokens (simple gate for /create_user, /login).
# Fine for a single-process dev/demo app; swap for a persisted store if you
# scale to multiple backend instances.
_valid_api_tokens: set[str] = set()

users_collection = db["users"]


class AuthRequest(BaseModel):
    username: str
    password: str


def _check_api_token(x_api_token: str) -> None:
    if x_api_token not in _valid_api_tokens:
        raise HTTPException(status_code=401, detail="Invalid or missing API token")


@router.post("/init")
async def init_session():
    """Issue a short-lived API token the frontend must send on auth calls."""
    token = str(uuid.uuid4())
    _valid_api_tokens.add(token)
    return {"api_token": token}


@router.post("/create_user")
async def create_user_route(
    body: AuthRequest,
    x_api_token: str = Header(..., alias="X-API-TOKEN"),
):
    """Create a new user with a bcrypt-hashed password in MongoDB."""
    _check_api_token(x_api_token)

    existing = await users_collection.find_one({"username": body.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(body.password)
    await users_collection.insert_one({
        "username": body.username,
        "password_hash": hashed_password,
        "created_at": datetime.now(timezone.utc),
    })
    return {"status": "created"}


@router.post("/login")
async def login_route(
    body: AuthRequest,
    x_api_token: str = Header(..., alias="X-API-TOKEN"),
):
    """Verify credentials and return a JWT on success."""
    _check_api_token(x_api_token)

    user = await users_collection.find_one({"username": body.username})
    if not user or not pwd_context.verify(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    payload = {
        "sub": body.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"jwt": token}