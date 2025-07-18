import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
import json
from backend.models import ChatRequest, ChatResponse, ChatSession, ChatMessage
from backend.services.model.service import ModelService
from .config import ChatConfig
from .storage import ChatStorageService
from .context_manager import ContextManager, ContextSettings, ContextWindow
from .context_config import MODEL_CONTEXT_WINDOWS
from .context_storage import ContextStorageService
from datetime import datetime
from backend.services.rag_service import RagService
from fastapi import HTTPException
from backend.services.search.hybrid_search import hybrid_search

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

class ChatService:
    def __init__(
        self,
        config: ChatConfig,
        model_service: ModelService,
        storage_service: ChatStorageService,
        context_storage_service: ContextStorageService,
        redis_pool=None,
        bm25_index=None,
        milvus_client=None,
        cross_encoder_model=None
    ):
        self.config = config
        self.model_service = model_service
        self.storage_service = storage_service
        self.context_storage_service = context_storage_service
        self.redis_pool = redis_pool
        self.logger = logging.getLogger(__name__)
        self.context_managers = {}  # Model bazlı context manager'lar
        
        # RAG service'i initialize ediyorum
        self.rag_service = RagService()
        self.bm25_index = bm25_index
        self.milvus_client = milvus_client
        self.cross_encoder_model = cross_encoder_model

    def _get_context_manager(self, model_id: str) -> ContextManager:
        """Model için context manager'ı döndürür veya oluşturur"""
        if model_id not in self.context_managers:
            # Model için context window ayarlarını al
            context_window = MODEL_CONTEXT_WINDOWS.get(model_id, ContextWindow(
                model=model_id,
                max_tokens=4000,  # Varsayılan değer
                max_messages=50
            ))
            
            # Context settings oluştur
            settings = ContextSettings()
            
            # Context manager oluştur
            self.context_managers[model_id] = ContextManager(
                settings,
                model_service=self.model_service
            )
            
        return self.context_managers[model_id]

    async def get_rag_context(self, query: str) -> Optional[str]:
        """RAG context'i alır ve sistem prompt'u olarak formatlar (hybrid search ile)"""
        try:
            self.logger.info(f"RAG context retrieval started for query: {query[:100]}...")
            # Hybrid search ile parent chunk'ları bul
            if self.bm25_index is not None and self.milvus_client is not None:
                parent_chunks = hybrid_search(
                    query,
                    bm25_index=self.bm25_index,
                    milvus_client=self.milvus_client,
                    cross_encoder_model=self.cross_encoder_model,
                    top_k=5
                )
                self.logger.info("Hybrid search pipeline kullanıldı.")
            else:
                self.logger.warning("BM25 veya Milvus index yok, sadece semantic search pipeline kullanılacak.")
                parent_chunks = await self.rag_service.retrieve_context(query)
            if parent_chunks:
                context_texts = []
                for chunk in parent_chunks:
                    text = chunk.get("parent_content", "") if isinstance(chunk, dict) else chunk.get("content", "")
                    if text:
                        context_texts.append(text)
                if context_texts:
                    context_text = "\n".join(context_texts)
                    rag_prompt = f"""Aşağıdaki bilgileri kullanarak kullanıcının sorusunu yanıtla. Bu bilgiler kullanıcının daha önce yüklediği belgelerden geliyor:
\n{context_text}\n\nEğer yukarıdaki bilgiler soruyla ilgili değilse, genel bilgin ile yanıtla."""
                    self.logger.info(f"RAG context retrieved: {len(parent_chunks)} parent chunks, {len(context_text)} chars")
                    return rag_prompt
            self.logger.info("No relevant RAG context found")
            return None
        except Exception as e:
            self.logger.error(f"RAG context retrieval failed: {e}", exc_info=True)
            return None

    async def process_chat_request(
        self,
        request: ChatRequest,
        chat_id: Optional[UUID] = None,
        chat_name: Optional[str] = None
    ) -> ChatResponse:
        """Process a chat request and return response"""
        self.logger.info(f"Processing chat request - chat_id: {chat_id}, chat_name: {chat_name or request.chat_name}")
        
        try:
            # Get or create chat session
            if not chat_id:
                chat_id = await self.storage_service.create_chat(label=chat_name or request.chat_name)
            
            # Get model configuration
            model_id = request.custom_config.model_id if request.custom_config else None
            model_config = await self._get_cached_model_config(model_id=model_id)
            
            if not model_config:
                raise ValueError("Model configuration not found. Please provide a valid model_id.")
            
            # Get context manager for the model
            context_manager = self._get_context_manager(model_id)
            
            # Get existing context or create new one
            existing_context = await self.context_storage_service.get_context(chat_id)

            messages = []
            if existing_context:
                messages.extend(existing_context.messages)
            else:
                history = await self._get_cached_chat_history(chat_id)
                messages.extend([ChatMessage(**msg) if isinstance(msg, dict) else msg for msg in history])

            # Store user messages (yeni mesajlar sona eklenir)
            for msg in request.messages:
                if msg.role == "user":
                    message_id = await self.storage_service.add_message(
                        chat_id=chat_id,
                        role=msg.role,
                        content=msg.content,
                        chat_name=chat_name or request.chat_name,
                        usage=None
                    )
                    messages.append(ChatMessage(
                        id=message_id,
                        chat_id=chat_id,
                        role=msg.role,
                        content=msg.content,
                        created_at=None  # DB'den gelecek
                    ))
            
            # Create chat session for context
            session = ChatSession(
                id=chat_id,
                model_id=model_id,
                temperature=model_config.get("temperature", 0.7)
            )
            
            # Gerçek model yanıtı al
            response = await self.call_model_api(
                session=session,
                messages=messages,
                custom_system_prompt=getattr(request.custom_config, 'system_prompt', None) if request.custom_config else None
            )
            
            if not response:
                raise ValueError("Model API'den geçerli bir yanıt alınamadı. Lütfen model ayarlarını ve API anahtarını kontrol edin.")
            
            # Store assistant response
            await self.storage_service.add_message(
                chat_id=chat_id,
                role="assistant",
                content=response["message"]["content"],
                usage=response.get("usage"),
                chat_name=chat_name or request.chat_name
            )
            
            # Update context
            context = await context_manager.prepare_context(
                messages=messages + [ChatMessage(
                    id=None,
                    chat_id=chat_id,
                    role="assistant",
                    content=response["message"]["content"],
                    created_at=None
                )],
                custom_system_prompt=getattr(request.custom_config, 'system_prompt', None) if request.custom_config else None,
                session_id=str(chat_id),
                model=model_config["model"],
                temperature=model_config.get("temperature", 0.7),
                max_tokens=model_config.get("max_tokens", 4000),
                created_at=datetime.utcnow()
            )
            
            await self.context_storage_service.update_context(
                chat_id=chat_id,
                context=context,
                metadata={
                    "model": model_config["model"],
                    "temperature": model_config.get("temperature", 0.7),
                    "provider": model_config.get("provider"),
                    "last_updated": datetime.utcnow().isoformat()
                }
            )
            
            # Invalidate cache
            await self._invalidate_chat_cache(chat_id)
            
            return ChatResponse(
                message=response["message"],
                model_used=response["model"],
                provider=response["provider"],
                usage=response.get("usage"),
                chat_id=str(chat_id)
            )
            
        except Exception as e:
            self.logger.error(f"Chat processing failed: {str(e)}", exc_info=True)
            raise

    async def _generate_response(self, messages: List[Dict], model_config: Dict, stream: bool) -> Dict:
        """Generate chat response using model service"""
        if not model_config:
            raise ValueError("No model configuration provided")
            
        provider = model_config.get("provider")
        model = model_config.get("model")
        api_key = model_config.get("api_key")
        
        if provider == "openrouter":
            return await self._call_openrouter_api(messages, model, api_key)
        elif provider == "openai":
            return await self._call_openai_api(messages, model, api_key)
        elif provider == "anthropic":
            return await self._call_anthropic_api(messages, model, api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _call_openrouter_api(self, messages: List[Dict], model: str, api_key: str) -> Dict:
        """Call OpenRouter API with the given messages"""
        import httpx
        
        # Apply rate limiting
        if self.redis_pool:
            rate_limit_key = f"rate_limit:openrouter:{api_key[-6:]}"
            current = await self.redis_pool.incr(rate_limit_key)
            if current == 1:
                await self.redis_pool.expire(rate_limit_key, 60)  # 1 minute window
            if current > 10:  # 10 requests per minute
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests to OpenRouter API"
                )

        self.logger.info(f"Calling OpenRouter API: model={model}")
        self.logger.debug(f"OpenRouter API request data: {messages}")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Configure timeout for longer responses (especially with RAG context)
        timeout = httpx.Timeout(60.0, connect=10.0)  # 60s total, 10s connect
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": model,
                    "messages": messages
                },
                headers=headers
            )

        self.logger.debug(f"OpenRouter API response: {response}")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error calling OpenRouter API: {response.text}"
            )
        
        data = response.json()
        self.logger.debug(f"OpenRouter API response JSON: {data}")
        return {
            "message": data["choices"][0]["message"],
            "model": model,
            "provider": "openrouter",
            "usage": data.get("usage")
        }

    async def _get_cached_chat_history(self, chat_id: UUID) -> List[Dict]:
        """Get chat history from cache or database"""
        if not self.redis_pool:
            return await self.storage_service.get_chat_history(chat_id)

        cache_key = f"chat:{chat_id}:history"
        try:
            cached = await self.redis_pool.get(cache_key)
            if cached:
                self.logger.debug(f"Cache hit for chat history: {chat_id}")
                return json.loads(cached)

            messages = await self.storage_service.get_chat_history(chat_id)
            if messages:
                await self.redis_pool.setex(
                    cache_key,
                    3600,  # 1 hour TTL
                    json.dumps([m.dict() for m in messages], cls=UUIDEncoder)
                )
            return messages
        except Exception as e:
            self.logger.error(f"Error getting chat history: {str(e)}")
            return await self.storage_service.get_chat_history(chat_id)

    async def _invalidate_chat_cache(self, chat_id: UUID):
        """Invalidate cached chat history"""
        if not self.redis_pool:
            return

        try:
            cache_key = f"chat:{chat_id}:history"
            await self.redis_pool.delete(cache_key)
            self.logger.debug(f"Invalidated cache for chat: {chat_id}")
        except Exception as e:
            self.logger.error(f"Error invalidating cache: {str(e)}")

    def _estimate_token_count(self, messages: List[dict]) -> int:
        """Mesaj listesinin yaklaşık toplam token sayısını döndürür."""
        total = 0
        for msg in messages:
            content = msg.get('content', '')
            total += len(content.split()) * 2  # Basit tahmin
        return total

    def _truncate_messages_to_token_limit(self, messages: List[dict], token_limit: int) -> List[dict]:
        """Token limiti aşılırsa en eski mesajdan başlayarak mesajları çıkarır. İlk system mesajı asla silinmez."""
        truncated = list(messages)
        # Eğer ilk mesaj system ise, onu koru
        system_msg = None
        if truncated and truncated[0].get('role') == 'system':
            system_msg = truncated.pop(0)
        while self._estimate_token_count(truncated) > token_limit and len(truncated) > 1:
            truncated.pop(0)
        if system_msg:
            truncated = [system_msg] + truncated
        return truncated

    async def call_model_api(self, session, messages, custom_system_prompt=None):
        """Gerçek model API çağrısı yapar. RAG entegrasyonu ile."""
        model_id = getattr(session, 'model_id', None)
        self.logger.info(f"call_model_api: model_id={model_id}")
        model_config = await self._get_cached_model_config(model_id=model_id)
        api_key = model_config.get("api_key")
        model = model_config["model"]
        self.logger.info(f"call_model_api: model_config={model_config}")
        self.logger.info(f"call_model_api: api_key={api_key}")
        
        # Sadece en son user mesajı için RAG context ekle
        user_message = None
        for msg in reversed(messages):
            if hasattr(msg, 'role') and msg.role == "user":
                user_message = msg
                break
            elif isinstance(msg, dict) and msg.get('role') == "user":
                user_message = msg
                break
        
        messages_with_rag = list(messages)
        if user_message:
            query = user_message.content if hasattr(user_message, 'content') else user_message.get('content', '')
            rag_context = await self.get_rag_context(query)
            if rag_context:
                self.logger.info("RAG context added to system prompt (only for last user message)")
                rag_system_message = {
                    "role": "system",
                    "content": rag_context
                }
                messages_with_rag = [rag_system_message] + messages_with_rag  # Kesinlikle başa ekle
        
        # Custom system prompt'u da ekle (varsa)
        if custom_system_prompt:
            custom_sys_message = {"role": "system", "content": custom_system_prompt}
            messages_with_rag = [custom_sys_message] + list(messages_with_rag)
        
        # Mesajları serializable hale getir
        messages_dict = self._serialize_messages_for_llm(messages_with_rag)

        # Token limiti uygula (truncate)
        token_limit = model_config.get("token_limit") or model_config.get("max_tokens") or 4000
        messages_dict = self._truncate_messages_to_token_limit(messages_dict, token_limit)
        
        self.logger.debug(f"OpenRouter API FINAL request data: {messages_dict}")
        if model_config["provider"] == "openrouter":
            return await self._call_openrouter_api(messages_dict, model, api_key)
        raise NotImplementedError(f"Provider {model_config['provider']} not implemented.")

    async def _get_cached_model_config(self, model_id: Optional[str] = None) -> Dict:
        """Sadece model_id ile cache/DB'den model config getirir."""
        self.logger.info(f"_get_cached_model_config: model_id={model_id}")
        if not model_id:
            return None
        cache_key = f"model_config:{model_id}"
        if self.redis_pool:
            cached = await self.redis_pool.get(cache_key)
            if cached:
                self.logger.debug(f"Cache hit for model config: {cache_key}")
                config = json.loads(cached)
                if config.get("api_key") and config.get("provider") and config.get("model"):
                    return config
                else:
                    self.logger.warning(f"Cache fallback: Eksik alan tespit edildi, DB'den güncellenecek. Anahtar: {cache_key}")
        # Cache yoksa veya eksikse DB'den çek
        config = await self.model_service.get_model_config(model_id=model_id)
        self.logger.info(f"_get_cached_model_config: config={config}")
        if config is None:
            return None
        config_filtered = {k: v for (k, v) in config.items() if k not in ("created_at", "updated_at")}
        if self.redis_pool:
            await self.redis_pool.setex(cache_key, 86400, json.dumps(config_filtered, cls=UUIDEncoder))
        return config_filtered

    async def _call_openai_api(self, messages: List[Dict], model: str, api_key: str) -> Dict:
        """Call OpenAI API with the given messages"""
        import openai
        
        # Apply rate limiting
        if self.redis_pool:
            rate_limit_key = f"rate_limit:openai:{api_key[-6:]}"
            current = await self.redis_pool.incr(rate_limit_key)
            if current == 1:
                await self.redis_pool.expire(rate_limit_key, 60)  # 1 minute window
            if current > 5:  # 5 requests per minute
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests to OpenAI API"
                )

        self.logger.info(f"Calling OpenAI API: model={model}")
        self.logger.debug(f"OpenAI API request data: {messages}")
        openai.api_key = api_key
        
        # Configure timeout for longer responses
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=messages,
            timeout=60.0  # 60 seconds timeout
        )
        
        self.logger.debug(f"OpenAI API response: {response}")
        
        return {
            "message": response["choices"][0]["message"],
            "model": model,
            "provider": "openai",
            "usage": response.get("usage")
        }

    async def _call_anthropic_api(self, messages: List[Dict], model: str, api_key: str) -> Dict:
        """Call Anthropic API with the given messages"""
        import anthropic
        
        # Apply rate limiting
        if self.redis_pool:
            rate_limit_key = f"rate_limit:anthropic:{api_key[-6:]}"
            current = await self.redis_pool.incr(rate_limit_key)
            if current == 1:
                await self.redis_pool.expire(rate_limit_key, 60)  # 1 minute window
            if current > 5:  # 5 requests per minute
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests to Anthropic API"
                )
        
        self.logger.info(f"Calling Anthropic API: model={model}")
        self.logger.debug(f"Anthropic API request data: {messages}")
        
        # Configure timeout for longer responses
        client = anthropic.AsyncAnthropic(
            api_key=api_key,
            timeout=60.0  # 60 seconds timeout
        )
        
        response = await client.messages.create(
            model=model,
            messages=messages,
            max_tokens=1000
        )
        
        self.logger.debug(f"Anthropic API response: {response}")
        
        return {
            "message": {
                "role": "assistant",
                "content": response.content[0].text
            },
            "model": model,
            "provider": "anthropic",
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }

    def _serialize_messages_for_llm(self, messages):
        """LLM'e gönderilecek mesajları JSON serializable hale getirir."""
        serialized = []
        for m in messages:
            # Eğer ChatMessage veya Message ise dict'e çevir
            d = m.dict() if hasattr(m, 'dict') else dict(m)
            # role enum ise string'e çevir
            if hasattr(d['role'], 'value'):
                d['role'] = d['role'].value
            # timestamp varsa string'e çevir
            if d.get('timestamp'):
                if hasattr(d['timestamp'], 'isoformat'):
                    d['timestamp'] = d['timestamp'].isoformat()
                else:
                    d['timestamp'] = str(d['timestamp'])
            serialized.append({k: v for k, v in d.items() if v is not None})
        return serialized