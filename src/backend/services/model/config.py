from pydantic_settings import BaseSettings
from enum import Enum

class ModelProvider(str, Enum):
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

class ModelConfig(BaseSettings):
    default_provider: ModelProvider = ModelProvider.OPENROUTER
    default_model: str = "deepseek/deepseek-chat-v3-0324:free"
    default_system_prompt: str = "You are a helpful assistant."
    
    class Config:
        env_file = ".env"
        env_prefix = "MODEL_"