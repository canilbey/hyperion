import logging
import asyncio
from databases import Database
import redis.asyncio as redis
from .config import CoreConfig
from .model import OpenRouterModel
from .migration_manager import ServiceMigrationManager

# Singleton database instance
_db = None

def get_db() -> Database:
    """Get or create database connection"""
    global _db
    if _db is None:
        config = CoreConfig()
        _db = Database(config.database_url)
        # Connect to database
        asyncio.create_task(_db.connect())
    return _db

class InitService:
    def __init__(self, config: CoreConfig):
        self.config = config
        self.database = get_db()
        self.redis_pool = redis.from_url(config.redis_url)
        self.logger = logging.getLogger(__name__)
        self.model = OpenRouterModel(config.openrouter_api_key, config.openrouter_model)
        self.migration_manager = ServiceMigrationManager(self.database)

    async def initialize(self):
        """Initialize all core services with retry logic"""
        max_retries = 5
        retry_delay = 2
        
        # Database connection with retry
        for attempt in range(max_retries):
            try:
                await self.database.connect()
                await self.redis_pool.ping()
                
                # Run migrations for all services
                await self.migration_manager.run_all_migrations()
                
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
            await self.redis_pool.aclose()
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
            
    async def run_service_migrations(self, service_name: str) -> None:
        """Run migrations for a specific service"""
        await self.migration_manager.run_service_migrations(service_name)