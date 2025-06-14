from pydantic_settings import BaseSettings

class FileConfig(BaseSettings):
    max_file_size: int = 1048576000  # 100MB (10x artırıldı)
    allowed_types: list = ["text/plain", "application/pdf"]
    
    class Config:
        env_file = ".env"
        env_prefix = "FILE_"