import pytest
from unittest.mock import AsyncMock, MagicMock
from src.backend.services.chat_service import ChatService
from src.backend.config.models import ModelConfig, ModelProvider
from fastapi import HTTPException

@pytest.fixture
def mock_model_config():
    return ModelConfig(
        provider=ModelProvider.OPENROUTER,
        model="test-model",
        temperature=0.7,
        knowledge_table="test_knowledge",
        api_key="sk-testkey123"  # Mock API key for testing
    )

@pytest.fixture
def mock_openai_response():
    return MagicMock(
        choices=[MagicMock(message=MagicMock(content="test response"))],
        usage=MagicMock(prompt_tokens=10, completion_tokens=5)
    )

@pytest.fixture
def chat_service(mock_model_config):
    service = ChatService(mock_model_config)
    service.client = AsyncMock()
    return service

@pytest.mark.asyncio
async def test_process_chat_request_success(chat_service, mock_openai_response):
    chat_service.client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
    
    messages = [{"role": "user", "content": "test"}]
    response = await chat_service.process_chat_request(messages)
    
    assert response["message"]["content"] == "test response"
    assert response["usage"]["input_tokens"] == 10
    assert response["usage"]["output_tokens"] == 5

@pytest.mark.asyncio
async def test_get_rag_context(chat_service):
    context = await chat_service.get_rag_context("test query")
    assert context == "Context from test_knowledge for: test query"

@pytest.mark.asyncio
async def test_process_chat_request_api_error(chat_service):
    from openai import APIStatusError
    from tenacity import RetryError
    
    chat_service.client.chat.completions.create = AsyncMock(
        side_effect=APIStatusError(
            message="API error",
            response=MagicMock(status_code=500),
            body={}
        )
    )

    with pytest.raises(RetryError) as exc_info:
        await chat_service.process_chat_request([{"role": "user", "content": "test"}])
    
    # Verify the original error was an HTTPException with status 500
    http_exc = exc_info.value.args[0].exception()
    assert isinstance(http_exc, HTTPException)
    assert http_exc.status_code == 500
    assert http_exc.detail == "API error"