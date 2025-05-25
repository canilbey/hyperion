from pydantic_settings import BaseSettings

class CoreConfig(BaseSettings):
    database_url: str = "postgresql://hyperion:hyperion123@db:5432/hyperion"
    redis_url: str = "redis://redis:6379"
    upload_dir: str = "/uploads"
    
    # OpenRouter settings
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-3.5-turbo"
    
    class Config:
        env_file = ".env"
        env_prefix = "CORE_"