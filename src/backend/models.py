from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import List, Optional, Literal, Dict, Any
from enum import Enum
import uuid
from datetime import datetime, timezone
from uuid import UUID

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
        description="Model_id must be provided"
    )
    provider: Optional[ModelProvider] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    knowledge_table: Optional[str] = None
    temperature: Optional[float] = None

    @field_validator('model_id', mode='before')
    def check_model_id(cls, v, info):
        if not v:
            raise ValueError("model_id must be provided")
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
            if model_id is None:
                raise ValueError("model_id must be provided in custom_config")
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
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature (0.0-2.0)")
    max_tokens: Optional[int] = Field(default=None, gt=0, le=100000, description="Maximum tokens per response")
    token_limit: Optional[int] = Field(default=None, gt=0, le=1000000, description="Maximum tokens per context")
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: uuid.UUID
    hashed_password: str
    roles: List[Role] = []

class UserPublic(UserBase):
    id: uuid.UUID
    roles: List[Role] = []

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenPayload(BaseModel):
    sub: str  # user_id
    roles: List[Role]
    exp: int

class ModelConfig(BaseModel):
    provider: ModelProvider
    model: str
    api_key: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0, le=100000)
    token_limit: Optional[int] = Field(default=None, gt=0, le=1000000)
    system_prompt: Optional[str] = None

class ChatSession(BaseModel):
    id: UUID
    model_id: str
    temperature: float = Field(default=0.7)