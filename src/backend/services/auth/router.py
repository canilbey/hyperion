from fastapi import APIRouter, Depends, HTTPException, status
from backend.models import UserCreate, UserLogin, Token
from backend.services.auth.service import AuthService
from backend.services.core.init_service import get_db
from typing import Any
import logging

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)

async def get_auth_service():
    """Get or create auth service with database connection"""
    try:
        db = get_db()
        if not db.is_connected:
            await db.connect()
        return AuthService(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )

@router.post("/signup", response_model=Any)
async def signup(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    logger.info(f"[POST /api/auth/signup] Signup called: email={user.email}")
    try:
        created = await service.register_user(user.email, user.password)
        logger.info(f"[POST /api/auth/signup] Success: {created}")
        return created
    except ValueError as e:
        logger.error(f"[POST /api/auth/signup] ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[POST /api/auth/signup] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(user: UserLogin, service: AuthService = Depends(get_auth_service)):
    logger.info(f"[POST /api/auth/login] Login called: email={user.email}")
    try:
        auth = await service.authenticate_user(user.email, user.password)
        if not auth:
            logger.error(f"[POST /api/auth/login] Invalid credentials for email={user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        token = await service.generate_jwt(auth["id"], auth["roles"])
        logger.info(f"[POST /api/auth/login] Success: token generated for user_id={auth['id']}")
        return Token(access_token=token, expires_in=1800)
    except Exception as e:
        logger.error(f"[POST /api/auth/login] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        ) 