import pytest
from uuid import UUID
from unittest.mock import AsyncMock
from src.backend.services.chat.service import ChatService
from src.backend.services.chat.storage import ChatStorageService
from src.backend.models import ChatRequest, ChatMessage

@pytest.mark.asyncio
async def test_process_new_chat(mock_model_service, mock_storage_service):
    # Setup mocks
    mock_model_service.get_model_config = AsyncMock(return_value={
        "provider": "openai",
        "model": "gpt-4"
    })
    mock_storage_service.create_chat = AsyncMock(return_value=UUID(int=0))
    mock_storage_service.add_message = AsyncMock()
    
    # Test new chat
    service = ChatService(
        config=AsyncMock(),
        model_service=mock_model_service,
        storage_service=mock_storage_service
    )
    
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="Hello")],
        custom_config=None,
        stream=False
    )
    
    response = await service.process_chat_request(request)
    
    # Verify
    mock_storage_service.create_chat.assert_called_once()
    mock_storage_service.add_message.assert_called()
    assert response.chat_id == "00000000-0000-0000-0000-000000000000"

@pytest.mark.asyncio
async def test_process_existing_chat(mock_model_service, mock_storage_service):
    # Setup mocks
    test_chat_id = UUID(int=1)
    mock_model_service.get_model_config = AsyncMock(return_value={
        "provider": "openai", 
        "model": "gpt-4"
    })
    mock_storage_service.get_chat_history = AsyncMock(return_value=[
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hi there")
    ])
    
    # Test existing chat
    service = ChatService(
        config=AsyncMock(),
        model_service=mock_model_service,
        storage_service=mock_storage_service
    )
    
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="New message")],
        custom_config=None,
        stream=False
    )
    
    response = await service.process_chat_request(request, chat_id=test_chat_id)
    
    # Verify
    mock_storage_service.get_chat_history.assert_called_once_with(test_chat_id)
    assert response.chat_id == str(test_chat_id)

@pytest.fixture
def mock_model_service():
    return AsyncMock()

@pytest.fixture
def mock_storage_service():
    return AsyncMock(spec=ChatStorageService)