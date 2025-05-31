from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    """LLM mesaj formatı"""
    role: MessageRole = Field(..., description="Mesajın rolü (system, user, assistant)")
    content: str = Field(..., description="Mesaj içeriği") 
    timestamp: Optional[datetime] = Field(None, description="Mesaj zamanı")

class ContextMetadata(BaseModel):
    """Bağlam meta verileri"""
    model: str = Field(..., description="Kullanılan model adı")
    temperature: float = Field(..., ge=0.0, le=2.0, description="Model sıcaklık değeri")
    max_tokens: int = Field(..., description="Maksimum token sayısı")
    created_at: datetime = Field(..., description="Bağlam oluşturma zamanı")

class Context(BaseModel):
    """Chat bağlamı"""
    session_id: str = Field(..., description="Chat oturum ID'si")
    messages: List[Message] = Field(..., description="Bağlam mesajları")
    metadata: ContextMetadata = Field(..., description="Bağlam meta verileri")

class ContextConfig(BaseModel):
    """Bağlam yapılandırması"""
    max_tokens: int = Field(4000, gt=0, description="Maksimum token sayısı")
    max_messages: int = Field(10, gt=0, description="Maksimum mesaj sayısı")
    system_prompt: str = Field(
        "You are a helpful AI assistant.",
        description="Sistem promptu"
    )
    preserve_history: bool = Field(
        True,
        description="Geçmiş mesajları koruma durumu"
    )
    compression_enabled: bool = Field(
        False,
        description="Bağlam sıkıştırma durumu"
    ) 