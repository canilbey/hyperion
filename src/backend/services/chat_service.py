import os
import logging
import aiohttp
import json
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential
from config.models import ModelProvider, ModelConfig
from fastapi import HTTPException
from backend.services.model.service import ModelService
from .chat.context_manager import ContextManager, ContextWindow
from .chat.context_config import ContextSettings
from .chat.context_types import Context, Message
from ...models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, model_service: ModelService):
        self.model_service = model_service
        self.context_settings = ContextSettings()
        self.context_manager = ContextManager(
            model_service=model_service,
            window_config=ContextWindow()  # Varsayılan yapılandırma
        )
        logger.info("Initialized ChatService with context management")
        
    def _get_context_window(self, model_name: str) -> ContextWindow:
        """Model için bağlam penceresi yapılandırmasını döndürür"""
        config = self.context_settings.get_model_config(model_name)
        return ContextWindow(
            max_tokens=config.max_tokens,
            max_messages=config.max_messages,
            system_prompt=config.system_prompt
        )

    async def _call_openrouter(self, messages: list, model_config: ModelConfig, context: Optional[Context] = None) -> dict:
        headers = {
            "Authorization": f"Bearer {model_config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Hyperion"
        }
        
        # Bağlam varsa, mesajları bağlamdan al
        if context:
            messages = [msg.dict() for msg in context.messages]
        
        data = {
            "model": model_config.model,
            "messages": messages,
            "temperature": model_config.temperature
        }
        
        logger.info("Sending request to OpenRouter", extra={
            "event": "openrouter_request",
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "headers": {k: "****" if k == "Authorization" else v for k, v in headers.items()},
            "payload": {
                "model": data["model"],
                "messages": [{"role": m["role"], "content_length": len(m["content"])} for m in data["messages"]],
                "message_count": len(data["messages"]),
                "temperature": data["temperature"]
            },
            "model_config": {
                "provider": model_config.provider.value,
                "model": model_config.model,
                "has_api_key": bool(model_config.api_key),
                "temperature": model_config.temperature
            },
            "context": {
                "has_context": bool(context),
                "message_count": len(context.messages) if context else 0,
                "max_tokens": context.metadata.max_tokens if context else None
            } if context else None
        })
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    response_text = await response.text()
                    logger.info(f"OpenRouter response: {response.status} - {response_text}")
                    
                    if response.status == 200:
                        response_data = await response.json()
                        logger.info("OpenRouter response received", extra={
                            "event": "openrouter_response",
                            "status": response.status,
                            "usage": response_data.get("usage", {}),
                            "response": {
                                "content_length": len(response_data["choices"][0]["message"]["content"]),
                                "finish_reason": response_data["choices"][0].get("finish_reason")
                            }
                        })
                        return response_data
                    else:
                        error_msg = f"OpenRouter API error: {response.status} - {response_text}"
                        logger.error(error_msg, extra={
                            "event": "openrouter_error",
                            "status": response.status,
                            "response_text": response_text,
                            "request": {
                                "model": data["model"],
                                "message_count": len(data["messages"]),
                                "temperature": data["temperature"]
                            }
                        })
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_msg
                        )
        except AttributeError as ae:
            error_msg = f"AttributeError in OpenRouter call: {str(ae)}"
            logger.error(error_msg, exc_info=True, extra={
                "event": "openrouter_error",
                "error_type": "AttributeError",
                "model_config": {
                    "provider": model_config.provider.value,
                    "model": model_config.model,
                    "has_api_key": bool(model_config.api_key)
                }
            })
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
        except Exception as e:
            error_msg = f"Error contacting OpenRouter: {str(e)}"
            logger.error(error_msg, exc_info=True, extra={
                "event": "openrouter_error",
                "error_type": type(e).__name__,
                "model_config": {
                    "provider": model_config.provider.value,
                    "model": model_config.model
                }
            })
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )

    async def get_rag_context(self, query: str) -> Optional[str]:
        return None  # RAG functionality not currently implemented

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_chat_request(
        self,
        session: ChatSession,
        messages: List[ChatMessage],
        model_config: ModelConfig,
        stream: bool = False,
        custom_system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            logger.info("Processing chat request", extra={
                "event": "chat_request_start",
                "session_id": str(session.id),
                "model": model_config.model,
                "provider": model_config.provider.value,
                "message_count": len(messages)
            })
            
            # Model için bağlam penceresini güncelle
            self.context_manager.window_config = self._get_context_window(model_config.model)
            
            # Bağlamı hazırla
            context = await self.context_manager.prepare_context(
                session=session,
                messages=messages,
                custom_system_prompt=custom_system_prompt
            )
            
            # Get RAG context if configured
            user_message = next((m for m in messages if m.role == "user"), None)
            if user_message is None:
                raise HTTPException(status_code=400, detail="No user message found")
            rag_context = await self.get_rag_context(user_message.content)
            
            if rag_context:
                context["messages"].insert(0, {
                    "role": "system",
                    "content": rag_context
                })

            if model_config.provider == ModelProvider.OPENROUTER:
                response = await self._call_openrouter(
                    messages=[],  # Mesajlar bağlamdan alınacak
                    model_config=model_config,
                    context=Context(**context)
                )

                logger.info("Chat request completed", extra={
                    "event": "chat_request_complete",
                    "session_id": str(session.id),
                    "model": model_config.model,
                    "provider": model_config.provider.value,
                    "response_tokens": response.get("usage", {}).get("completion_tokens", 0),
                    "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0),
                    "context": {
                        "message_count": len(context["messages"]),
                        "max_tokens": context["metadata"]["max_tokens"]
                    }
                })
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Only OpenRouter provider currently supported"
                )

            return {
                "message": {
                    "role": "assistant",
                    "content": response["choices"][0]["message"]["content"]
                },
                "model_used": model_config.model,
                "provider": model_config.provider.value,
                "usage": response.get("usage"),
                "context": {
                    "message_count": len(context["messages"]),
                    "max_tokens": context["metadata"]["max_tokens"]
                }
            }
            
        except HTTPException as he:
            logger.error("Chat processing HTTP exception", extra={
                "event": "chat_request_failed",
                "session_id": str(session.id),
                "error_type": "HTTPException",
                "status_code": he.status_code,
                "detail": he.detail
            })
            raise
        except Exception as e:
            error_msg = f"Chat processing error: {str(e)}"
            logger.error(error_msg, extra={
                "event": "chat_request_failed",
                "session_id": str(session.id),
                "error_type": type(e).__name__,
                "error_details": str(e),
                "model": model_config.model,
                "provider": model_config.provider.value
            })
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )