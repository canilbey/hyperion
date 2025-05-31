from typing import List, Optional, Dict, Any
from backend.models import ChatSession, ChatMessage
from .context_config import ContextSettings, ContextWindow
from .context_types import Context, ContextMetadata, Message
from datetime import datetime

class ContextManager:
    def __init__(self, settings: ContextSettings, model_service):
        self.settings = settings
        self.model_service = model_service

    async def get_llm_response(
        self,
        session: ChatSession,
        messages: List[ChatMessage],
        custom_system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        # Input validation
        if not isinstance(session, ChatSession):
            raise TypeError("session must be a ChatSession instance")
        if not isinstance(messages, list) or not all(isinstance(m, ChatMessage) for m in messages):
            raise TypeError("messages must be a list of ChatMessage instances")
        if custom_system_prompt is not None and not isinstance(custom_system_prompt, str):
            raise TypeError("custom_system_prompt must be None or a string")

        # Gerçek model entegrasyonu
        # model_service, model_config ve provider bilgisi ChatService tarafından sağlanıyor
        # Bu fonksiyonun imzası değişmeden, model çağrısını ChatService üzerinden yapacağız
        # Bu nedenle, burada stub yerine gerçek çağrı için bir hook bırakıyoruz
        if hasattr(self.model_service, "call_model_api"):
            # Eğer model_service üzerinde call_model_api fonksiyonu varsa onu kullan
            return await self.model_service.call_model_api(
                session=session,
                messages=messages,
                custom_system_prompt=custom_system_prompt
            )
        # Eğer yoksa, eski stub'u koru (geri uyumluluk için)
        return {
            "message": ChatMessage(role="assistant", content="Stub response"),
            "model": session.model_name,
            "provider": "stub",
            "usage": None
        }

    async def prepare_context(
        self,
        messages: List[ChatMessage],
        custom_system_prompt: Optional[str] = None,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        created_at: Optional[datetime] = None
    ) -> Context:
        # ChatMessage -> Message dönüşümü
        message_objs = []
        for m in messages:
            role = m.role.value if hasattr(m.role, 'value') else str(m.role)
            ts = None
            if hasattr(m, 'created_at') and m.created_at:
                ts = m.created_at.isoformat() if hasattr(m.created_at, 'isoformat') else str(m.created_at)
            elif hasattr(m, 'timestamp') and m.timestamp:
                ts = m.timestamp.isoformat() if hasattr(m.timestamp, 'isoformat') else str(m.timestamp)
            message_objs.append(Message(
                role=role,
                content=m.content,
                timestamp=ts
            ))
        return Context(
            session_id=session_id or "stub-session",
            messages=message_objs,
            metadata=ContextMetadata(
                model=model or "stub-model",
                temperature=temperature or 0.7,
                max_tokens=max_tokens or 4000,
                created_at=(created_at.isoformat() if created_at and hasattr(created_at, 'isoformat') else (created_at or datetime.utcnow().isoformat()))
            )
        ) 