from typing import Optional, List
from uuid import UUID, uuid4
from backend.models import UserCreate, UserLogin, UserInDB, Role
from backend.services.auth.utils import hash_password, verify_password, create_jwt
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db):
        self.db = db

    async def register_user(self, email: str, password: str) -> dict:
        try:
            # Check if user exists
            existing = await self.db.fetch_one(
                "SELECT id FROM users WHERE email = :email",
                {"email": email}
            )
            if existing:
                raise ValueError("User already exists")

            # Hash password
            hashed = hash_password(password)
            user_id = uuid4()

            # Start transaction
            async with self.db.transaction():
                # Insert user
                await self.db.execute(
                    """
                    INSERT INTO users (id, email, hashed_password, is_active)
                    VALUES (:id, :email, :hashed_password, TRUE)
                    """,
                    {"id": str(user_id), "email": email, "hashed_password": hashed}
                )

                # Get default role
                role = await self.db.fetch_one(
                    "SELECT id, name FROM roles WHERE name = :name",
                    {"name": Role.USER.value}
                )
                
                if not role:
                    logger.error("Default role 'user' not found in database")
                    raise ValueError("System configuration error: default role not found")

                # Assign role
                await self.db.execute(
                    """
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (:user_id, :role_id)
                    """,
                    {"user_id": str(user_id), "role_id": role["id"]}
                )

            return {
                "id": str(user_id),
                "email": email,
                "roles": [Role.USER]
            }

        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            raise ValueError(f"Registration failed: {str(e)}")

    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        try:
            user = await self.db.fetch_one(
                """
                SELECT id, email, hashed_password, is_active
                FROM users
                WHERE email = :email
                """,
                {"email": email}
            )

            if not user or not user["is_active"]:
                return None

            if not verify_password(password, user["hashed_password"]):
                return None

            # Fetch roles
            roles = await self.db.fetch_all(
                """
                SELECT r.name
                FROM roles r
                JOIN user_roles ur ON ur.role_id = r.id
                WHERE ur.user_id = :user_id
                """,
                {"user_id": str(user["id"])}
            )

            role_list = [Role(role["name"]) for role in roles]
            return {
                "id": user["id"],
                "email": user["email"],
                "roles": role_list
            }

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return None

    async def generate_jwt(self, user_id: UUID, roles: List[Role]) -> str:
        try:
            return create_jwt(user_id, roles)
        except Exception as e:
            logger.error(f"JWT generation failed: {str(e)}")
            raise ValueError("Token generation failed")

    async def request_password_reset(self, email: str) -> None:
        """Initiate password reset process."""
        pass

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset user password using a valid token."""
        pass

    async def update_profile(self, user_id: UUID, profile_data: dict) -> dict:
        """Update user profile fields."""
        pass

    async def assign_role(self, user_id: UUID, role_name: str) -> None:
        """Assign a role to a user."""
        pass 