from pydantic_settings import BaseSettings

class HealthConfig(BaseSettings):
    check_interval: int = 30  # seconds
    timeout: int = 5  # seconds
    
    class Config:
        env_file = ".env"
        env_prefix = "HEALTH_"