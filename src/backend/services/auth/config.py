import os

class AuthConfig:
    JWT_SECRET: str = os.getenv("JWT_SECRET", "changeme-super-secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_MINUTES: int = int(os.getenv("JWT_EXPIRY_MINUTES", "30"))
    PASSWORD_HASH_ALGORITHM: str = os.getenv("PASSWORD_HASH_ALGORITHM", "bcrypt") 