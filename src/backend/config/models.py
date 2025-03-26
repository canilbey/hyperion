from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class ModelProvider(str, Enum):
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"

class ModelConfig(BaseModel):
    provider: ModelProvider = Field(
        default=ModelProvider.OPENROUTER,
        description="LLM service provider"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for provider (required for OpenRouter)"
    )
    model: str = Field(
        default="gpt-3.5-turbo",
        description="Model name to use for completions"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Custom base URL for self-hosted providers"
    )
    knowledge_table: Optional[str] = Field(
        default=None,
        description="Database table name for RAG context"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Model temperature parameter"
    )