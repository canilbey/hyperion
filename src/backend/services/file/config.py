from pydantic_settings import BaseSettings

class FileConfig(BaseSettings):
    max_file_size: int = 10485760  # 10MB
    allowed_types: list = ["text/plain", "application/pdf"]
    
    class Config:
        env_file = ".env"
        env_prefix = "FILE_"