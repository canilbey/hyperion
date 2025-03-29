import os
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI, APIError
from tenacity import retry, stop_after_attempt, wait_exponential
from config.models import ModelConfig, ModelProvider
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, model_config: ModelConfig):
        self.config = model_config
        self.client = self._init_client()
        
    def _init_client(self):
        base_url = self.config.base_url or self._get_default_base_url()
        return AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=base_url
        )

    def _get_default_base_url(self):
        return {
            ModelProvider.OPENROUTER: "https://openrouter.ai/api/v1",
            ModelProvider.OLLAMA: "http://localhost:11434/v1",
            ModelProvider.LM_STUDIO: "http://localhost:1234/v1"
        }.get(self.config.provider, "https://api.openai.com/v1")

    async def get_rag_context(self, query: str) -> Optional[str]:
        """Placeholder for RAG service integration"""
        if not self.config.knowledge_table:
            return None
        return f"Context from {self.config.knowledge_table} for: {query}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_chat_request(self, messages: list, stream: bool = False):
        """Main chat processing method"""
        try:
            # Get RAG context if configured
            user_message = next(m for m in messages if m["role"] == "user")
            rag_context = await self.get_rag_context(user_message["content"])
            
            if rag_context:
                messages = [{"role": "system", "content": rag_context}] + messages

            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                stream=stream
            )

            return {
                "message": {
                    "role": "assistant",
                    "content": response.choices[0].message.content
                },
                "model_used": self.config.model,
                "provider": self.config.provider.value,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                } if response.usage else None
            }
        except APIError as e:
            logger.error(f"API Error: {str(e)}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Chat processing error: {str(e)}")
            raise HTTPException(status_code=500, detail="Chat service unavailable")