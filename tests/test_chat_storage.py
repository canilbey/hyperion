import pytest
from uuid import UUID
from datetime import datetime
from src.backend.services.chat.storage import ChatStorageService
from src.backend.models import ChatMessage

@pytest.mark.asyncio
async def test_create_chat(db_pool):
    storage = ChatStorageService(db_pool)
    chat_id = await storage.create_chat(label="Test Chat")
    assert isinstance(chat_id, UUID)

@pytest.mark.asyncio 
async def test_add_message(db_pool):
    storage = ChatStorageService(db_pool)
    chat_id = await storage.create_chat()
    
    message_id = await storage.add_message(
        chat_id=chat_id,
        role="user",
        content="Hello",
        usage={"tokens": 10}
    )
    assert message_id > 0

@pytest.mark.asyncio
async def test_get_history(db_pool):
    storage = ChatStorageService(db_pool)
    chat_id = await storage.create_chat()
    
    # Add test messages
    await storage.add_message(chat_id, "user", "Hello")
    await storage.add_message(chat_id, "assistant", "Hi there")
    
    history = await storage.get_chat_history(chat_id)
    assert len(history) == 2
    assert isinstance(history[0], ChatMessage)
    assert history[0].role == "user"
    assert history[0].content == "Hello"

@pytest.mark.asyncio
async def test_update_chat_label(db_pool):
    storage = ChatStorageService(db_pool)
    chat_id = await storage.create_chat(label="Old Label")
    await storage.update_chat_label(chat_id, "New Label")
    
    # Fetch from DB to verify
    query = "SELECT label FROM chats WHERE chat_id = :chat_id"
    row = await db_pool.fetch_one(query, {"chat_id": str(chat_id)})
    assert row["label"] == "New Label"