from pydantic_settings import BaseSettings

class ChatConfig(BaseSettings):
    default_model: str = "deepseek/deepseek-chat-v3-0324:free"
    system_prompt: str = "You are a helpful assistant."
    max_tokens: int = 2048
    
    class Config:
        env_file = ".env"
        env_prefix = "CHAT_"