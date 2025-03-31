from pydantic_settings import BaseSettings

class CoreConfig(BaseSettings):
    database_url: str = "postgresql://user:pass@db:5432/db"  # Changed to container port 5432
    redis_url: str = "redis://redis:6379"
    upload_dir: str = "/uploads"
    
    class Config:
        env_file = ".env"
        env_prefix = "CORE_"