# Model service components
from .config import ModelConfig
from .service import ModelService
from ..core.migration_manager import MigrationManager

class ModelServiceManager:
    def __init__(self, database, config: ModelConfig):
        self.service = ModelService(config, database)
        self.migration_manager = MigrationManager(database, "model")
         
    async def initialize(self):
        """Initialize model service and run migrations"""
        try:
            await self.migration_manager.run_migrations()
            return self.service
        except Exception as e:
            # Log the error and re-raise with context
            import logging
            logging.error(f"Failed to initialize ModelService: {e}")
            raise RuntimeError(f"ModelService initialization failed: {e}") from e

    async def list_models(self):
        return await self.service.list_models()

    async def get_model(self, model_id: str):
        return await self.service.get_model(model_id)

    async def update_model(self, model_id: str, update_data: dict):
        return await self.service.update_model(model_id, update_data)

    async def delete_model(self, model_id: str):
        return await self.service.delete_model(model_id)

    async def create_model(self, request):
        return await self.service.create_model(request)

__all__ = ['ModelConfig', 'ModelService', 'ModelServiceManager']