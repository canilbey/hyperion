# Chat service components
from typing import Optional
# from backend.config import Settings
from backend.services.model.service import ModelService
from .config import ChatConfig
from .service import ChatService
from .storage import ChatStorageService
from .context_storage import ContextStorageService
from backend.services.core.migration_manager import MigrationManager

import logging


class ChatServiceManager:
    def __init__(
        self,
        model_service: ModelService,
        database=None,
        redis=None
    ):
        self.model_service = model_service
        self.database = database
        self.redis = redis
        self.logger = logging.getLogger(__name__)
        self.config = ChatConfig()
        self.storage_service = ChatStorageService(database, redis)
        self.context_storage_service = ContextStorageService(database, redis)
        self.service = ChatService(
            config=self.config,
            model_service=model_service,
            storage_service=self.storage_service,
            context_storage_service=self.context_storage_service,
            redis_pool=redis
        )
        self.migration_manager = MigrationManager(database, "chat")  # <-- Doğru girintide ve __init__ içinde

    async def initialize(self):
        """Servisi başlat ve migration'ları çalıştır"""
        if not self.database:
            raise ValueError("Database connection required for initialization")
            
        # Migration'ları çalıştır
        await self.migration_manager.run_migrations()
        
        # Redis cache'i temizle
        if self.redis:
            # Use SCAN and DELETE for pattern-based clearing
            async for key in self.redis.scan_iter(match="chat:*"):
                await self.redis.delete(key)
            async for key in self.redis.scan_iter(match="model:*"):
                await self.redis.delete(key)
            
        self.logger.info("Chat service initialized successfully")

__all__ = ['ChatConfig', 'ChatService', 'ChatStorageService', 'ChatServiceManager']