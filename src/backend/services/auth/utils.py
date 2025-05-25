import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID
from backend.services.auth.config import AuthConfig
from backend.models import Role

# Password hashing

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# JWT utilities

def create_jwt(user_id: UUID, roles: List[Role], expires_minutes: int = None) -> str:
    if expires_minutes is None:
        expires_minutes = AuthConfig.JWT_EXPIRY_MINUTES
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(user_id),
        "roles": [role.value for role in roles],
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, AuthConfig.JWT_SECRET, algorithm=AuthConfig.JWT_ALGORITHM)

def decode_jwt(token: str) -> dict:
    return jwt.decode(token, AuthConfig.JWT_SECRET, algorithms=[AuthConfig.JWT_ALGORITHM]) 