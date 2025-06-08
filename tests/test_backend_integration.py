import pytest
import httpx
import time
from uuid import uuid4
from fastapi.testclient import TestClient
from src.backend.main import app
from services.core.config import CoreConfig
from services.core.init_service import InitService

@pytest.fixture(scope="module")
def test_client():
    """Fixture providing test client with Docker backend"""
    client = TestClient(app)
    yield client

@pytest.fixture(scope="module")
async def redis_pool():
    """Fixture providing Redis connection pool"""
    config = CoreConfig()
    init_service = InitService(config)
    await init_service.initialize()
    yield init_service.redis_pool
    await init_service.cleanup()

@pytest.mark.integration
class TestBackendIntegration:
    def test_health_check(self, test_client):
        """Test health endpoint reports Redis and DB status"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "connected"
        assert data["redis"] == "connected"

    async def test_redis_caching(self, test_client, redis_pool):
        """Test Redis caching through API endpoints"""
        # Create test chat
        chat_name = f"test_chat_{uuid4()}"
        create_res = test_client.post(f"/chat/{chat_name}", json={
            "messages": [{"role": "user", "content": "test"}],
            "chat_name": chat_name
        })
        assert create_res.status_code == 200
        chat_id = create_res.json()["chat_id"]

        # Verify cache is populated
        cache_key = f"chat:{chat_id}:history"
        cached = await redis_pool.get(cache_key)
        assert cached is not None

    def test_database_persistence(self, test_client):
        """Test data persists across requests"""
        # Create model
        model_name = f"test_model_{uuid4()}"
        create_res = test_client.post("/model/create", json={
            "model_name": model_name,
            "model": "test",
            "system_prompt": "test"
        })
        assert create_res.status_code == 200
        model_id = create_res.json()["model_id"]

        # Verify model exists in subsequent request
        get_res = test_client.get(f"/model/{model_id}")
        assert get_res.status_code == 200
        assert get_res.json()["model_name"] == model_name

    def test_rate_limiting(self, test_client):
        """Test API rate limiting"""
        # First requests should succeed
        for _ in range(5):
            res = test_client.get("/health")
            assert res.status_code == 200

        # Subsequent requests should be rate limited
        res = test_client.get("/health")
        assert res.status_code == 429

@pytest.mark.e2e
class TestEndToEnd:
    def test_chat_workflow(self, test_client):
        """Test complete chat workflow"""
        # Create model
        model_res = test_client.post("/model/create", json={
            "model_name": "e2e_test_model",
            "model": "test",
            "system_prompt": "test"
        })
        assert model_res.status_code == 200

        # Create chat
        chat_res = test_client.post("/chat/e2e_test_chat", json={
            "messages": [{"role": "user", "content": "hello"}],
            "chat_name": "e2e_test_chat"
        })
        assert chat_res.status_code == 200
        chat_id = chat_res.json()["chat_id"]

        # Continue chat
        continue_res = test_client.post(f"/chat/{chat_id}", json={
            "messages": [{"role": "user", "content": "hello again"}],
            "chat_name": "e2e_test_chat"
        })
        assert continue_res.status_code == 200

        # Verify chat history
        history_res = test_client.get(f"/chats/{chat_id}/messages")
        assert history_res.status_code == 200
        assert len(history_res.json()) == 2