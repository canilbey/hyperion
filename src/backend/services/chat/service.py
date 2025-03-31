import logging
from typing import Dict, Any, List
from models import ChatRequest, ChatResponse
from services.model.service import ModelService
from .config import ChatConfig  # Added import for ChatConfig

class ChatService:
    def __init__(self, config: ChatConfig, model_service: ModelService):
        self.config = config
        self.model_service = model_service
        self.logger = logging.getLogger(__name__)

    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request and return response"""
        self.logger.info("Processing chat request")
        
        try:
            # Get model configuration
            model_config = await self.model_service.get_model_config(
                model_id=request.custom_config.model_id,
                model_name=request.custom_config.model_name
            )
            
            # Process messages
            response = await self._generate_response(
                messages=[m.dict() for m in request.messages],
                model_config=model_config,
                stream=request.stream
            )
            
            return ChatResponse(
                message=response["message"],
                model_used=response["model"],
                provider=response["provider"],
                usage=response.get("usage")
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
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "message": result["choices"][0]["message"],
                "model": model,
                "provider": "openrouter",
                "usage": result.get("usage")
            }

    async def _call_openai_api(self, messages: List[Dict], model: str, api_key: str) -> Dict:
        """Call OpenAI API with the given messages"""
        import openai
        
        openai.api_key = api_key
        
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=messages
        )
        
        return {
            "message": response["choices"][0]["message"],
            "model": model,
            "provider": "openai",
            "usage": response.get("usage")
        }

    async def _call_anthropic_api(self, messages: List[Dict], model: str, api_key: str) -> Dict:
        """Call Anthropic API with the given messages"""
        import anthropic
        
        client = anthropic.AsyncAnthropic(api_key=api_key)
        
        response = await client.messages.create(
            model=model,
            messages=messages,
            max_tokens=1000
        )
        
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