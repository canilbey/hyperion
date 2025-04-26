from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Dict
from enum import Enum
import uuid

class ModelProvider(str, Enum):
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ModelConfigRequest(BaseModel):
    model_id: Optional[str] = Field(
        default=None,
        description="Either model_id or model_name must be provided"
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Either model_id or model_name must be provided"
    )
    provider: Optional[ModelProvider] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    knowledge_table: Optional[str] = None
    temperature: Optional[float] = None

    @field_validator('model_id', 'model_name', mode='before')
    def check_at_least_one_identifier(cls, v, info):
        if not v and not info.data.get('model_name' if info.field_name == 'model_id' else 'model_id'):
            raise ValueError("Either model_id or model_name must be provided")
        return v

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_items=1)
    custom_config: Optional[ModelConfigRequest] = None
    stream: bool = False
    chat_name: Optional[str] = Field(
        default=None,
        description="Optional name/identifier for the chat session"
    )

    @field_validator('custom_config', mode='before')
    def validate_custom_config(cls, v):
        if v is not None:
            # Handle both dict and ModelConfigRequest inputs
            model_id = v.get('model_id') if isinstance(v, dict) else v.model_id
            model_name = v.get('model_name') if isinstance(v, dict) else v.model_name
            if model_id is None and model_name is None:
                raise ValueError("Either model_id or model_name must be provided in custom_config")
        return v

class ChatResponse(BaseModel):
    message: ChatMessage
    model_used: str
    provider: str
    usage: Optional[dict] = None
    chat_id: Optional[str] = Field(
        default=None,
        description="ID of the chat session, if persisted"
    )

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size: int

class ModelCreateRequest(BaseModel):
    provider: ModelProvider = ModelProvider.OPENROUTER
    model: str = "deepseek/deepseek-chat-v3-0324:free"
    model_name: str = "Deepseek Chat v3"
    system_prompt: str = "You are a helpful assistant."
    api_key: Optional[str] = None
    knowledge_table_name: Optional[str] = None
    knowledge_table_id: Optional[str] = None

class ModelCreateResponse(BaseModel):
    status: str
    model_name: str
    model_id: str
    error: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    database: str
    redis: str