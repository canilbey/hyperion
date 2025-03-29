import os
import logging
import aiohttp
import json
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from config.models import ModelProvider
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, model_config: dict):
        self.config = model_config
        logger.info(f"Initialized ChatService with config: {self.config}")
        
    async def _call_openrouter(self, messages: list) -> dict:
        headers = {
            "Authorization": f"Bearer {self.config.get('api_key')}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Hyperion"
        }
        
        data = {
            "model": self.config.get("model"),
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7)
        }
        
        logger.info(f"Sending request to OpenRouter with data: {data}")
        
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
                        return await response.json()
                    else:
                        error_msg = f"OpenRouter API error: {response.status} - {response_text}"
                        logger.error(error_msg)
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_msg
                        )
        except Exception as e:
            error_msg = f"Network error contacting OpenRouter: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )

    async def get_rag_context(self, query: str) -> Optional[str]:
        if not self.config.get('knowledge_table'):
            return None
        return f"Context from {self.config['knowledge_table']} for: {query}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_chat_request(self, messages: list, stream: bool = False):
        try:
            # Verify model configuration
            if not self.config.get('api_key'):
                raise HTTPException(
                    status_code=400,
                    detail="API key is required for OpenRouter"
                )
                
            if not self.config.get('model'):
                raise HTTPException(
                    status_code=400,
                    detail="Model name is required"
                )

            # Get RAG context if configured
            user_message = next(m for m in messages if m["role"] == "user")
            rag_context = await self.get_rag_context(user_message["content"])
            
            if rag_context:
                messages = [{"role": "system", "content": rag_context}] + messages

            logger.info("Starting chat request processing", extra={
                "event": "chat_request_start",
                "model": self.config.get("model"),
                "provider": self.config.get("provider"),
                "message_count": len(messages),
                "has_rag_context": bool(rag_context)
            })

            if self.config.get("provider") == ModelProvider.OPENROUTER:
                response = await self._call_openrouter(messages)

                logger.info("Chat request completed successfully", extra={
                    "event": "chat_request_complete",
                    "model": self.config.get("model"),
                    "provider": self.config.get("provider"),
                    "response_tokens": response.get("usage", {}).get("completion_tokens", 0),
                    "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0)
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
                "model_used": self.config.get("model"),
                "provider": self.config.get("provider"),
                "usage": response.get("usage")
            }
            
        except HTTPException as he:
            logger.error("Chat processing HTTP exception", extra={
                "event": "chat_request_failed",
                "error_type": "HTTPException",
                "status_code": he.status_code,
                "detail": he.detail
            })
            raise
        except Exception as e:
            error_msg = f"Chat processing error: {str(e)}"
            logger.error(error_msg, extra={
                "event": "chat_request_failed",
                "error_type": type(e).__name__,
                "error_details": str(e),
                "model": self.config.get("model"),
                "provider": self.config.get("provider")
            })
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )