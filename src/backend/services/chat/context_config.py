from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from .context_types import ContextConfig
from backend.config.models import MODEL_TOKEN_LIMITS

class ContextSettings(BaseSettings):
    """Bağlam yapılandırma ayarları"""
    # Varsayılan bağlam ayarları
    DEFAULT_MAX_TOKENS: int = 4000
    DEFAULT_MAX_MESSAGES: int = 10
    DEFAULT_SYSTEM_PROMPT: str = "You are a helpful AI assistant."
    DEFAULT_PRESERVE_HISTORY: bool = True
    DEFAULT_COMPRESSION_ENABLED: bool = False

    # Model bazlı bağlam ayarları
    MODEL_CONTEXT_CONFIGS: Dict[str, Dict[str, Any]] = {
        "gpt-4": {
            "max_tokens": MODEL_TOKEN_LIMITS["gpt-4"],
            "max_messages": 20,
            "system_prompt": "You are a helpful AI assistant powered by GPT-4.",
            "preserve_history": True,
            "compression_enabled": False
        },
        "gpt-3.5-turbo": {
            "max_tokens": MODEL_TOKEN_LIMITS.get("gpt-3.5-turbo", 4000),
            "max_messages": 10,
            "system_prompt": "You are a helpful AI assistant powered by GPT-3.5.",
            "preserve_history": True,
            "compression_enabled": False
        },
        "claude-3-opus": {
            "max_tokens": 100000,
            "max_messages": 50,
            "system_prompt": "You are a helpful AI assistant powered by Claude 3.",
            "preserve_history": True,
            "compression_enabled": True
        }
    }

    def get_model_config(self, model_name: str) -> ContextConfig:
        """Model için bağlam yapılandırmasını döndürür"""
        model_config = self.MODEL_CONTEXT_CONFIGS.get(
            model_name,
            {
                "max_tokens": self.DEFAULT_MAX_TOKENS,
                "max_messages": self.DEFAULT_MAX_MESSAGES,
                "system_prompt": self.DEFAULT_SYSTEM_PROMPT,
                "preserve_history": self.DEFAULT_PRESERVE_HISTORY,
                "compression_enabled": self.DEFAULT_COMPRESSION_ENABLED
            }
        )
        
        return ContextConfig(**model_config)

    class Config:
        env_prefix = "CONTEXT_"
        case_sensitive = True 

class ContextWindow(BaseModel):
    """Model bazlı context window yapılandırması"""
    model: str
    max_tokens: Optional[int] = None  # Model'in maksimum token limiti
    token_limit: Optional[int] = None  # Kullanıcı tarafından belirlenen token limiti
    max_messages: int = 50  # Maksimum mesaj sayısı
    system_prompt: Optional[str] = None  # Model'e özel system prompt

    @property
    def effective_token_limit(self) -> Optional[int]:
        """Etkili token limitini döndürür"""
        return self.token_limit or self.max_tokens

# Model bazlı context window yapılandırmaları
MODEL_CONTEXT_WINDOWS = {
    # OpenAI modelleri
    "gpt-4": ContextWindow(
        model="gpt-4",
        max_tokens=8192,
        max_messages=50
    ),
    "gpt-4-turbo": ContextWindow(
        model="gpt-4-turbo",
        max_tokens=128000,
        max_messages=50
    ),
    "gpt-3.5-turbo": ContextWindow(
        model="gpt-3.5-turbo",
        max_tokens=16385,
        max_messages=50
    ),
    
    # Anthropic modelleri
    "claude-3-opus": ContextWindow(
        model="claude-3-opus",
        max_tokens=200000,
        max_messages=50
    ),
    "claude-3-sonnet": ContextWindow(
        model="claude-3-sonnet",
        max_tokens=200000,
        max_messages=50
    ),
    "claude-3-haiku": ContextWindow(
        model="claude-3-haiku",
        max_tokens=200000,
        max_messages=50
    ),
    
    # Deepseek modelleri
    "deepseek/deepseek-chat-v3-0324:free": ContextWindow(
        model="deepseek/deepseek-chat-v3-0324:free",
        max_tokens=32768,
        max_messages=50
    ),
    
    # Mistral modelleri
    "mistral/mistral-large": ContextWindow(
        model="mistral/mistral-large",
        max_tokens=32768,
        max_messages=50
    ),
    "mistral/mistral-medium": ContextWindow(
        model="mistral/mistral-medium",
        max_tokens=32768,
        max_messages=50
    ),
    "mistral/mistral-small": ContextWindow(
        model="mistral/mistral-small",
        max_tokens=32768,
        max_messages=50
    )
} 