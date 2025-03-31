import logging
import asyncio
from databases import Database
import redis.asyncio as redis
from .config import CoreConfig

class InitService:
    def __init__(self, config: CoreConfig):
        self.config = config
        self.database = Database(config.database_url)
        self.redis_pool = redis.from_url(config.redis_url)
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Initialize all core services with retry logic"""
        max_retries = 5
        retry_delay = 2
        
        # Database connection with retry
        for attempt in range(max_retries):
            try:
                await self.database.connect()
                await self.redis_pool.ping()
                self.logger.info("Core services initialized")
                return
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    raise

    async def cleanup(self):
        """Clean up all core services"""
        try:
            await self.database.disconnect()
            await self.redis_pool.close()
            self.logger.info("Core services cleaned up")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
            raise

    async def health_check(self):
        """Check health of core services"""
        try:
            db_status = "connected" if self.database.is_connected else "disconnected"
            redis_status = "connected" if await self.redis_pool.ping() else "disconnected"
            return {
                "database": db_status,
                "redis": redis_status
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "database": "error",
                "redis": "error"
            }