import pytest
from uuid import uuid4
from src.backend.services.core.init_service import InitService
from backend.services.core.config import CoreConfig
from backend.services.chat.service import ChatService
from backend.services.chat.storage import ChatStorageService
from backend.services.model.service import ModelService
from models import ChatRequest, ChatMessage

@pytest.mark.asyncio
class TestRedisIntegration:
    @pytest.fixture
    async def services(self):
        config = CoreConfig()
        init_service = InitService(config)
        await init_service.initialize()
        
        model_service = ModelService(config, init_service.database)
        chat_storage = ChatStorageService(init_service.database)
        chat_service = ChatService(
            config, 
            model_service, 
            chat_storage,
            init_service.redis_pool
        )
        
        yield {
            'init': init_service,
            'chat': chat_service,
            'storage': chat_storage
        }
        
        await init_service.cleanup()

    async def test_chat_history_caching(self, services):
        """Test chat history is properly cached in Redis"""
        chat_id = uuid4()
        
        # Add test messages
        await services['storage'].add_message(
            chat_id=chat_id,
            role="user",
            content="Test message 1",
            chat_name="test"
        )
        
        # First call should cache
        messages1 = await services['chat']._get_cached_chat_history(chat_id)
        
        # Add another message to invalidate cache
        await services['storage'].add_message(
            chat_id=chat_id,
            role="assistant",
            content="Test response 1",
            chat_name="test"
        )
        
        # Second call should get fresh data
        messages2 = await services['chat']._get_cached_chat_history(chat_id)
        
        assert len(messages2) == len(messages1) + 1

    async def test_model_config_caching(self, services):
        """Test model config is properly cached in Redis"""
        # Create test model
        model_id = "test_model"
        test_config = {"model": "test", "provider": "test"}
        
        # Mock model service
        services['chat'].model_service.get_model_config = lambda *_: test_config
        
        # First call should cache
        config1 = await services['chat']._get_cached_model_config(model_id=model_id)
        
        # Second call should hit cache
        config2 = await services['chat']._get_cached_model_config(model_id=model_id)
        
        assert config1 == config2 == test_config

    async def test_rate_limiting(self, services):
        """Test API rate limiting works"""
        test_key = "test_api_key"
        
        # Should allow first 5 calls (for OpenAI/Anthropic)
        for i in range(5):
            try:
                await services['chat']._call_openai_api([], "test", test_key)
            except Exception as e:
                if "Too many requests" in str(e):
                    pytest.fail(f"Rate limited too early on call {i+1}")
        
        # 6th call should be rate limited
        with pytest.raises(Exception) as exc:
            await services['chat']._call_openai_api([], "test", test_key)
        assert "Too many requests" in str(exc.value)

    async def test_redis_unavailable(self, services):
        """Test graceful fallback when Redis is unavailable"""
        # Simulate Redis being down
        original_redis = services['chat'].redis_pool
        services['chat'].redis_pool = None
        
        try:
            # Should still work without Redis
            chat_id = uuid4()
            messages = await services['chat']._get_cached_chat_history(chat_id)
            assert isinstance(messages, list)
        finally:
            # Restore Redis
            services['chat'].redis_pool = original_redis