import pytest
from services.core.init_service import InitService
from services.core.config import CoreConfig

@pytest.mark.asyncio
async def test_redis_connection():
    """Basic test verifying Redis connection works"""
    config = CoreConfig()
    init_service = InitService(config)
    await init_service.initialize()
    
    try:
        # Test basic Redis operations
        await init_service.redis_pool.set("test_key", "test_value")
        value = await init_service.redis_pool.get("test_key")
        assert value.decode() == "test_value"
    finally:
        await init_service.cleanup()

# For comprehensive Redis integration tests, see test_redis_integration.py