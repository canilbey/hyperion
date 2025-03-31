from pydantic_settings import BaseSettings

class SearchConfig(BaseSettings):
    top_k_default: int = 5
    similarity_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        env_prefix = "SEARCH_"